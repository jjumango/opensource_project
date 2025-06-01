import requests

# 1. 도시명으로 위도/경도 가져오기
def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("results")
        if results:
            latitude = results[0]["latitude"]
            longitude = results[0]["longitude"]
            return latitude, longitude
        else:
            print("도시를 찾을 수 없습니다.")
            return None, None
    except Exception as e:
        print("좌표 가져오기 실패:", e)
        return None, None

# 2. 위도/경도로 현재 날씨 코드와 기온 가져오기
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("current")
        if data:
            code = data.get("weather_code")
            temp = data.get("temperature_2m")
            return code, temp
        else:
            print("현재 날씨 정보를 찾을 수 없습니다.")
            return None, None
    except Exception as e:
        print("날씨 가져오기 실패:", e)
        return None, None

# 3. 날씨 코드 해석
def interpret_weather_code(code):
    if code in [0]: return "맑음"
    elif code in [1, 2, 3]: return "흐림"
    elif code in [45, 48]: return "안개"
    elif code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]: return "비"
    elif code in [71, 73, 75, 77, 85, 86]: return "눈"
    elif code in [95, 96, 99]: return "뇌우"
    else: return "정보없음"