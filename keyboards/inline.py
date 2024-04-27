from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from database.db import Base

db = Base()


def menu():
     return InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(text="📋 Изменить", callback_data="edita")
               ],
               [
                    InlineKeyboardButton(text="🚀 Смотреть анкеты", callback_data="start")
               ]
          ]
     )


def gender():
     return InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(text="Я парень", callback_data="gboy"),
                    InlineKeyboardButton(text="Я девушка", callback_data="ggirl"),
               ]
          ]
     )


def interest():
     return InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(text="Парни", callback_data="iboy"),
                    InlineKeyboardButton(text="Девушки", callback_data="igirl"),
               ],
               [
                    InlineKeyboardButton(text="Все равно", callback_data="idm"),
               ]
          ]
     )



def edit(user_id):
     s = db.connections_state(user_id)
     return InlineKeyboardMarkup(
          inline_keyboard=[
               [
                    InlineKeyboardButton(text="🏷️ Имя", callback_data="edit_name"),
                    InlineKeyboardButton(text="🔞 Возраст", callback_data="edit_age"),
                    InlineKeyboardButton(text="🌎 Город", callback_data="edit_city")
               ],
               [    
                    InlineKeyboardButton(text="📷 Фото", callback_data="edit_photo"),
                    InlineKeyboardButton(text="🖊 Описание", callback_data="edit_text"),
                    InlineKeyboardButton(text="🎮 Игры", callback_data="edit_games"),
               ],
               [
                   
                    InlineKeyboardButton(text="⚧ Пол", callback_data="edit_gender"),
                    InlineKeyboardButton(text="👀 Кто интересен", callback_data="edit_interest")
               ],
               [
                   InlineKeyboardButton(text=f"{s[0][0]} Instagram", callback_data=f"edit_{s[0][1]}insta"),
                   InlineKeyboardButton(text=f"{s[1][0]} Steam", callback_data=f"edit_{s[1][1]}steam")
               ],
               [
                    InlineKeyboardButton(text="Вернуться назад", callback_data="edit_back")
               ]
          ]
     )
     