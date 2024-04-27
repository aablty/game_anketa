import sqlite3

class Base:

    # database.db

     def __init__(self):
          self.base = sqlite3.connect('./database/database.db')
          self.cursor = self.base.cursor()


     def user_exists(self, user_id):
        return bool(len(self.cursor.execute("SELECT name FROM ankets WHERE user_id = ?", (user_id, )).fetchall()))
     
     
     def get_caption(self, user_id):
          return self.cursor.execute("""SELECT name, age, city, text, games, insta, steam
                                       FROM ankets WHERE user_id = ?""", (user_id, )).fetchone()


     def get_photo(self, user_id):
          return self.cursor.execute("SELECT photo FROM ankets WHERE user_id = ?", (user_id, )).fetchone()[0]


     def add_user_anketa(self, user_id, name, age, city, text, photo, games, gender, interest ):
          self.cursor.execute("INSERT INTO ankets (user_id, name, age, city, text, photo, games, gender, interest, status) VALUES\
               (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, name, age, city, text if text != '' else None, photo, games, gender, interest, 0))
          return self.base.commit()

     def update_anketa(self, user_id, type, new_value):
          self.cursor.execute(f"UPDATE ankets SET {type} = ? WHERE user_id = ?", (new_value if new_value != '' else None, user_id))
          return self.base.commit()

     def get_games(self, user_id):
          return self.cursor.execute("SELECT games FROM ankets WHERE user_id = ?", (user_id, )).fetchone()[0].split(", ")

     def delete_anketa(self, user_id):
          self.cursor.execute("DELETE FROM anketi WHERE users_id = ?", (user_id, ))
          return self.base.commit()

     def find_anketi(self, user_id, interest, city, age):
          gender: str = ""
          if interest == "парни":
               gender = "парень"
          if interest == "девушки":
               gender = "девушка"

          result = self.cursor.execute("""SELECT * FROM anketi 
                                       WHERE users_id != ? 
                                       AND gender = ? 
                                       AND city = ? 
                                       AND age BETWEEN ? AND ?""", 
                                       (user_id, gender, city.title(), int(age) - 1, int(age) + 1))

          return result.fetchall()
     
     def count_games(self, game):
          result = self.cursor.execute("SELECT COUNT(*) FROM ankets WHERE games LIKE ? OR games = 'Любые игры'", (f"%{game}%", ))
          return result.fetchone()[0]
     
     def connections_state(self, user_id):
          result = self.cursor.execute("SELECT insta, steam FROM ankets WHERE user_id = ?", (user_id, ))
          return [["➖", "-"] if bool(a) else ["➕", "+"] for a in result.fetchone()]

     def close(self):
          sqlite3.Connection.close()