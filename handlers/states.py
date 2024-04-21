from aiogram.fsm.state import State, StatesGroup

class Wait(StatesGroup):
    choosing_gender = State()
    choosing_interest = State()
    choosing_games = State()
    name = State()
    age = State()
    city = State()
    text = State()
    photo = State()
    menu_answer = State()
    my_anketa_answer = State()
    change_text = State()
    change_photo = State()
    delete_confirm = State()
    anketa_reaction = State()