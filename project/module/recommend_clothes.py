import random
from module.clothes_data import clothes_dict

# 스타일 선택: 나이에 따라 다르게
def get_style_options(gender: str, age: int):
    age_group = "20~28" if age <= 28 else "29~"
    try:
        return list(clothes_dict[gender][age_group].keys())
    except KeyError:
        return []

# 나이 그룹 설정
def get_age_group(age):
    if age <= 28:
        return "20~28"
    else:
        return "29~"

# 온도 구간 해석
def get_temperature_range(temp):
    if temp >= 28:
        return "28↑"
    elif 23 <= temp <= 27:
        return "23~27"
    elif 17 <= temp <= 22:
        return "17~22"
    elif 12 <= temp <= 16:
        return "12~16"
    elif 5 <= temp <= 11:
        return "5~11"
    else:
        return "0↓"

# 최종 추천 함수
def recommend_outfit(gender, age, style, temp):
    age_group = get_age_group(age)
    temp_range = get_temperature_range(temp)

    try:
        outfit_options = clothes_dict[gender][age_group][style][temp_range]
        return random.sample(outfit_options, min(3, len(outfit_options)))
    except KeyError:
        return ["❌ 추천 정보를 찾을 수 없습니다."]
