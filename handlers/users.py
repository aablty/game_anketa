from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
     Message, 
     CallbackQuery, 
     InlineQuery,
     InlineQueryResultArticle,
     InputTextMessageContent,
     ChosenInlineResult,
     InputMediaPhoto,
     ReplyKeyboardRemove
     
)
from aiogram.fsm.context import FSMContext

from database.db import Base 
from handlers.states import *
from keyboards import reply, inline
from utils.utils import *
from utils.text_patterns import *


router=Router()
db = Base()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
     user_id = message.from_user.id
     if db.user_exists(user_id):
          photo = db.get_photo(user_id)
          await message.answer(f"Так выглядит твоя анкета:")
          anketa = await message.answer_photo(photo=photo, caption=caption_anket(user_id), reply_markup=inline.menu(), parse_mode="HTML")
          await state.set_state(Wait.menu)
          await state.update_data(anketa = anketa.message_id)

     else:

          await message.answer("Давай заполним анкету! Для начала выбери свой пол",
                                   reply_markup=inline.gender())
          await state.set_state(Wait.gender)



@router.callback_query(StateFilter(Wait.gender))
async def choose_gender(callback: CallbackQuery, state: FSMContext, bot: Bot):
     gender=1 if callback.data == "gboy" else 0
     await state.update_data(gender=gender)
     await bot.send_message(callback.from_user.id, "Кто тебя интересует?", reply_markup=inline.interest())
     await state.set_state(Wait.interest)



@router.callback_query(StateFilter(Wait.interest))
async def choose_interest(callback: CallbackQuery, state: FSMContext, bot: Bot):
     interest=1 if callback.data == "iboy" else 0 if callback.data == "igirl" else 2
     await state.update_data(interest=interest)
     me=await bot.get_me()
     tech1 = await bot.send_message(callback.from_user.id, games_text(me.username), parse_mode="HTML")
     
     await state.update_data(tech1 = tech1.message_id)
     await state.set_state(Wait.games)


     

@router.inline_query(StateFilter(Wait.games))
async def choose_games(iquery: InlineQuery):
     query=iquery.query.strip().lower() 
     results=[]

     for title, logo in gamesdict.items():
          if query.strip() in title.lower():  
               results.append(InlineQueryResultArticle(
               id=title,
               title=title,
               description=games_description(title),
               thumb_url=logo,
               input_message_content=InputTextMessageContent(
                    message_text=f"— {title}",  
                    parse_mode="HTML"
                    )
               ))

     await iquery.answer(results, is_personal=True)


@router.chosen_inline_result(StateFilter(Wait.games))
async def chosed_games1(iquery: ChosenInlineResult, state: FSMContext, bot: Bot):
     user_id = iquery.from_user.id
     game = iquery.result_id
     d = await state.get_data()
     tech1 = d['tech1']
     me=await bot.get_me()

     try:
          games = d['games']
     except:
          games = []

     if game == "Любые игры" and "Любые игры" not in games: 
          games.remove.all, games.append(game)  

     games.append(game) if game not in games else games.remove(game)

     if games != []:
          await state.update_data(games=games)
          if len(games) < 3:
               await bot.delete_message(user_id, tech1)
               tech1 = await bot.send_message(user_id, f"Вы выбрали {", ".join(games)} ({len(games)}/3).\n{games_text(me.username)}", 
                                              reply_markup=reply.confirm,  parse_mode="HTML")
               await state.update_data(tech1 = tech1.message_id)

          else:
               await bot.delete_message(user_id, tech1)
               await bot.send_message(user_id, f"Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
               await state.set_state(Wait.name)

     else:
          await bot.delete_message(user_id, tech1)
          tech1 = await bot.send_message(user_id, f"Игры не могут быть пустыми.\n{games_text(me.username)}", 
                                         reply_markup=reply.confirm,  parse_mode="HTML")
          await state.update_data(tech1 = tech1.message_id)
          return
     


@router.message(StateFilter(Wait.games))
async def chosed_games2(message: Message, state: FSMContext, bot: Bot):
     if message.text == "Продолжить":
          await message.delete()
          await bot.send_message(message.from_user.id, f"Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
          await state.set_state(Wait.name)



@router.message(StateFilter(Wait.name))
async def chosed_games3(message: Message, state: FSMContext):
     if len(message.text) > 15:
          await message.answer("Слишком длинное имя")
          return
          
     await state.update_data(name=message.text)                    
     await message.answer("Сколько вам лет?")
     await state.set_state(Wait.age)



@router.message(StateFilter(Wait.age))
async def age(message: Message, state: FSMContext, bot):
     try:
          if 10 > int(message.text) or int(message.text) > 90:
               await message.answer("Какой-то странный возраст")
               return
     except(TypeError, ValueError):
          await message.answer("Какой-то странный возраст")
          return
     await state.update_data(age=message.text)
     me=await bot.get_me()
     await message.answer(city_text(me.username), parse_mode="HTML")
     await state.set_state(Wait.city)



@router.inline_query(StateFilter(Wait.city))
async def city(iquery: InlineQuery):
     query=iquery.query.lower() 
     results=[]

     if query.strip():
          for city in get_cities(query):
               if query in city[1].lower():
                    description = ', '.join(i for i in city[2:] if i is not None)
                    results.append(InlineQueryResultArticle(
                    id=city[0],
                    title=city[1],
                    description=description + '\n',
                    input_message_content=InputTextMessageContent(
                         message_text=f"— {city[1]}",  
                         parse_mode="HTML"
                         )))

     await iquery.answer(results, is_personal=True)  




@router.chosen_inline_result(StateFilter(Wait.city))
async def chosed_city(iquery: ChosenInlineResult, state: FSMContext, bot: Bot):
     cities = get_cities(iquery.query.lower())
     for city in cities:
          if city[0] == iquery.result_id:
               city = city
               break
     
     await state.update_data(city=", ".join(i for i in city[1:] if i is not None))
     await bot.send_message(iquery.from_user.id, "Расскажи о себе и кого хочешь найти, чем предлагаешь заняться", reply_markup=reply.skip)
     await state.set_state(Wait.text)



@router.message(StateFilter(Wait.text))
async def test(message: Message, state: FSMContext):
     if message.text == "Пропустить":
          await state.update_data(text='')
     else:
          if len(message.text) > 1000:
               await message.answer("Описание должно быть длинной до 1000 символов")
               return
          await state.update_data(text = message.text)

     await message.answer("Теперь отправь свое фото", reply_markup=ReplyKeyboardRemove())
     await state.set_state(Wait.photo)

     

@router.message(StateFilter(Wait.photo), F.photo)
async def photo(message: Message, state: FSMContext, bot: Bot):
     photo = message.photo[-1].file_id

     d = await state.get_data()
     db.add_user_anketa(message.from_user.id, d['name'], d['age'], d['city'], d['text'], photo, ", ".join(d['games']), d['gender'], d['interest'])

     await message.answer(f"Так выглядит твоя анкета: ")
     await message.answer_photo(photo=photo, caption=caption_anket(message.from_user.id), reply_markup=inline.menu(), parse_mode="HTML")
     await state.set_state(Wait.menu)



@router.callback_query(StateFilter(Wait.menu))
async def menu(callback: CallbackQuery, bot: Bot, state: FSMContext):
     if callback.data == "edita":
          anketa = (await state.get_data())['anketa']
          await bot.edit_message_reply_markup(callback.from_user.id, anketa, reply_markup=inline.edit(callback.from_user.id))
          await state.set_state(Edit.menu)

     if callback.data == "start":
          pass



@router.callback_query(StateFilter(Edit.menu), F.data.startswith("edit_"))
async def edit(callback: CallbackQuery, state: FSMContext, bot: Bot):
     anketa = (await state.get_data())['anketa']
     user_id = callback.from_user.id

     if callback.data == "edit_back":
          await bot.edit_message_reply_markup(user_id, anketa, reply_markup=inline.menu())
          await state.set_state(Wait.menu)

     if callback.data == "edit_text":
          tech1 = await bot.send_message(user_id, 
                                        "Расскажи о себе и кого хочешь найти, чем предлагаешь заняться.", 
                                        reply_markup=reply.empty)
          await state.update_data(tech1 = tech1.message_id)
          await state.set_state(Edit.text)

     if callback.data == "edit_photo":
          await edit_util2(bot, user_id, state, "Отправь новое фото", Edit.photo, None)

     if callback.data == "edit_name":
          await edit_util2(bot, user_id, state, "Как тебя зовут?", Edit.name, None)

     if callback.data == "edit_age":
          await edit_util2(bot, user_id, state, "Сколько тебе лет?", Edit.age, None)

     if callback.data == "edit_gender":
          await edit_util2(bot, user_id, state, "Выбери свой пол", Edit.gender, inline.gender())

     if callback.data == "edit_interest":
          await edit_util2(bot, user_id, state, "Выбери свой пол", Edit.interest, inline.interest())

     if callback.data == "edit_games":
          me=await bot.get_me()
          tech1 = await bot.send_message(user_id, games_text(me.username), reply_markup=reply.confirm, parse_mode="HTML")
          await state.update_data(tech1 = tech1.message_id)
          await state.set_state(Edit.games)

     if callback.data == "edit_city":
          me=await bot.get_me()
          tech1 = await bot.send_message(user_id, city_text(me.username), parse_mode="HTML")
          await state.update_data(tech1 = tech1.message_id)
          await state.set_state(Edit.city)

     if callback.data.startswith("edit_+"):
          target = callback.data[6:]
          a, b, c = ("@username", "Instagram", "@therock") if target == "insta" else ("ссылку", "Steam", "https://steamcommunity.com/profiles/135737978379135")
          text = f"Отправь {a} своего профиля в {b}.\nПример: <code>{c}</code>"
          tech1 = await bot.send_message(user_id, text, parse_mode="HTML")
          await state.update_data(tech1 = tech1.message_id)
          await state.set_state(Edit.insta if target=="insta" else Edit.steam)
          
     if callback.data.startswith("edit_-"):
          target = callback.data[6:]
          db.update_anketa(user_id, target, '')
          await callback.answer(f"{"Instagram" if target == "insta" else "Steam"} отвязан")
          await bot.edit_message_caption(user_id, anketa, caption=caption_anket(user_id), reply_markup=inline.edit(user_id), parse_mode="HTML")



@router.message(StateFilter(Edit.insta))
async def edit_insta(message: Message, state: FSMContext, bot: Bot):
     user_id = message.from_user.id
     d = await state.get_data()
     tech1, anketa = d['tech1'], d['anketa']

     if message.text.startswith('@') and insta_valid(message.text[1:]):
          db.update_anketa(user_id, "insta", message.text[1:])
          await message.delete()
          await bot.delete_message(user_id, tech1)
          await bot.edit_message_caption(user_id, anketa, caption=caption_anket(user_id), reply_markup=inline.edit(user_id), parse_mode="HTML")
          await state.set_state(Edit.menu)
     else:
          await bot.edit_message_text("Некорректный @username, попробуй еще раз", user_id, tech1)
          await message.delete()
          return
     
          

@router.message(StateFilter(Edit.steam))
async def edit_steam(message: Message, state: FSMContext, bot: Bot):
     user_id = message.from_user.id
     d = await state.get_data()
     tech1, anketa = d['tech1'], d['anketa']

     if  message.text.startswith('https://steamcommunity.com/') and steam_valid(message.text):
          db.update_anketa(user_id, "steam", message.text[1:])
          await message.delete()
          await bot.delete_message(user_id, tech1)
          await bot.edit_message_caption(user_id, anketa, caption=caption_anket(user_id), reply_markup=inline.edit(user_id), parse_mode="HTML")
          await state.set_state(Edit.menu)
     else:
          await bot.edit_message_text("Некорректная ссылка, попробуй еще раз", user_id, tech1)
          await message.delete()
          return
     


@router.message(StateFilter(Edit.text), F.text)
async def edit_text(message: Message, state: FSMContext, bot: Bot):
     user_id = message.from_user.id
     d = await state.get_data()
     anketa, tech1 = d['anketa'], d['tech1']
     if message.text == "Оставить пустым":
          db.update_anketa(user_id, "text", '')
          await bot.edit_message_caption(user_id, anketa, caption=caption_anket(user_id), reply_markup=inline.edit(user_id), parse_mode="HTML")

     else:    
          if len(message.text) > 1000:
               await bot.edit_message_text("Описание должно быть длинной до 1000 символов", user_id, tech1)
               return
          db.update_anketa(user_id, "text", message.text)
          await edit_util1(bot, message, Edit, anketa, tech1, inline, state, caption_anket)



@router.message(StateFilter(Edit.photo), F.photo)
async def edit_photo(message: Message, state: FSMContext, bot: Bot):
     d = await state.get_data()
     anketa, tech1 = d['anketa'], d['tech1']
     
     db.update_anketa(message.from_user.id, "photo", message.photo[-1].file_id)
     await message.delete()
     await bot.delete_message(message.from_user.id, tech1)
     await bot.edit_message_media(
          InputMediaPhoto(
               media = db.get_photo(message.from_user.id), 
               caption = caption_anket(message.from_user.id),
               parse_mode="HTML"
          ), 
          message.from_user.id, anketa, reply_markup=inline.edit(message.from_user.id)
     )
     await state.set_state(Edit.menu)



@router.message(StateFilter(Edit.name), F.text)
async def edit_name(message: Message, state: FSMContext, bot: Bot):
     d = await state.get_data()
     anketa, tech1 = d['anketa'], d['tech1']

     if len(message.text) > 15:
          await bot.edit_message_text("Слишком длинное имя", message.from_user.id, tech1)
          return
     db.update_anketa(message.from_user.id, "name", message.text)
     await edit_util1(bot, message, Edit, anketa, tech1, inline, state, caption_anket)



@router.message(StateFilter(Edit.age), F.text.isdigit())
async def edit_age(message: Message, state: FSMContext, bot: Bot):
     d = await state.get_data()
     anketa, tech1 = d['anketa'], d['tech1']

     if 12 > int(message.text) or int(message.text) > 90:
          await bot.edit_message_text("Какой-то странный возраст", message.from_user.id, tech1)
          return
     
     db.update_anketa(message.from_user.id, "age", message.text)
     await edit_util1(bot, message, Edit, anketa, tech1, inline, state, caption_anket)



@router.callback_query(StateFilter(Edit.gender))
async def edit_gender(callback: CallbackQuery, state: FSMContext, bot: Bot):
     tech1 = (await state.get_data())['tech1']

     gender=1 if callback.data == "gboy" else 0
     db.update_anketa(callback.from_user.id, "gender", gender)
     await callback.answer("Гендер изменен", show_alert=True)
     await bot.delete_message(callback.from_user.id, tech1)
     await state.set_state(Edit.menu)



@router.callback_query(StateFilter(Edit.interest))
async def edit_interest(callback: CallbackQuery, state: FSMContext, bot: Bot):
     tech1 = (await state.get_data())['tech1']

     interest=1 if callback.data == "iboy" else 0 if callback.data == "igirl" else 2
     db.update_anketa(callback.from_user.id, "interest", interest)
     await callback.answer("Интерес изменен", show_alert=True)
     await bot.delete_message(callback.from_user.id, tech1)
     await state.set_state(Edit.menu)



@router.inline_query(StateFilter(Edit.games))
async def edit_games(iquery: InlineQuery):
     query=iquery.query.strip().lower() 
     results=[]

     for title, logo in gamesdict.items():
          if query.strip() in title.lower():  
               results.append(InlineQueryResultArticle(
               id=title,
               title=title,
               description=games_description(title),
               thumb_url=logo,
               input_message_content=InputTextMessageContent(
                    message_text=f"— {title}",  
                    parse_mode="HTML"
                    )
               ))

     await iquery.answer(results, is_personal=True)



@router.chosen_inline_result(StateFilter(Edit.games))
async def echosed_games1(iquery: ChosenInlineResult, state: FSMContext, bot: Bot):
     user_id = iquery.from_user.id
     games = db.get_games(user_id)
     game = iquery.result_id
     d = await state.get_data()
     anketa, tech1 = d['anketa'], d['tech1']
     me=await bot.get_me()

     if game == "Любые игры" and "Любые игры" not in games: 
          games.remove.all, games.append(game)  

     games.append(game) if game not in games else games.remove(game)

     if games != []:
          if len(games) < 4:
               db.update_anketa(user_id, "games", ", ".join(games))
               await bot.edit_message_caption(user_id, anketa, caption=caption_anket(user_id), reply_markup=inline.edit(user_id), parse_mode="HTML")
               
               if len(games) < 3:
                    await bot.delete_message(user_id, tech1)
                    tech1 = await bot.send_message(user_id, games_text(me.username), reply_markup=reply.confirm,  parse_mode="HTML")
                    await state.update_data(tech1 = tech1.message_id)

               else:
                    await bot.delete_message(user_id, tech1)
                    await state.set_state(Edit.menu)
          else:
               await bot.delete_message(user_id, tech1)
               tech1 = await bot.send_message(user_id, f"Количество игр превышает максимум.\n{games_text(me.username)}", reply_markup=reply.confirm,  parse_mode="HTML")
               await state.update_data(tech1 = tech1.message_id)
               return
     else:
          await bot.delete_message(user_id, tech1)
          tech1 = await bot.send_message(user_id, f"Игры не могут быть пустыми.\n{games_text(me.username)}", 
                                         reply_markup=reply.confirm,  parse_mode="HTML")
          await state.update_data(tech1 = tech1.message_id)
          return
     
     

@router.message(StateFilter(Edit.games))
async def echosed_games2(message: Message, state: FSMContext, bot: Bot):
     tech1 = (await state.get_data())['tech1']
     if message.text == "Продолжить":
          await state.set_state(Edit.menu)
          await message.delete()
          await bot.delete_message(message.from_user.id, tech1)



@router.inline_query(StateFilter(Edit.city))
async def edit_city(iquery: InlineQuery):
     query=iquery.query.lower() 
     results=[]

     if query.strip():
          for city in get_cities(query):
               if query in city[1].lower():
                    description = ', '.join(i for i in city[2:] if i is not None)
                    results.append(InlineQueryResultArticle(
                    id=city[0],
                    title=city[1],
                    description=description + '\n',
                    input_message_content=InputTextMessageContent(
                         message_text=f"— {city[1]}",  
                         parse_mode="HTML"
                         )))

     await iquery.answer(results, is_personal=True)  



@router.chosen_inline_result(StateFilter(Edit.city))
async def echosed_city(iquery: ChosenInlineResult, state: FSMContext, bot: Bot):
     d = await state.get_data()
     anketa, tech1 = d['anketa'], d['tech1']
     cities = get_cities(iquery.query.lower())
     for city in cities:
          if city[0] == iquery.result_id:
               city = city
               break
     user_id = iquery.from_user.id
     db.update_anketa(user_id, "city", ", ".join(i for i in city[1:] if i is not None))
     await bot.delete_message(user_id, tech1)
     await bot.edit_message_caption(user_id, anketa, caption=caption_anket(user_id), reply_markup=inline.edit(user_id), parse_mode="HTML")
     await state.set_state(Edit.menu)