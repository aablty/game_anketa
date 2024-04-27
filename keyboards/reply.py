from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def kbs(button_text):
     return ReplyKeyboardMarkup(
          keyboard=[[
               KeyboardButton(text=button_text)
          ]],
          resize_keyboard=True
     )

confirm, skip, empty = kbs("Продолжить"), kbs("Пропустить"), kbs("Оставить пустым")



def reacts():
     keyboard=[]
     for e in ["❤️", "💌|📷", "👎", "✖️"]:
          keyboard.append(
               KeyboardButton(text=e)
          )

     return ReplyKeyboardMarkup(
          keyboard=[keyboard],
          resize_keyboard=True
     )