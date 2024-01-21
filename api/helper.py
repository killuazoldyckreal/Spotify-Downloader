from mutagen.id3 import ID3, APIC
from PIL import Image
from io import BytesIO
import requests
import os
from urllib.parse import urlparse
from spotipy.cache_handler import CacheHandler
import dropbox

api_key=os.environ.get('API_KEY')
ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')

class CustomCacheHandler(CacheHandler):
    def __init__(self):
        self.cache_path = None

    def get_cached_token(self):
        cached_token = os.environ.get('MY_API_TOKEN')
        return eval(cached_token) if cached_token else None

    def save_token_to_cache(self, token_info):
        os.environ['MY_API_TOKEN'] = str(token_info)

def is_valid_spotify_url(url):
    """
    Verify if the given URL is a valid Spotify track URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https'] and 'open.spotify.com' in parsed_url.netloc

def get_song_metadata(track_info, sp):
    track_name = track_info['name']
    album_name = track_info['album']['name']
    release_date = track_info['album']['release_date']
    artists = [artist['name'] for artist in track_info['artists']]
    album_artists = [artist['name'] for artist in track_info['album']['artists']]
    genres = sp.artist(track_info['artists'][0]['id'])['genres']
    cover_art_url = track_info['album']['images'][0]['url']
    data = {
        'track_name': track_name,
        'album_name': album_name,
        'release_date': release_date,
        'artists': artists,
        'album_artists': album_artists,
        'genres': genres,
        'cover_art_url': cover_art_url
    }
    return data

def search_track(track_name, artist_name):
    base_url = "https://api.musixmatch.com/ws/1.1/"
    endpoint = "track.search"

    params = {
        "q_track": track_name,
        "q_artist": artist_name,
        "apikey": api_key,
    }

    response = requests.get(base_url + endpoint, params=params)
    data = response.json()

    if response.status_code == 200:
        track_list = data["message"]["body"]["track_list"]
        if track_list:
            track_id = track_list[0]["track"]["track_id"]
            return track_id
        else:
            return None
    else:
        return None

def get_lyrics(track_id):
    base_url = "https://api.musixmatch.com/ws/1.1/"
    endpoint = "track.lyrics.get"

    params = {
        "track_id": track_id,
        "apikey": api_key,
    }

    response = requests.get(base_url + endpoint, params=params)
    data = response.json()

    if response.status_code == 200:
        if data["message"]["body"]!=[]:
            lyrics = data["message"]["body"]["lyrics"]["lyrics_body"]
            return lyrics
        return None
    else:
        return None

def add_cover_art(audio_file, cover_art_url):
    audio_file.seek(0)
    tags = ID3()
    cover_image_data = BytesIO(requests.get(cover_art_url).content)
    tags['APIC'] = APIC(
        encoding=0,
        mime='image/jpeg',
        type=3,
        desc=u'Cover',
        data=cover_image_data.getvalue()
    )
    tags.save(audio_file)
    audio_file.seek(0)
    return audio_file

def upload_file(f, dropbox_path):
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    response = dbx.files_upload(f.read(), dropbox_path, autorename=True)
    shared_link_metadata = dbx.sharing_create_shared_link(path=response.path_display)
    direct_link = shared_link_metadata.url.replace('&dl=0', '&dl=1')
    direct_link2 = direct_link.replace('https://www.dropbox.com', 'https://dl.dropboxusercontent.com')
    return direct_link, direct_link2

def get_mp3(url):
    try:
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en;q=0.7',
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
    except:
        return None, None