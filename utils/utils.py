from config.config import config
from geopy.geocoders import Nominatim
from database.db import Base

import json
import hashlib
import requests


geolocator = Nominatim(user_agent="GeoCode")



with open('./utils/gamesdict.json', 'r', encoding='utf-8') as file:
     gamesdict = json.load(file)


def generate_unique_id(text):
    return hashlib.md5(text.encode()).hexdigest()


def get_cities(query: str):
     url = "https://api.vk.com/method/database.getCities"
     params = {
          'access_token': config.access_token.get_secret_value(), 
          'v': '5.199', 
          'q': query, 
          'need_all': 1,
          'count': 5,
          'lang': 'ru'  
     }

     response = requests.get(url, params=params)
     if response.status_code == 200:
          data = response.json()['response']['items']
          cities = []
          for item in data:
               city = [
                    str(item.get('id')),
                    item.get('title', None),
                    item.get('area', None),
                    item.get('region', None),
                    item.get('country', None)
               ]
               cities.append(city)
          return cities
     else:
          return None


def steam_valid(url):
     try:
          response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
          return response.status_code == 200
     
     except requests.RequestException:
          return False


def insta_valid(username):
     try:
          response = requests.get(f"https://www.instagram.com/{username}", headers={"User-Agent": "Mozilla/5.0"})
          return response.status_code == 200
     
     except requests.RequestException:
          return False


async def edit_util1(bot, message, Edit, anketa, tech1, inline, state, caption_anket):
     user_id = message.from_user.id
     await message.delete()
     await bot.edit_message_caption(user_id, anketa, caption=caption_anket(user_id), reply_markup=inline.edit(user_id), parse_mode="HTML")
     await bot.delete_message(user_id, tech1)
     await state.set_state(Edit.menu)


async def edit_util2(bot, user_id, state, text, state_, reply):
     tech1 = await bot.send_message(user_id, text, reply_markup=reply)
     await state.update_data(tech1 = tech1.message_id)
     await state.set_state(state_)