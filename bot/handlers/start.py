from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import bold

from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import re

from bot.buttons.reply import gender_keyboard, phone_keyboard, debt
from bot.state.register import UserRegistration
from db.model import session, User

start_router = Router()


@start_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    query = select(User).where(User.id == message.from_user.id)
    user = session.execute(query).scalar_one_or_none()

    if user:
        await message.answer(f"👋 Assalomu alaykum {bold(user.first_name)}! Siz allaqachon ro'yxatdan o'tgansiz.",
                             reply_markup=debt)
        return

    await message.answer("👋 Assalomu alaykum! Ro'yxatdan o'tish jarayonini boshlaymiz.")
    await message.answer("👤 Passport bo'yicha ismingizni kiriting\n(Misol uchun: Baxodir)")
    await state.set_state(UserRegistration.first_name)


@start_router.message(UserRegistration.first_name)
async def process_first_name(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("❌ Iltimos, to'g'ri ism kiriting (kamida 2 ta harf)")
        return

    await state.update_data(first_name=message.text)
    await message.answer("👤 Passportingiz bo'yicha familiyangizni kiriting\n(Misol uchun: Baxodirov)")
    await state.set_state(UserRegistration.last_name)


@start_router.message(UserRegistration.last_name)
async def process_last_name(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("❌ Iltimos, to'g'ri familiya kiriting (kamida 2 ta harf)")
        return

    await state.update_data(last_name=message.text)
    await message.answer("👤 Passportingizdagi otangiz ismini kiriting\n(Misol: Abdurashidovich)")
    await state.set_state(UserRegistration.middle_name)


@start_router.message(UserRegistration.middle_name)
async def process_middle_name(message: Message, state: FSMContext):
    await state.update_data(middle_name=message.text)
    await message.answer("👨‍💼/👩‍🦰 Jinsingizni tanlang", reply_markup=gender_keyboard)
    await state.set_state(UserRegistration.gender)


@start_router.message(UserRegistration.gender, F.text.in_(["👨‍💼 Erkak", "👩‍🦰 Ayol"]))
async def process_gender(message: Message, state: FSMContext):
    gender = "Erkak" if message.text == "👨‍💼 Erkak" else "Ayol"
    await state.update_data(gender=gender)
    await message.answer("📅 Tug'ilgan kuningizni kiriting (masalan, dd.mm.yyyy):",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserRegistration.birth_date)


@start_router.message(UserRegistration.gender)
async def wrong_gender(message: Message):
    await message.answer("❌ Iltimos, jinsingizni tugmalardan tanlang")


@start_router.message(UserRegistration.birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    # Sana formatini tekshirish
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(date_pattern, message.text):
        await message.answer("❌ Iltimos, to'g'ri formatda kiriting (dd.mm.yyyy)")
        return

    await state.update_data(birth_date=message.text)
    await message.answer("🏠 Yashash manzilingizni kiriting (shahar, tuman, ko'cha/blok):")
    await state.set_state(UserRegistration.address)


@start_router.message(UserRegistration.address)
async def process_address(message: Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer("❌ Iltimos, to'liq manzil kiriting")
        return

    await state.update_data(address=message.text)
    await message.answer("📱 Iltimos, quyidagi tugmani bosib, telefon raqamingizni yuboring:",
                         reply_markup=phone_keyboard)
    await state.set_state(UserRegistration.phone_number)


@start_router.message(UserRegistration.phone_number, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    await message.answer("✏️ Telegramda username kiriting (@username):",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserRegistration.username)


@start_router.message(UserRegistration.phone_number)
async def wrong_phone_input(message: Message):
    await message.answer("❌ Iltimos, telefon raqamingizni tugma orqali yuboring")


@start_router.message(UserRegistration.username)
async def process_username(message: Message, state: FSMContext):
    username = message.text
    if username.startswith('@'):
        username = username[1:]

    await state.update_data(username=username)
    await message.answer("🔢 Passport seria raqamingizni kiriting:\n(Misol: AA1234567 yoki AB1234567)")
    await state.set_state(UserRegistration.seria_number)


@start_router.message(UserRegistration.seria_number)
async def process_seria_number(message: Message, state: FSMContext):
    seria_text = message.text.upper().strip()

    # Passport seria formatini tekshirish (2 ta harf + 7 ta raqam)
    seria_pattern = r'^[A-Z]{2}\d{7}$'

    if not re.match(seria_pattern, seria_text):
        await message.answer("❌ Iltimos, to'g'ri formatda kiriting:\n• 2 ta katta harf\n• 7 ta raqam\nMisol: AA1234567")
        return

    await state.update_data(seria_number=seria_text)
    await message.answer("🤵 Suratingizni yuboring (telefoningizdan selfi olishingiz mumkin):")
    await state.set_state(UserRegistration.photo)


@start_router.message(UserRegistration.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    # Rasmni saqlash (file_id ni saqlaymiz)
    photo_id = message.photo[-1].file_id

    user_data = await state.get_data()

    # User yaratish
    user = User(
        id=message.from_user.id,
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        middle_name=user_data.get('middle_name'),
        gender=user_data.get('gender'),
        birth_date=user_data.get('birth_date'),
        address=user_data.get('address'),
        phone_number=user_data.get('phone_number'),
        username=user_data.get('username'),
        seria_number=user_data.get('seria_number'),  # Passport seria
        photo=photo_id
    )

    session.add(user)
    session.commit()

    # Foydalanuvchi ma'lumotlarini ko'rsatish
    user_info = (
        "✅ Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
        f"📋 Ma'lumotlaringiz:\n"
        f"👤 Ism: {user_data.get('first_name')}\n"
        f"👤 Familiya: {user_data.get('last_name')}\n"
        f"👤 Otangiz ismi: {user_data.get('middle_name')}\n"
        f"👨‍💼/👩‍🦰 Jins: {user_data.get('gender')}\n"
        f"📅 Tug'ilgan sana: {user_data.get('birth_date')}\n"
        f"🏠 Manzil: {user_data.get('address')}\n"
        f"📱 Telefon: {user_data.get('phone_number')}\n"
        f"✏️ Username: @{user_data.get('username')}\n"
        f"🔢 Passport seria: {user_data.get('seria_number')}\n"
    )

    await message.answer(user_info, reply_markup=debt)
    await state.clear()


@start_router.message(UserRegistration.photo)
async def wrong_photo_input(message: Message):
    await message.answer("❌ Iltimos, rasm yuboring")
