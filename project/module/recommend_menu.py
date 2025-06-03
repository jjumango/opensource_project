import json
import random

def load_menulist(filename="add_menulist.json"):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def temp_category(temp):
    if temp <= 8:
        return "추움"
    elif temp <= 20:
        return "선선"
    else:
        return "더움"

def recommend_menu(city, weather, temp, category, menulist):
    if not city or city.strip() == "":
        return {"error": "도시를 먼저 입력해 주세요!"}
    temp_type = temp_category(temp)
    weather_data = menulist.get(weather, menulist.get("정보없음", {}))
    temp_data = weather_data.get(temp_type, {})
    menu_list = temp_data.get(category)

    if not menu_list:
        return {"error": f"{weather}/{temp_type} 조건에 '{category}' 메뉴가 없어요."}
    return {"category": category, "menu": random.choice(menu_list)}