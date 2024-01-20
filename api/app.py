from flask import Flask, request, render_template, send_file, jsonify, after_this_request
import tempfile
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheHandler
from helper import is_valid_spotify_url, get_song_metadata
import traceback
from flask_cors import CORS
import requests, json
from io import BytesIO
#from vercel_storage import blob
import time, secrets
from datetime import datetime, timedelta
from mutagen.id3 import ID3, APIC
from PIL import Image
import dropbox
blob_files = {}
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
client_id=os.environ.get('CLIENT_ID')
client_secret=os.environ.get('CLIENT_SECRET')
ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')
class CustomCacheHandler(CacheHandler):
    def __init__(self):
        self.cache_path = None

    def get_cached_token(self):
        cached_token = os.environ.get('MY_API_TOKEN')
        return eval(cached_token) if cached_token else None

    def save_token_to_cache(self, token_info):
        os.environ['MY_API_TOKEN'] = str(token_info)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, cache_handler=CustomCacheHandler()))

@app.route('/deletefile', methods=['POST'])
def deletingfile():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if 'dkey' in data and data['dkey'] in blob_files:
                #blob.delete(blob_files[data['dkey']])
                try:
                    url = "https://api.dropboxapi.com/2/files/delete_v2"
                    url2 = "https://api.dropboxapi.com/2/files/permanently_delete"
                    headers = {
                        "Authorization": f"Bearer {ACCESS_TOKEN}",
                        "Content-Type": "application/json"
                    }
                    dropbox_path = blob_files[data['dkey']]
                    rdata = {
                        "path": dropbox_path
                    }
                    r = requests.post(url, headers=headers, data=json.dumps(rdata))
                    r = requests.post(url2, headers=headers, data=json.dumps(rdata))
                    
                    return jsonify({'success': True}), 200
                except:
                    traceback.print_exc()
                    return jsonify({'success': False, 'filepath': dropbox_path, 'error': traceback.format_exc()}), 400
            else:
                return jsonify({'success': False, 'error': 'Key Mismatch or File does not exist'}), 400


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
                    return jsonify({'success': False, 'error': 'Song not found or invalid URL', 'errorinfo' : traceback.format_exc()}), 400
            else:
                track_name = data.get('name')
                try:
                    results = sp.search(q=track_name, type='track', limit=1)['tracks']['items'][0]
                except:
                    return jsonify({'success': False, 'error': 'Song not found'}), 400
                url = 'https://api.spotifydown.com/download/' + results['id']
                audiobytes, filename = get_mp3(url)
            cover_art_url = results['album']['images'][0]['url']
            filelike = BytesIO(audiobytes)
            merged_file = add_cover_art(filelike, cover_art_url)
            token = secrets.token_hex(12)
            try:
                #resp = blob.put(
                #    pathname=filename,
                #    body=merged_file.read()
                #)
                #blob_files[token] = resp['url']
                dropbox_path = f"/songs/{filename}"
                file_url, direct_url = upload_file(merged_file, dropbox_path)
                blob_files[token] = dropbox_path
                return jsonify({'success': True, 'url': direct_url, 'filename' : filename, 'dkey' : token}), 200
            except Exception as e:
                return jsonify({'success': False, 'error': traceback.format_exc()}), 400
        else:
            return render_template('home.html')
    else:
        return render_template('home.html')

def upload_file(f, dropbox_path):
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    response = dbx.files_upload(f.read(), dropbox_path, autorename=True)
    shared_link_metadata = dbx.sharing_create_shared_link(path=response.path_display)
    direct_link = shared_link_metadata.url.replace('&dl=0', '&dl=1')
    direct_link2 = direct_link.replace('https://www.dropbox.com', 'https://dl.dropboxusercontent.com')
    return direct_link, direct_link2

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
        audiobytes = response.content
        return audiobytes, filename
    else:
        return None, None
    
def add_cover_art(audio_file, cover_art_url):
    audio_file.seek(0)
    tags = ID3()
    cover_image_data = BytesIO(requests.get(cover_art_url).content)
    tags['APIC'] = APIC(
        encoding=0,  # 0 is for utf-8
        mime='image/jpeg',
        type=3,  # 3 is for the front cover
        desc=u'Cover',
        data=cover_image_data.getvalue()
    )
    tags.save(audio_file)
    audio_file.seek(0)
    return audio_file

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443)
