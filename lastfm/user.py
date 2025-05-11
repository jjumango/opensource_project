class User:
    def __init__(self, app):
        self.app = app

    def get_recent_tracks(self, user, limit=5):
        params = {
            'method': 'user.getrecenttracks',
            'user': user,
            'api_key': self.app.api_key,
            'format': 'json',
            'limit': limit
        }
        data = self.app.request_auto(params)
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
