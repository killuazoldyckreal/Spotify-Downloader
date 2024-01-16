from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TPE2, USLT
from PIL import Image
from io import BytesIO
import requests
#from pydub import AudioSegment
import os, re, ffmpeg
from urllib.parse import urlparse

api_key=os.environ.get('API_KEY')
    
def is_valid_spotify_url(url):
    """
    Verify if the given URL is a valid Spotify track URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https'] and 'open.spotify.com' in parsed_url.netloc

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

class MDATA:
    def __init__(self, path, data) -> None:
        self.path = path
        self.metadata = data

    def add_cover_art(self, output_file):
        metadata = self.metadata
        tags = ID3(output_file)
        if 'cover_art_url' in metadata:
            cover_url = metadata['cover_art_url']
            with open("cover.jpg", "wb") as f:
                f.write(requests.get(cover_url).content)
            tags['APIC'] = APIC(encoding=0, mime='image/jpeg', type=3, desc=u'Cover', data=open('cover.jpg', 'rb').read())
        tags.save(output_file)
        return True

