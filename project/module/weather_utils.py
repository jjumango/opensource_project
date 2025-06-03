# module/weather_utils.py

import requests

def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}
    response = requests.get(url, params=params)
    results = response.json().get("results")
    if results:
        return results[0]["latitude"], results[0]["longitude"]
    return None, None

def get_temperature_and_weathercode(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
        "timezone": "Asia/Seoul"
    }
    response = requests.get(url, params=params)
    data = response.json()
    temp = data["current"]["temperature_2m"]
    code = data["current"]["weather_code"]
    return temp, code

def get_weather_comment(code):
    code_map = {
        0: "맑음", 1: "대체로 맑음", 2: "부분 흐림", 3: "흐림",
        45: "안개", 48: "서리 안개", 51: "약한 이슬비",
        61: "약한 비", 71: "약한 눈", 95: "천둥번개"
    }
    return code_map.get(code, "알 수 없음")
