from aiogram.fsm.state import State, StatesGroup


class UserRegistration(StatesGroup):
    first_name = State()
    last_name = State()
    middle_name = State()
    gender = State()
    birth_date = State()
    address = State()
    phone_number = State()
    username = State()
    seria_number = State()  # Yangi state: passport seria
    photo = State()
