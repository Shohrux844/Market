from aiogram import Router, Bot, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from datetime import datetime, timedelta
import asyncio


from db.model import session, User

debt_router = Router()


def format_time_remaining(end_date: datetime) -> str:
    """Qolgan vaqtni formatlash"""
    now = datetime.now()
    if end_date <= now:
        return "⏰ Muddati tugagan!"

    time_left = end_date - now
    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60

    if days > 0:
        return f"⏳ {days} kun {hours} soat qoldi"
    else:
        return f"⏳ {hours} soat {minutes} daqiqa qoldi"


@debt_router.message(F.text == "💰 Mening Qarzlarim")
async def debt_info_handler(message: Message):
    """Foydalanuvchi qarz ma'lumotlarini ko'rsatish"""
    query = select(User).where(User.id == message.from_user.id)
    user = session.execute(query).scalar_one_or_none()

    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz. /start buyrug'ini bosing.")
        return

    if user.debt == 0 or not user.end_debt:
        await message.answer("💰 Sizda hozirda qarz mavjud emas.")
        return

    time_remaining = format_time_remaining(user.end_debt)

    debt_info = (
        "🏪 **Ortiqboyev Market Qarz Ma'lumotlari**\n\n"
        f"💳 **Joriy qarz:** {user.debt:,.0f} so'm\n"
        f"📅 **Qarz olingan sana:** {user.start_debt.strftime('%d.%m.%Y %H:%M')}\n"
        f"⏰ **Qarz tugash sanasi:** {user.end_debt.strftime('%d.%m.%Y %H:%M')}\n"
        f"🕐 **Qolgan muddat:** {time_remaining}\n\n"
    )

    # Qarz foizini hisoblash
    total_days = (user.end_debt - user.start_debt).days
    days_passed = (datetime.now() - user.start_debt).days
    if total_days > 0:
        progress_percent = min(100, (days_passed / total_days) * 100)
        debt_info += f"📊 **Muddat bajarilishi:** {progress_percent:.1f}%"

    await message.answer(debt_info)


@debt_router.message(F.text == "👤 Mening Malumotlarim")
async def my_info_handler(message: Message):
    """Foydalanuvchi shaxsiy ma'lumotlari"""
    query = select(User).where(User.id == message.from_user.id)
    user = session.execute(query).scalar_one_or_none()

    if not user:
        await message.answer("❌ Siz ro'yxatdan o'tmagansiz. /start buyrug'ini bosing.")
        return

    user_info = (
        "👤 **Shaxsiy ma'lumotlar**\n\n"
        f"🆔 **ID:** {user.id}\n"
        f"👤 **Ism:** {user.first_name or 'Noma\'lum'}\n"
        f"👤 **Familiya:** {user.last_name or 'Noma\'lum'}\n"
        f"📱 **Telefon:** {user.phone_number or 'Noma\'lum'}\n"
        f"🔢 **Passport:** {user.seria_number or 'Noma\'lum'}\n"
        f"💰 **Qarz:** {user.debt:,.0f} so'm\n"
        f"📅 **Ro'yxatdan o'tgan:** {user.created_at.strftime('%d.%m.%Y')}\n"
        f"🔰 **Holat:** {'🟢 Faol' if user.is_active else '🔴 Nofaol'}"
    )

    await message.answer(user_info)


async def check_deadlines(bot: Bot):
    """Muddati tugayotgan qarzlarni tekshirish"""
    while True:
        try:
            now = datetime.now()

            # 1 kun qolgan qarzlarni topish
            one_day_left = now + timedelta(days=1)
            query = select(User).where(
                User.end_debt <= one_day_left,
                User.end_debt > now,
                User.debt > 0,
                User.is_active == True
            )
            users = session.execute(query).scalars().all()

            for user in users:
                time_left = user.end_debt - now
                hours_left = time_left.total_seconds() // 3600

                if hours_left <= 24:
                    warning_msg = (
                        "⚠️ **Qarz muddati ogohlantirishi**\n\n"
                        f"Qarzingizning muddati {hours_left:.0f} soatdan keyin tugaydi!\n"
                        f"💳 Qarz miqdori: {user.debt:,.0f} so'm\n"
                        f"⏰ Tugash sanasi: {user.end_debt.strftime('%d.%m.%Y %H:%M')}\n\n"
                        f"Iltimos, qarzni o'z vaqtida to'lang!"
                    )
                    await bot.send_message(user.id, warning_msg)

            # Muddati tugagan qarzlarni topish
            expired_query = select(User).where(
                User.end_debt <= now,
                User.debt > 0,
                User.is_active == True
            )
            expired_users = session.execute(expired_query).scalars().all()

            for user in expired_users:
                expired_msg = (
                    "❌ **Qarz muddati tugadi!**\n\n"
                    f"Qarzingizning muddati tugadi!\n"
                    f"💳 Qarz miqdori: {user.debt:,.0f} so'm\n"
                    f"⏰ Tugash sanasi: {user.end_debt.strftime('%d.%m.%Y %H:%M')}\n\n"
                    f"Iltimos, darhol qarzni to'lang yoki admin bilan bog'laning!"
                )
                await bot.send_message(user.id, expired_msg)
                # Foydalanuvchini nofaol qilish
                user.is_active = False
                session.commit()

            # Har 1 soatda tekshiramiz
            await asyncio.sleep(3600)

        except Exception as e:
            print(f"Error in check_deadlines: {e}")
            await asyncio.sleep(300)  # 5 minut kutib qayta urinamiz
