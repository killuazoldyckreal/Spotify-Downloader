from flask import Flask, request, render_template, send_file, redirect, jsonify, after_this_request, send_from_directory
import logging, os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheHandler
from api.helper import is_valid_spotify_url, MDATA
import traceback
from flask_cors import CORS
import requests
from io import BytesIO
logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
cache_path = "api/.spotify_cache"

if not os.path.exists(cache_path):
    os.makedirs(cache_path)
client_id=os.environ.get('CLIENT_ID')
client_secret=os.environ.get('CLIENT_SECRET')
class CustomCacheHandler(CacheHandler):
    def __init__(self, cache_path):
        self.cache_path = cache_path

    def get_cached_token(self):
        cache_file = os.path.join(self.cache_path, 'token.txt')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                token_info = f.read()
                return eval(token_info) if token_info else None

    def save_token_to_cache(self, token_info):
        cache_file = os.path.join(self.cache_path, 'token.txt')
        with open(cache_file, 'w') as f:
            f.write(str(token_info))
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, cache_handler=CustomCacheHandler(cache_path)))

@app.route('/.well-known/pki-validation/<filename>')
def verification_file(filename):
    return send_from_directory('verification', filename)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/download', methods=['HEAD','GET','POST'])
def downloading():
    app.logger.debug('Received request to /download with method: %s', request.method)
    if request.method == 'GET':
        # Handle GET request
        return jsonify({'message': 'This is a GET request on /download'})
    elif request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if 'track_id' in data:
                track_id = data.get('track_id')
                url = 'https://api.spotifydown.com/download/' + track_id
                try:
                    results = sp.track(track_id)
                    audiobytes, filename = get_mp3(url)
                except:
                    traceback.print_exc()
                    return jsonify({'success': False, 'error': 'Song not found or invalid URL'}), 400
            else:
                track_name = data.get('name')
                try:
                    results = sp.search(q=track_name, type='track', limit=1)['tracks']['items'][0]
                except:
                    return jsonify({'success': False, 'error': 'Song not found'}), 400
                url = 'https://api.spotifydown.com/download/' + results['id']
                audiobytes, filename = get_mp3(data, url)
            try:
                if audiobytes and filename:
                    file_like = MDATA(filename, results).add_cover_art(audiobytes)
                    return send_file(file_like, as_attachment=False, download_name=filename, mimetype='audio/mpeg'), 200
                return jsonify({'success': False, 'error': 'Song not found'}), 400
            except Exception as e:
                return jsonify({'success': False, 'error': traceback.format_exc()}), 400
        else:
            return render_template('home.html')
    else:
        return render_template('home.html')

def get_mp3(url):
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Origin': 'https://spotifydown.com',
        'Pragma': 'no-cache',
        'Referer': 'https://spotifydown.com/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Gpc': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    new_url = data['link']
    new_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Origin': 'https://spotifydown.com',
        'Pragma': 'no-cache',
        'Referer': 'https://spotifydown.com/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Gpc': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    response = requests.get(new_url, headers=new_headers)

    if response.ok:
        content_disposition = response.headers.get('Content-Disposition')
        filename = content_disposition.split('filename=')[1].replace('"', '') if content_disposition else 'output.mp3'
        audiobytes = BytesIO(response.content)
        return audiobytes, filename
    else:
        return None, None

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443)
