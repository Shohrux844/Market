from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Jins uchun keyboard
gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨‍💼 Erkak"), KeyboardButton(text="👩‍🦰 Ayol")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Telefon raqam uchun keyboard
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

debt = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💰 Mening Qarzlarim"),
            KeyboardButton(text="👤 Mening Malumotlarim")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)



