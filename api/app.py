from gevent import monkey
monkey.patch_all()
from flask import Flask, request, render_template, send_file, redirect, jsonify, after_this_request, send_from_directory
from flask_socketio import SocketIO
import logging, os, yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from api.chandler import CustomCacheHandler
from api.helper import MDATA, is_valid_spotify_url, get_song_metadata, estimate_conversion_time
import traceback
import glob
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from flask_compress import Compress
from geventwebsocket.handler import WebSocketHandler


logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)
app = Flask(__name__)
CORS(app, supports_credentials=True)

compress = Compress()
compress.init_app(app)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, secure=True, cors_allowed_origins="*", async_mode='gevent')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

cache_path = "api/.spotify_cache"

if not os.path.exists(cache_path):
    os.makedirs(cache_path)
client_id=os.environ.get('CLIENT_ID')
client_secret=os.environ.get('CLIENT_SECRET')
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret, cache_handler=CustomCacheHandler(cache_path)))

@app.route('/.well-known/pki-validation/<filename>')
def verification_file(filename):
    return send_from_directory('verification', filename)

@app.route('/')
def home():
    if 'urlInput' in request.args:
        url = request.args['urlInput']
        if url=="":
            return jsonify({'success': False, 'error': 'Song field cannot be empty'}), 400
        if is_valid_spotify_url(url):
            if "track" in url:
                track_id = url.replace("https://open.spotify.com/track/","").split("?")[0]
                try:
                    item = {"track" : sp.track(track_id)}
                    _id = item['track']['id']
                    track_info = sp.track(_id)
                    song_title = track_info['name']
                    data = get_song_metadata(track_info, sp)
                    path = get_mp3(data,"sp")
                except:
                    traceback.print_exc()
                    return jsonify({'success': False, 'error': 'Song not found or invalid URL'}), 400
        else:
            if "https://" not in url:
                song_title = url
                try:
                    try:
                        results = sp.search(q=song_title, type='track', limit=1)['tracks']['items'][0]
                    except:
                        socketio.emit('error_', {'error': 'Song not found'})
                        return jsonify({'success': False, 'error': 'Song not found'}), 400
                    data = get_song_metadata(results, sp)
                    song_title = data['track_name']
                    path = get_mp3(data,"sp")
                except:
                    return jsonify({'success': False, 'error': 'Song not found'}), 400

        try:
            file_handle = open(path, 'r')
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(path)
                    file_handle.close()
                except Exception as error:
                    app.logger.error("Error removing or closing downloaded file handle", error)
                return response
            socketio.emit('converted', {'status':'finished'})
            return send_file(path, download_name = song_title + '.mp3', as_attachment=True, mimetype='audio/mpeg'), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    else:
        return render_template('home.html', async_mode=socketio.async_mode)

def progress_hook(d):
    if d['status'] == 'downloading':
        socketio.emit('progress', {'downloaded_bytes': d['downloaded_bytes'], 'total_bytes': d['total_bytes']})
    if d['status'] == 'finished':
        socketio.emit('finished', {'status':'finished'})

def get_mp3(data, query):
    squery = data['search_query']
    song_title = data['track_name']
    ydl_opts = {
        'quiet': True,
        'extract_audio': True,
        'format': '251/140/ba',
        'outtmpl': f'static/songs/{song_title}.%(ext)s',
        'external_downloader_args': ['-loglevel', 'panic'],
        'progress_hooks': [progress_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if query=="sp":
            ydl.download([f'ytsearch:"{squery} song"'])
    input_file = glob.glob(f'static/songs/{song_title}*')[0]
    fileext = input_file.split('.',-1)[1]
    convertor = MDATA(input_file, data)
    if fileext!= 'mp3' or fileext!= 'MP3':
        for file in glob.glob(f'static/songs/{song_title}*'):
            fileext = input_file.split('.',-1)[1]
            if fileext== 'mp3':
                convertor.export_mp3_with_metadata(input_file)
                return input_file
        eta = estimate_conversion_time(input_file)
        socketio.emit('conversion', {'eta':eta})
        convertor.convert_to_mp3()
        return f'static/songs/{song_title}.mp3'
    else:
        convertor.export_mp3_with_metadata(input_file)
        return input_file

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
    http_server = WSGIServer(('0.0.0.0'), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
