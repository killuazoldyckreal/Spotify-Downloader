import os, asyncio, shutil
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from flask import Flask
import traceback
from threading import Thread
import logging
from spotipy.cache_handler import CacheHandler

logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)
app = Flask(__name__)

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

def is_song_already_downloaded(song_title):
    song_filename = f'songs/{song_title}.mp3'
    return os.path.exists(song_filename)
    
async def download_spotify_playlist(playlist_url):
    try:
        playlist_id = playlist_url.replace("https://open.spotify.com/playlist/", "").split("?")[0]
        cache_path = ".spotify_cache"
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"], cache_handler=CustomCacheHandler(cache_path)))
        results = sp.playlist_tracks(playlist_id)
    
        for item in results['items']:
            try:
                _id = item['track']['id']
                track_info = sp.track(_id)
                artist_name = track_info["artists"][0]["name"]
                song_name = track_info["name"]
                song_title = f"{artist_name} - {song_name}"
                if "'" in song_title:
                    song_title = song_title.replace("'", "")
                elif '"' in song_title:
                    song_title = song_title.replace('"', "")
            
                search_query = f'ytsearch:"{song_title}"'
                if not is_song_already_downloaded(song_title):
                    await download_youtube_video(search_query, song_title)
                else:
                    print(f"Skipping '{song_title}' - Already downloaded")
            
            
            except Exception as e:
                print(f"Error: {e}")
                continue
    except:
        traceback.print_exc()

async def download_youtube_video(query, song_title):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': f'songs/{song_title}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        
    except:
        traceback.print_exc()

@app.route('/')
def home():
    return "Welcome to Spotify Playlist Downloader!"

def run():
    app.run(host='0.0.0.0',port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
    
async def main():
    keep_alive()
    await asyncio.sleep(2)
    print("=======================================")
    print("Welcome to Spotify Playlist Downloader!")
    print("=======================================")
    playlist_url = input("Enter the Spotify playlist URL: ")
        
    if not os.path.exists('songs'):
        os.makedirs('songs')
    
    await download_spotify_playlist(playlist_url)
    print("Download completed!\nCreating zip file...")
    shutil.make_archive('songs', 'zip', 'songs')
    print("Zip file created and removing songs folder...")
    shutil.rmtree('songs')      
    print("Process completed!")

if __name__ == "__main__":
    asyncio.run(main())
