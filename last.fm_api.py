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

city_name = input("도시 이름을 입력하세요 (영어로 입력): ")
get_coordinates(city_name)

import random

def get_weather_main(city):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        print("위치 정보를 가져오지 못했습니다.")
        return None
    
    code, temp = get_weather(lat, lon)
    if code is None:
        print("날씨 정보를 가져오지 못했습니다.")
        return None
    
    return interpret_weather_code(code)

get_weather_main(city_name)

lastfm_api_key = "bb5b59ee8e285582b5b90e8aaa1055e9"


weather_genre_map = {
    "맑음": ['indie', 'jazz', 'reggae', 'british', 'dance', 'hip-hop'],
    "흐림": ['classical', 'reggae', 'country', 'blues', 'hip-hop', 'electronic'], 
    "안개": ['jazz', 'reggae', 'british', 'blues', 'hip-hop', 'electronic'],
    "비": ['hip-hop', 'dance', 'electronic', 'rnb', 'blues'],
    "눈": ['acoustic', 'blues', 'rnb'],
    "뇌우": ['hardcore', 'alternative', 'rock', 'punk'],
    "정보없음": ['indie', 'jazz', 'classical', 'british', 'dance', 'reggae', 'country', 'blues', 'hip-hop', 'electronic', 'rnb', 'acoustic', 'hardcore', 'alternative', 'rock', 'punk']
}

def get_top_tracks_by_genre(genre, limit=50):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'tag.gettoptracks',
        'tag': genre,
        'api_key': lastfm_api_key,
        'format': 'json',
        'limit': limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    tracks = data.get('tracks', {}).get('track', [])
    return [[track['artist']['name'], track['name']] for track in tracks]

def recommend_music_by_weather(city):
    weather_main = get_weather_main(city)
    
    genres = weather_genre_map.get(weather_main, ['pop'])
    selected_genre = random.choice(genres)
    print(f"\n 날씨 '{weather_main}'에 어울리는 장르: {selected_genre}")
    if not weather_main:
        print("날씨 데이터를 가져오지 못했습니다.")
        return

    tracks = get_top_tracks_by_genre(selected_genre)
    if not tracks:
        print("추천 트랙이 없습니다.")
        return

    recommendations = random.sample(tracks, 3) if len(tracks) >= 3 else tracks
    print(" 추천 트랙:")
    for artist, title in recommendations:
        print(f"- {artist} - {title}")

recommend_music_by_weather(city_name)

import time
from collections import Counter
from lastfm import lfm

def get_user_permission_and_recommend():
    user_input = input("사용자 정보를 수집하여 추천해드릴 수 있습니다. 수락: y/ 거절: n: ")
    if user_input.lower() == 'y':
        user_name = input("Last.fm 사용자 이름을 입력하세요: ")
        return user_name
    elif user_input.lower() == 'n':
        print("추천을 거절하셨습니다.")
        exit()
    else:
        print("잘못된 입력입니다.")

def get_recent_tracks(user, limit=5):
    params = {
        'method': 'user.getrecenttracks',
        'user': user,
        'api_key': lastfm_api_key,
        'format': 'json',
        'limit': limit
    }
    response = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)  
    data = response.json()
    
    if 'recenttracks' not in data:
        print(" 최근 트랙 정보가 없습니다. 사용자 이름이나 API 키를 확인하세요.")
        print("응답 내용:", data) 
        return []

    return data['recenttracks'].get('track', [])

    if 'recenttracks' not in data:
        raise Exception("최근 트랙 정보를 가져올 수 없습니다.")

    tracks = data['recenttracks'].get('track', [])
    result = []
    for track in tracks:
        artist = track['artist']['#text']
        title = track['name']
        url = track['url']
        result.append({'artist': {'name': artist}, 'name': title, 'url': url})
    return result


def recommend_music_by_user(user):
    recent_tracks = get_recent_tracks(user) 
    if not recent_tracks:
        print("사용자의 최근 트랙 데이터를 가져오지 못했습니다.")
        return
    
    def get_track_genre(artist, track):
        params = {
        'method': 'track.getInfo',
        'artist': artist,
        'track': track,
        'api_key': lastfm_api_key,
        'format': 'json'
    }
        response = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)
        data = response.json()
        tags = data.get('track', {}).get('toptags', {}).get('tag', [])
        if tags:
            return tags[0]['name'].lower()  
        return None

    genres = []
    for track in recent_tracks:
        artist = track['artist']['#text']
        title = track['name']
        genre = get_track_genre(artist, title)
        if genre:
            genres.append(genre)

    if not genres:
        print("장르를 파악할 수 없습니다.")
        return

    most_common_genre = Counter(genres).most_common(1)[0][0]
    print(f"\n 사용자에게 맞는 장르: {most_common_genre}")

    tracks = get_top_tracks_by_genre(most_common_genre)
    if not tracks:
        print("추천 음악이 없습니다.")
        return

    recommendations = random.sample(tracks, 3) if len(tracks) >= 3 else tracks
    print(" 장르에 따른 추천 음악:")
    for artist, title in recommendations:
        print(f"- {artist} - {title}")

    print("\n 최근 들은 음악:")
    for track in random.sample(recent_tracks, 2):
        print(f"- {track['artist']['#text']} - {track['name']}")

y = get_user_permission_and_recommend()
if y:
    recommend_music_by_user(y)

  
