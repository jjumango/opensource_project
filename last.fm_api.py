import requests
import json

def get_weather(city):
    API_KEY = "자신의 API KEY"
    lang = "kr"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang={lang}&units=metric"

    response = requests.get(url)
    data = json.loads(response.text)

    if response.status_code == 200:
        print(f"{city}의 날씨: {data['weather'][0]['description']}")
        print(f"현재 기온: {data['main']['temp']}")
        print(f"체감 온도; {data['main']['feels_like']}")
        print(f"최저 기온: {data['main']['temp_min']}")
        print(f"최고 기온: {data['main']['temp_max']}")
        print(f"습도: {data['main']['humidity']}")
    else:
        print("error")

city_name = input("도시 이름을 입력하세요 (영어로 입력): ")
get_weather(city_name)

import random

def get_weather_main(city):
    API_KEY = "자신의 API KEY"
    lang = "kr"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang={lang}&units=metric"

    response = requests.get(url)
    data = json.loads(response.text)

    if response.status_code == 200:
        return data['weather'][0]['main']
    else:
        print("error")

get_weather_main(city_name)

lastfm_api_key = "자신의 LAST.FM API KEY"


weather_genre_map = {
    'Clear': ['indie', 'jazz', 'reggae', 'british', 'dance', 'hip-hop'],
    'Clouds': ['country', 'blues', 'classical'],
    'Rain': ['hip-hop', 'dance', 'electronic', 'rnb', 'blues'],
    'Drizzle': ['hip-hop', 'dance', 'electronic', 'rnb', 'blues'],
    'Squall': ['hardcore', 'alternative', 'rock', 'punk'],
    'Tornado': ['hardcore', 'alternative', 'rock', 'punk'],
    'Thunderstorm': ['hardcore', 'alternative', 'rock', 'punk'],
    'Dust': ['hardcore', 'alternative', 'rock', 'punk'],
    'Sand': ['hardcore', 'alternative', 'rock', 'punk'],
    'Snow': ['acoustic', 'blues', 'rnb'],
    'Mist': ['jazz', 'reggae', 'british', 'blues', 'hip-hop', 'electronic'],
    'Fog': ['jazz', 'reggae', 'british', 'blues', 'hip-hop', 'electronic'],
    'Haze': ['jazz', 'reggae', 'british', 'blues', 'hip-hop', 'electronic'],
    'Smoke': ['jazz', 'reggae', 'british', 'blues', 'hip-hop', 'electronic']
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

# 날씨에 따라 장르 선택 후 추천
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

# 사용자 수락 후 음악 추천
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

# 사용자 최근 트랙 정보 가져오기 (lfm 사용)
def get_recent_tracks(user, limit=5):
    params = {
        'method': 'user.getrecenttracks',
        'user': user,
        'api_key': lastfm_api_key,
        'format': 'json',
        'limit': limit
    }
    response = requests.get("http://ws.audioscrobbler.com/2.0/", params=params)  # 이 부분에서 API 요청
    data = response.json()
     # 응답 확인 코드 추가
    if 'recenttracks' not in data:
        print(" 최근 트랙 정보가 없습니다. 사용자 이름이나 API 키를 확인하세요.")
        print("응답 내용:", data)  # 디버깅용 출력
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

# 사용자 정보를 수집하여 최근 트랙 장르 기반 추천
def recommend_music_by_user(user):
    recent_tracks = get_recent_tracks(user)  # self를 제거한 함수 호출
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
            return tags[0]['name'].lower()  # 가장 상위 태그 반환
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

    # 장르별 인기 트랙 추천
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

  
