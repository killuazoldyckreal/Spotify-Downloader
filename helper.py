from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TPE2, USLT
from PIL import Image
from io import BytesIO
import requests
from pydub import AudioSegment
import os, re
from urllib.parse import urlparse

api_key=os.environ["API_KEY"]
def estimate_conversion_time(input_file):
    audio = AudioSegment.from_file(input_file)
    duration_seconds = len(audio) / 1000.0
    average_conversion_speed = 5.3
    estimated_conversion_time = duration_seconds / average_conversion_speed
    return estimated_conversion_time
    
def is_valid_spotify_url(url):
    """
    Verify if the given URL is a valid Spotify track URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.scheme in ['http', 'https'] and 'open.spotify.com' in parsed_url.netloc

def parse_bytes(byte_str):
    units = {"B": 1, "KiB": 1024, "MiB": 1024 ** 2, "GiB": 1024 ** 3, "TiB": 1024 ** 4}
    try:
        value, unit = re.match(r"([\d.]+)\s*([a-zA-Z]+)", byte_str).groups()
        return float(value) * units[unit]
    except:
        return 0.0, "unknown"

def get_song_metadata(track_info, sp):
    track_name = track_info['name']
    album_name = track_info['album']['name']
    release_date = track_info['album']['release_date']
    artists = [artist['name'] for artist in track_info['artists']]
    song_title = (str(track_info['name']) +' ' +str(artists[0]) +' ' +str(track_info['album']['release_date']))
    album_artists = [artist['name'] for artist in track_info['album']['artists']]
    genres = sp.artist(track_info['artists'][0]['id'])['genres']
    cover_art_url = track_info['album']['images'][0]['url']
    if "'" in song_title:
        song_title = song_title.replace("'", "")
    elif '"' in song_title:
        song_title = song_title.replace('"', "")

    data = {
        'search_query': song_title, 
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

class MDATA:
    def __init__(self, path, data) -> None:
        self.path = path
        self.metadata = data


    def export_mp3_with_metadata(self, output_file):
        metadata = self.metadata
        track_id = search_track(metadata['track_name'], metadata['artists'][0])
        tags = ID3(output_file)
        tags['TIT2'] = TIT2(encoding=3, text=metadata['track_name'])
        tags['TPE1'] = TPE1(encoding=3, text=metadata['artists'])
        tags['TALB'] = TALB(encoding=3, text=metadata['album_name'])
        tags['TDRC'] = TDRC(encoding=3, text=metadata['release_date'])
        tags['TCON'] = TCON(encoding=3, text=metadata['genres'])
        if track_id:
            lyrics = get_lyrics(track_id)
            if lyrics:
                tags['USLT'] = USLT(encoding=3, lang='eng', text=lyrics)
        if 'album_artists' in metadata:
            tags['TPE2'] = TPE2(encoding=3, text=metadata['album_artists'])
        if 'cover_art_url' in metadata:
            cover_url = metadata['cover_art_url']
            with open("cover.jpg", "wb") as f:
                f.write(requests.get(cover_url).content)
            tags['APIC'] = APIC(encoding=0, mime='image/jpeg', type=3, desc=u'Cover', data=open('cover.jpg', 'rb').read())

        tags.save(output_file)
        return True

    def convert_to_mp3(self):
        output_file = str(self.path).rsplit('.',1)[0]+'.mp3'
        audio = AudioSegment.from_file(self.path)
        audio.export(output_file, format="mp3")
        self.export_mp3_with_metadata(output_file)
        os.remove(self.path)
        return output_file

    def batch_convert_to_mp3(self, input_folder, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        supported_formats = [".m4a", ".aac", ".ogg", ".opus", ".webm"]

        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith(tuple(supported_formats)):
                    input_path = os.path.join(root, file)
                    output_file = os.path.splitext(file)[0] + ".mp3"
                    output_path = os.path.join(output_folder, output_file)

                    print(f"Converting {input_path} to {output_path}")
                    self.convert_to_mp3(input_path, output_path)

    def show_art(self):
        for k, v in self.audio.items():
            if "APIC" in k:
                image = Image.open(BytesIO(v.data))
                image.show()
                return
        else:
            print("No embedded cover art found.")