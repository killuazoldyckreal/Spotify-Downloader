from flask import Flask, request, render_template, jsonify
import os, requests, json, traceback, secrets
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from helper import is_valid_spotify_url, get_song_metadata, get_mp3, upload_file, add_mdata, CustomCacheHandler
from flask_cors import CORS
from io import BytesIO
import dropbox

active_files = {}
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
client_id=os.environ.get('CLIENT_ID')
client_secret=os.environ.get('CLIENT_SECRET')
ACCESS_KEY = os.environ.get('DROPBOX_KEY')
ACCESS_SECRET = os.environ.get('DROPBOX_SECRET')
ACCESS_TOKEN = os.environ.get('DROPBOX_TOKEN')

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, cache_handler=CustomCacheHandler()))

@app.route('/deletefile', methods=['POST'])
def deletingfile():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            if 'dkey' in data and data['dkey'] in active_files:
                try:
                    try:
                        dbx = dropbox.Dropbox(ACCESS_TOKEN)
                        dbx.users_get_current_account()
                    except:
                        new_access_token = dropbox.DropboxOAuth2FlowNoRedirect(ACCESS_KEY, ACCESS_SECRET).refresh_token(ACCESS_TOKEN)
                        os.environ['DROPBOX_TOKEN'] = new_access_token
                        dbx = dropbox.Dropbox(new_access_token)
                    dropbox_path = active_files[data['dkey']]
                    dbx.files_delete(dropbox_path)
                    return jsonify({'success': True}), 200
                except:
                    app.logger.exception(traceback.format_exc())
                    return jsonify({'success': False}), 400
            else:
                return jsonify({'success': False, 'error': 'Key Mismatch or File does not exist'}), 400
        else:
            return jsonify({'success': False, 'error': 'Data must be in json format'}), 400
    else:
        message = f'This is a {request.method} request on /download'
        return jsonify({'message': message})

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/download', methods=['HEAD','GET','POST'])
def downloading():
    app.logger.debug('Received request to /download with method: %s', request.method)
    if request.method == 'GET':
        return jsonify({'message': 'This is a GET request on /download'})
    elif request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            baseurl = 'https://api.fabdl.com/spotify/get?url='
            if 'track_id' in data:
                track_id = data.get('track_id')
                baseurl = 'https://api.fabdl.com/spotify/get?url=https://open.spotify.com/track/'
                try:
                    results = sp.track(track_id)
                    url = baseurl + track_id
                    audiobytes, filename = get_mp3(url)
                except:
                    logger.exception(traceback.format_exc())
                    return jsonify({'success': False, 'error': 'Song not found or invalid URL'}), 400
            else:
                track_name = data.get('name')
                try:
                    results = sp.search(q=track_name, type='track', limit=1)['tracks']['items'][0]
                except:
                    logger.exception(traceback.format_exc())
                    return jsonify({'success': False, 'error': 'Song not found'}), 400
                url = baseurl + results['id']
                audiobytes, filename = get_mp3(url)
            if not audiobytes:
                return jsonify({'success': False, 'error': 'Song not found'}), 400
            track_name = results['name']
            album_name = results['album']['name']
            release_date = results['album']['release_date']
            artists = [artist['name'] for artist in results['artists']]
            album_artists = [artist['name'] for artist in results['album']['artists']]
            genres = sp.artist(results['artists'][0]['id'])['genres']
            cover_art_url = results['album']['images'][0]['url']
            mdata = { 
                'track_name': track_name,
                'album_name': album_name,
                'release_date': release_date,
                'artists': artists,
                'album_artists': album_artists,
                'genres': genres,
                'cover_art_url': cover_art_url
            }
            filelike = BytesIO(audiobytes)
            merged_file = add_mdata(filelike, mdata)
            token = secrets.token_hex(12)
            try:
                dropbox_path = f"/songs/{filename}"
                file_url, direct_url = upload_file(merged_file, dropbox_path)
                active_files[token] = dropbox_path
                return jsonify({'success': True, 'url': direct_url, 'filename' : filename, 'dkey' : token}), 200
            except Exception as e:
                return jsonify({'success': False, 'error': traceback.format_exc()}), 400
        else:
            return render_template('home.html')
    else:
        return render_template('home.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443)
