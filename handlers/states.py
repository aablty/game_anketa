from aiogram.fsm.state import State, StatesGroup

class Wait(StatesGroup):
    gender = State()
    interest = State()
    games = State()
    name = State()
    age = State()
    city = State()
    text = State()
    photo = State()
    menu = State()


class Edit(StatesGroup):
    menu = State()
    text = State()
    photo = State()
    name = State()
    age = State()
    gender = State()
    interest = State()
    games = State()
    city = State()
    insta = State()
    steam = State()


class React(StatesGroup):
    pass