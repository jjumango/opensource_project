from flask import Flask, request, render_template, redirect, url_for
from module.open_meteo import get_coordinates, get_weather, interpret_weather_code
from module.recommends_todo import recommends_todo
from module.recommend_menu import load_menulist, recommend_menu
from module.recommend_clothes import get_style_options, recommend_outfit
from module.recommends_music import (
    recommend_music_by_weather,
    get_user_permission_and_recommend,
    recommend_music_by_user
)
from module import recommends_music


app = Flask(__name__)
lastfm_key_set = False

@app.route('/', methods=['GET', 'POST'])
def index():
    city = None
    weather = "정보없음"
    temp = None
    if request.method == 'POST':
        city = request.form['city'].strip()
        lat, lon = get_coordinates(city)
        if lat is not None and lon is not None:
            code, temp = get_weather(lat, lon)
            if code is not None and temp is not None:
                weather = interpret_weather_code(code)
    return render_template("index.html", city=city, weather=weather, temp=temp)

@app.route('/weather/<city>/todo')
def todo(city):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        weather_desc = "정보없음"
        temp = 15
    else:
        code, temp = get_weather(lat, lon)
        weather_desc = interpret_weather_code(code)

    recommended = recommends_todo(weather_desc)
    return render_template("index.html", city=city, weather=weather_desc, temp=temp, todo=recommended, path=request.path)

@app.route('/weather/<city>/food', methods=['GET', 'POST'])
def food(city):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        weather_desc = "정보없음"
        temp = 15
    else:
        code, temp = get_weather(lat, lon)
        weather_desc = interpret_weather_code(code)

    menu_result = None
    if request.method == 'POST':
        category = request.form.get('category')
        menulist = load_menulist()
        result = recommend_menu(city, weather_desc, temp, category, menulist)
        if result.get("error"):
            menu_result = f"오류: {result['error']}"
        else:
            menu_result = f"{category} 중 추천 음식: {result['menu']}"

    return render_template("index.html", city=city, weather=weather_desc, temp=temp, menu=menu_result, path=request.path)

from flask import request, render_template
from module.recommend_clothes import get_style_options, recommend_outfit
from module.weather_utils import (
    get_coordinates,
    get_temperature_and_weathercode,
    get_weather_comment
)

@app.route('/weather/<city>/clothes', methods=['GET', 'POST'])
def clothes(city):
    weather_desc = ""
    temp = 0
    outfit_list = []
    style_list = []
    gender = ""
    age = ""
    selected_style = ""

    # 현재 날씨 정보 가져오기
    lat, lon = get_coordinates(city)
    temp, weather_code = get_temperature_and_weathercode(lat, lon)
    weather_desc = get_weather_comment(weather_code)

    # POST일 때 폼 처리
    if request.method == 'POST':
        gender = request.form.get('gender')        # '남' 또는 '여'
        age = request.form.get('age')              # 숫자 문자열
        selected_style = request.form.get('style') # 선택된 스타일 (nullable)

        try:
            age_int = int(age)

            # 🔹 스타일 선택 목록 생성 (성별+나이 기반으로)
            style_list = get_style_options(gender, age_int)

            # 🔹 스타일이 선택되었을 때만 추천 실행
            if selected_style:
                outfit_list = recommend_outfit(gender, age_int, selected_style, temp)

        except ValueError:
            outfit_list = ["❗ 나이를 숫자로 입력해주세요."]
        except Exception as e:
            outfit_list = [f"⚠️ 오류 발생: {str(e)}"]

    return render_template(
        "index.html",
        city=city,
        weather=weather_desc,
        temp=temp,
        outfit=outfit_list,
        style_list=style_list,
        selected_style=selected_style,
        gender=gender,
        age=age,
        path=request.path
    )

@app.route('/weather/<city>/music', methods=['GET', 'POST'])
def music(city):
    global lastfm_key_set

    if request.method == 'POST':
        api_key = request.form.get('apikey')
        if not api_key:
            return render_template("index.html", city=city, path=request.path, music_error="API 키를 입력해주세요.")

        recommends_music.lastfm_api_key = api_key
        lastfm_key_set = True

    if not lastfm_key_set:
        return render_template("index.html", city=city, path=request.path, lastfm_key_set=False)

    result = recommends_music.recommend_music_by_weather(city)
    if result:
        weather = result.get("weather", "정보없음")
        genre = result.get("genre", "정보없음")
        tracks = result.get("tracks", [])
    else:
        weather = "정보없음"
        genre = "정보없음"
        tracks = []

    track_text = "\n".join([f"{artist} - {title}" for artist, title in tracks])

    return render_template(
        "index.html",
        city=city,
        weather=weather,
        temp=15,
        music_genre=genre,
        music_tracks=track_text,
        path=request.path,
        lastfm_key_set=True
    )

@app.route('/weather/<city>/music/user', methods=['GET', 'POST'])
def user_music(city):
    global lastfm_key_set
    genre = None
    recommended = []
    recent = []
    music_error = None

    if not lastfm_key_set:
        return redirect(url_for('music', city=city))

    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            music_error = "사용자 이름을 입력해주세요."
        else:
            result = recommends_music.recommend_music_by_user(username)
            if not result:
                music_error = "추천 결과를 가져오지 못했습니다."
            else:
                genre = result.get("genre", "정보없음")
                recommended = result.get("recommended", [])
                recent = result.get("recent", [])

    recommended_tracks = "\n".join([f"{a} - {t}" for a, t in recommended])
    recent_tracks = "\n".join([f"{a} - {t}" for a, t in recent])

    return render_template(
        "index.html",
        city=city,
        user_music_genre=genre,
        user_recommended_tracks=recommended_tracks,
        user_recent_tracks=recent_tracks,
        music_error=music_error,
        path=request.path,
        lastfm_key_set=True
    )

if __name__ == "__main__":
    app.run(debug=True)
