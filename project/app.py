from flask import Flask, request, redirect, url_for
from module.open_metro import get_coordinates, get_weather, interpret_weather_code
from module.recommends_todo import recommends_todo
from module.recommends_menu import load_menulist, recommends_menu
from module.recommends_music import recommend_music_by_weather, get_user_permission_and_recommend, recommend_music_by_user
from module.recommend_clothes import recommend_outfit
from module import recommends_music

app = Flask(__name__)

city_name = None
lastfm_key_set = False

topics = [
    {'id': 1, 'title': '할 일 추천', 'body': '실시간 날씨에 맞춘 새로운 할 일을 추천해 드립니다.' },
    {'id': 2, 'title': '음식 추천', 'body': '실시간 날씨에 맞추어 어울리는 음식을 추천해 드립니다.' },
    {'id': 3, 'title': '음악 추천', 'body': '실시간 날씨에 맞추어 어울리는 음악을 추천해 드립니다.' },
    {'id': 4, 'title': '옷 추천', 'body': '실시간 날씨에 맞추어 온도에 맞는 복장을 제시해 드립니다.' },
]

def template(contents, content, city=None):
    contextUI = ''
    if city:
        contextUI = f'''
            <li><a href="/weather/{city}/todo">할 일 추천</a></li>
            <li><a href="/weather/{city}/food">음식 추천</a></li>
            <li><a href="/weather/{city}/music">음악 추천</a></li>
            <li><a href="/weather/{city}/clothes">옷 추천</a></li>
        '''
    return f'''<!doctype html>
    <html>
        <body>
            <h1><a href="/">Weather Life</a></h1>
            <ol>
                {contents}
            </ol>
            {content}
            <ul>
                {contextUI}
            </ul>
        </body>
    </html>
    '''

def getContents(city):
    liTags = '<p><strong>기능 설명:</strong></p>'
    for topic in topics:
        liTags += f'<li><a href="/weather/{city}/read/{topic["id"]}">{topic["title"]}</a></li>'
    return liTags

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city'].strip()
        if city:
            return redirect(url_for('weather_home', city=city))
    return '''
    <!doctype html>
    <html>
        <body>
            <h1><a href="/">Weather Life</a></h1>
            <ol>
            
            </ol>
            <h2>실시간 날씨에 맞추어 할 일을 추천해드립니다.</h2>
            <p>원하는 도시를 입력해주시면 추천 기능을 제공해드립니다.</p>
            <form method="POST">
                <input type="text" name="city" placeholder="영어로 도시 입력(예:Seoul) " required>
                <input type="submit" value="입력">
            </form>
        </body>
    </html>
    '''

@app.route('/weather/<city>')
def weather_home(city):
    contents = getContents(city)

    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        weather_info = f'<p>죄송합니다, "{city}" 도시를 찾을 수 없습니다.</p>'
    else:
        code, temp = get_weather(lat, lon)
        if code is None or temp is None:
            weather_info = f'<p>죄송합니다, "{city}"의 날씨 정보를 가져올 수 없습니다.</p>'
        else:
            weather_desc = interpret_weather_code(code)
            weather_info = f'<p>현재 {city.title()}의 날씨는 <strong>{weather_desc}</strong>이고, 기온은 <strong>{temp}°C</strong>입니다!</p>'

    return template(contents, f'<h2>{city.title()}</h2>{weather_info}', city)

@app.route('/weather/<city>/read/<int:id>')
def read(city, id):
    title = ''
    body = ''
    for topic in topics:
        if id == topic['id']:
            title = topic['title']
            body = topic['body']
            break
    return template(getContents(city), f'<h2>{title}</h2>{body}', city)

@app.route('/weather/<city>/todo')
def todo(city):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        weather_desc = "정보없음"
    else:
        code, _ = get_weather(lat, lon)
        weather_desc = interpret_weather_code(code) if code else "정보없음"

    recommended = recommends_todo(weather_desc)
    body = f'''
        <h2>할 일 추천</h2>
        <p><strong>현재 {city.title()}의 날씨는 {weather_desc}입니다.</strong></p>
        <p><strong>추천 활동:</strong> {recommended}</p>
    '''
    return template(getContents(city), body, city)

@app.route('/weather/<city>/food')
def food(city):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        weather_desc = "정보없음"
        temp = 15 
    else:
        code, temp = get_weather(lat, lon)
        weather_desc = interpret_weather_code(code) if code else "정보없음"

    menulist = load_menulist()
    recommended = recommends_menu(weather_desc, temp, menulist)

    body = f'''
        <h2>음식 추천</h2>
        <p><strong>현재 {city.title()}의 날씨는 {weather_desc}이며, 기온은 {temp}°C입니다.</strong></p>
        <p><strong>추천 음식:</strong> {recommended}</p>
    '''
    return template(getContents(city), body, city)

@app.route('/weather/<city>/clothes')
def clothes(city):
    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        weather_desc = "알 수 없음"
        temp = 15
    else:
        code, temp = get_weather(lat, lon)
        weather_desc = interpret_weather_code(code) if code else "알 수 없음"

    outfit_msg = recommend_outfit(temp, weather_desc)

    body = f'''
        <h2>옷 추천</h2>
        <p><strong>현재 {city.title()}의 날씨는 {weather_desc}이며, 기온은 {temp}°C입니다.</strong></p>
        <p><strong>추천 옷차림:</strong> {outfit_msg}</p>
    '''
    return template(getContents(city), body, city)

@app.route('/weather/<city>/music/user', methods=['GET', 'POST'])
def user_music(city):
    global city_name
    city_name = city

    if not lastfm_key_set:
        return redirect(url_for('music', city=city))  # API 키 없으면 music 라우트로 이동

    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return template(getContents(city), "<p> 사용자 이름을 입력해주세요.</p>", city)

        result = recommends_music.recommend_music_by_user(username)
        if not result:
            return template(getContents(city), "<p>추천 결과를 가져오지 못했습니다.</p>", city)

        genre = result.get("genre", "정보 없음")
        recommended_tracks = result.get("recommended", [])
        recent_tracks = result.get("recent", [])

        recommended_html = "<ul>"
        for artist, title in recommended_tracks:
            recommended_html += f"<li>{artist} - {title}</li>"
        recommended_html += "</ul>"

        recent_html = "<ul>"
        for artist, title in recent_tracks:
            recent_html += f"<li>{artist} - {title}</li>"
        recent_html += "</ul>"

        body = f'''
            <h2> 사용자 기반 음악 추천</h2>
            <p><strong>가장 많이 들은 장르:</strong> {genre}</p>
            <p><strong>추천 음악:</strong></p>
            {recommended_html}
            <p><strong>최근 들은 음악:</strong></p>
            {recent_html}
        '''
        return template(getContents(city), body, city)

    # GET 요청 시 사용자 이름 입력 폼
    return template(getContents(city), f'''
        <h2> 사용자 기반 음악 추천</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Last.fm 사용자 이름" required>
            <input type="submit" value="추천 받기">
        </form>
    ''', city)

@app.route('/weather/<city>/music', methods=['GET', 'POST'])
def music(city):
    global city_name, lastfm_key_set
    city_name = city  # 입력한 도시 저장
    if request.method == 'POST':
        api_key = request.form.get('apikey')
        if not api_key:
            return template(getContents(city), "<p> API 키를 입력해주세요.</p>", city)

        # API 키 설정
        recommends_music.lastfm_api_key = api_key
        lastfm_key_set = True

    if not lastfm_key_set:
        # API 키 입력 폼 보여주기
        body = f'''
            <h2> 음악 추천을 위해 Last.fm API 키를 입력해주세요</h2>
            <form method="POST">
                <input type="text" name="apikey" placeholder="Last.fm API Key" required>
                <input type="submit" value="제출">
            </form>
        '''
        return template(getContents(city), body, city)

    # 키가 설정되었을 경우 추천 실행
    result = recommends_music.recommend_music_by_weather(city)
    if result is None:
     weather= "정보없음"
     recommendations = []
    else:
        weather = result.get("weather", "정보없음")
        recommendations = result.get("recommendations", [])
        genre = result.get("genre", "unknown")
        tracks = result.get("tracks", [])

    track_html = "<ul>"
    for artist, title in tracks:
        track_html += f"<li>{artist} - {title}</li>"
    track_html += "</ul>"

    body = f'''
        <h2>음악 추천</h2>
        <p><strong>현재 {city.title()}의 날씨는 {weather}입니다.</strong></p>
        <p><strong>추천 장르:</strong> {genre}</p>
        <p><strong>추천 음악:</strong></p>
        {track_html}
        <br><a href="/weather/{city}/music/user"> 사용자 기반 추천도 보기</a>
    '''
    return template(getContents(city), body, city)

app.run(debug=True)