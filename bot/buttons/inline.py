from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def kino_genre_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # [
            #     InlineKeyboardButton(text='🎭 Drama', callback_data='drama'),
            #     InlineKeyboardButton(text='😂 Komediya', callback_data='komediya')
            # ],
            # [
            #     InlineKeyboardButton(text='😱 Triller', callback_data='triller'),
            #     InlineKeyboardButton(text='🕵️‍♂️ Detektiv', callback_data='detektiv')
            # ],
            # [
            #     InlineKeyboardButton(text='🥋 Jangari', callback_data='jangari'),
            #     InlineKeyboardButton(text='🗺️ Sarguzasht', callback_data='sarguzasht')
            # ],
            # [
            #     InlineKeyboardButton(text='🏰 Tarixiy', callback_data='tarixiy'),
            #     InlineKeyboardButton(text='🚀 Fantastika', callback_data='fantastika')
            # ],
            [
                InlineKeyboardButton(text="Qidiruv Tugmasi 🔎", switch_inline_query_current_chat=" ")
            ]
        ]
    )
