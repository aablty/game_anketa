from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(
     keyboard = [
          [
               KeyboardButton(text="1"),
               KeyboardButton(text="2"),
               KeyboardButton(text="3")
          ]
     ],
     resize_keyboard=True
)



gender = ReplyKeyboardMarkup(
     keyboard = [
          [
               KeyboardButton(text="Я парень"),
               KeyboardButton(text="Я девушка")
          ]
     ],
     resize_keyboard=True
)



interest_gender = ReplyKeyboardMarkup(
     keyboard = [
          [
               KeyboardButton(text="Парни"),
               KeyboardButton(text="Девушки"),
               KeyboardButton(text="Все равно")
          ]
     ],
     resize_keyboard=True
)

confirm = ReplyKeyboardMarkup(
     keyboard= [
          [
               KeyboardButton(text="Продолжить")
          ]
     ],
     resize_keyboard=True
)

def geoloc(town: str = None):
     keyboard= []
     keyboard.append([KeyboardButton(text=town)]) if town else None
     keyboard.append([KeyboardButton(text="Отправить мои координаты", request_location=True)])

     geoloc = ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard=True)
     return geoloc


skip = ReplyKeyboardMarkup(
     keyboard= [
          [
               KeyboardButton(text="Пропустить")
          ]
     ],
     resize_keyboard=True
)