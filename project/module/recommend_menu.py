import json
import random

# 1. JSON 불러오기
def load_menulist(filename="add_menulist.json"):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# 2. 숫자 온도를 카테고리로 변환
def temp_category(temp):
    if temp <= 8:
        return "추움"
    elif temp <= 20:
        return "선선"
    else:
        return "더움"

# 3. 추천 함수 (모든 조건 반영)
def recommend_menu(city, weather, temp, category, menulist):
    # 도시 미입력 시 추천 중단
    if not city or city.strip() == "":
        return {"error": "도시를 먼저 입력해 주세요!"}

    # 기온 숫자를 "추움/선선/더움"으로 변환
    temp_type = temp_category(temp)

    # 날씨 기준 데이터 찾기, 없으면 "정보없음"으로 대체
    weather_data = menulist.get(weather, menulist.get("정보없음", {}))

    # 기온 기준 데이터
    temp_data = weather_data.get(temp_type, {})

    # 사용자가 고른 카테고리(밥/면/빵 등)
    menu_list = temp_data.get(category)

    # 해당 조건에서 메뉴가 없다면
    if not menu_list:
        return {"error": f"{weather}/{temp_type} 조건에 '{category}' 메뉴가 없어요."}

    # 정상 추천
    return {"category": category, "menu": random.choice(menu_list)}