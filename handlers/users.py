from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
     Message, 
     CallbackQuery, 
     InlineQuery,
     InlineQueryResultArticle,
     InputTextMessageContent,
     ChosenInlineResult,
     ContentType,
     ReplyKeyboardRemove
     
)
from aiogram.fsm.context import FSMContext
from geopy.geocoders import Nominatim

from database.db import Base
from handlers.states import *
from keyboards import reply
from tmp.gamesdict import gamesdict

import random

router = Router()
geolocator = Nominatim(user_agent="GeoCode")

menu_main_text = '1. Смотреть анкеты\n2. Моя анкета\n3. Отключить анкету'
my_anketa_text = '1. Заполнить анкету заново\n2. Изменить текст анкеты\n3. Изменить фото\n4. Вернутся назад'

def games_text(me):
     return (f"Выберите интересующие вас 1-3 игры. Введите @{me} "
               f"игры [название] (повторный выбор удаляет из списка).\n\n"
               f"Пример: <code>@{me} игры Valorant</code>")


def show_anketa(name, age, city, text):
     return f'{name}\n{age}\n{city}\n{text}'

def get_random_anketa(list_of_anketi):
     anketa = list_of_anketi[random.randint(0, len(list_of_anketi) - 1)]
     a = anketa
     return [show_anketa(a[2], a[3], a[4], a[5]), Base.get_photo_id(a[1])]

def get_city(latitude: str, longitude: str):
     location = geolocator.reverse(latitude+","+longitude, language='ru')
     address = location.raw['address']
     return address.get('city', '') if address.get('city', '') else address.get('town')



@router.message(Command("start"), StateFilter(None))
async def start(message: Message, state: FSMContext):

     """ if(Base.user_exists(message.from_user.id)):

          anketa = Base.get_anketa(message.from_user.id)
          a = anketa[0]
          caption = show_anketa(a[2], a[3], a[4], a[5])

          await message.answer(photo = open(f"photos/{message.from_user.id}.jpg", "rb"), chat_id = message.from_user.id, caption = caption)
          await message.answer(menu_main_text, reply_markup = reply.main)

          await Wait.menu_answer.set()

     else: """

     await message.answer("Давайте заполним анкету! Для начала выберите свой пол",
                              reply_markup=reply.gender)
     await state.set_state(Wait.choosing_gender)



@router.message(StateFilter(Wait.choosing_gender))
async def choose_gender(message: Message, state: FSMContext):
     if message.text not in ["Я парень", "Я девушка"]:
          await message.answer("Выберите вариант из кнопок ниже")
          return
     
     gender = 1 if message.text == "Я парень" else 0
     await state.update_data(gender = gender)
     await message.answer("Кто тебя интересует?", reply_markup = reply.interest_gender)
     await state.set_state(Wait.choosing_interest)



@router.message(StateFilter(Wait.choosing_interest))
async def choose_interest(message: Message, state: FSMContext, bot: Bot):
     if message.text == "Парни" or message.text == "Девушки" or message.text == "Все равно":
          interest = 1 if message.text == "Парни" else 0 if message.text == "Девушки" else 2
          await state.update_data(interest = interest)
          me = await bot.get_me()
          await message.answer(games_text(me.username), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
          
          await state.set_state(Wait.choosing_games)

     else:
          await message.answer("Выберите вариант из кнопок ниже")
          return

     

@router.inline_query(StateFilter(Wait.choosing_games), F.query.startswith("игры"))
async def choose_games(iquery: InlineQuery, state: FSMContext):
     query = iquery.query.strip().lower() 
     results = []

     search_query = query[5:].strip()
     for title, logo in gamesdict.items():
          if search_query in title.lower():  
               results.append(InlineQueryResultArticle(
               id=title,
               title=title,
               thumb_url=logo,
               input_message_content=InputTextMessageContent(
                    message_text=f"— {title}",
                    parse_mode="HTML"
                    )
               ))

     await iquery.answer(results, is_personal=True)


@router.chosen_inline_result(StateFilter(Wait.choosing_games))
async def chosed_games(iquery: ChosenInlineResult, state: FSMContext, bot: Bot):
     try:
          data = await state.get_data()
          games = data['games']
          tech1 = data['tech1']
          if iquery.result_id not in games:
               games.append(iquery.result_id)
          else:
               games.remove(iquery.result_id)
          await bot.delete_message(iquery.from_user.id, tech1)

     except:
          games = [iquery.result_id]

     me = await bot.get_me()
     text = f"Вы выбрали {len(games)}/3. \n\n— {", ".join(games)}" if games else (games_text(me.username))
     text = f"Вы выбрали 'любые игры'" if "Любые игры" in games else text
     tech1 = await bot.send_message(iquery.from_user.id, text, reply_markup=reply.confirm, parse_mode="HTML")
     await state.update_data(tech1=tech1.message_id)
     await state.update_data(games = games)

     if len(games) == 3 or "Любые игры" in games:
          await bot.send_message(iquery.from_user.id, f"Введите свое имя")
          await state.set_state(Wait.name)

@router.message(StateFilter(Wait.choosing_games))
async def chosed_games(message: Message, state: FSMContext, bot: Bot):
     if message.text == "Продолжить":
          await bot.send_message(message.from_user.id, f"Введите свое имя", reply_markup=ReplyKeyboardRemove())
          await state.set_state(Wait.name)
     
     else:
          await bot.send_message(message.from_user.id, f"Выберите игры")



@router.message(StateFilter(Wait.name))
async def chosed_games(message: Message, state: FSMContext):
     if len(message.text) > 15:
          await message.answer("Слишком длинное имя")
          return
          
     await state.update_data(name = message.text)                    
     await message.answer("Сколько вам лет?")
     await state.set_state(Wait.age)



@router.message(StateFilter(Wait.age))
async def age(message: Message, state: FSMContext):
     try:
          if 10 > int(message.text) or int(message.text) > 100:
               await message.answer("Какой-то странный возраст")
               return
     except(TypeError, ValueError):
          await message.answer("Какой-то странный возраст")
          return
     await state.update_data(age = message.text)
     await message.answer("Из какого ты города?", reply_markup=reply.geoloc())
     await state.set_state(Wait.city)



@router.message(StateFilter(Wait.city))
async def city(message: Message, state: FSMContext):
     if message.text and len(message.text) > 20:
          await message.answer("Слишком длинное название города")
          return
     if message.content_type == ContentType.LOCATION:
          city = get_city(str(message.location.latitude), str(message.location.longitude))
     else:
          city = message.text

     await state.update_data(city = city)
     await message.answer("Расскажи о себе и кого хочешь найти, чем предлагаешь заняться.", reply_markup = reply.skip)
     await state.set_state(Wait.text)



@router.message(StateFilter(Wait.text))
async def test(message: Message, state: FSMContext):
     pass