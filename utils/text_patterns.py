from database.db import Base

db = Base()



def games_text(me):
     return (f"Выберите интересующие вас 1-3 игры. Введите @{me} [название игры].\n\n"
               f"Пример: <code>@{me} Valorant</code>")


def games_description(title):
     d = f"INFO\nИнтересуются: {db.count_games(title)}"
     return d


def city_text(me):
     return (f"Выберите свой город. Введите @{me}  [название города].\n\n"
               f"Пример: <code>@{me} Москва</code>")


def caption_anket(user_id):
     c = db.get_caption(user_id)
     name, age, city, text, insta, steam = c[0], c[1], c[2].split(", ")[0], c[3], c[5], c[6]
     games = []
     for g in c[4].split(', '):
          a = '#' + g.replace(' ', '_')
          games.append(a)
     caption = f"{name}, {age}, {city}{" – " + text if text else ""}\n\nИгры — {', '.join(games)}\n\n"\
               f"{f"<a href='https://www.instagram.com/{insta}'>Instagram</a>\n" if insta else ""}"\
               f"{f"<a href='{steam}'>Steam</a>" if steam else ""}"
     return caption




