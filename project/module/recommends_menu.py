import json
import random

def load_menulist(filename="menulist.json"):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def temp_category(temp):
    if temp <= 8:
        return "추움"
    elif temp <= 20:
        return "선선"
    else:
        return "더움"
    
def recommends_menu(weather, temp, menulist):
    temp_type = temp_category(temp)
    weather_menu = menulist.get(weather, menulist["정보없음"])
    return random.choice(weather_menu.get(temp_type, []))