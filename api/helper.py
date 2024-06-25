from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TPE2, USLT
from PIL import Image
from io import BytesIO
import requests
import os, secrets
from urllib.parse import urlparse
from spotipy.cache_handler import CacheHandler
import dropbox
from dotenv import load_dotenv
import logging
import sys, traceback
import time, re
from bs4 import BeautifulSoup

load_dotenv()
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    stream=sys.stdout,
                    datefmt='%Y-%m-%d %H:%M:%S')

api_key = os.getenv("API_KEY")
ACCESS_KEY = os.getenv("DROPBOX_KEY")
ACCESS_SECRET = os.getenv("DROPBOX_SECRET")
ACCESS_TOKEN = os.getenv("DROPBOX_RTOKEN")

def getid(url):
    """
    Extract the video ID from the YouTube URL.
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube\.com/watch\?v=|youtu\.be/)'
        '([a-zA-Z0-9_-]{11})'
    )
    match = re.match(youtube_regex, url)
    if match:
        return match.group(4)
    else:
        return None

class RequestHandler:
    def __init__(self, base_url):
        self.url = base_url

    def post(self, endpoint, reqdata, query, headers=None):
        url = self.url+endpoint
        if "yt" in query:
            response = requests.post(url, headers=headers, json=reqdata)
        else:
            response = requests.post(url, headers=headers, data=reqdata)
        if response.status_code==200:
            try:
                if query=="yta":
                    data = response.json()
                    title = data['title']
                    duration = data["lengthSeconds"]
                    datadict = {"title": title, "duration": duration}
                    for task in data["tasks"]:
                        quality = task["bitrate"]
                        audio_size = task["filesize"]
                        audio_hash = task["hash"]
                        datadict[quality] = {"size": audio_size, "audio_hash": audio_hash}
                    return datadict
                elif query=="yt2":
                    data = response.json()
                    return data["taskId"]
                elif query=="yt3":
                    data = response.json()
                    while data["status"]!="finished":
                        time.sleep(2.5)
                        response = requests.post(url, headers=headers, data=reqdata)
                        data = response.json()
                    return data["download"]
            except:
                logging.error(traceback.format_exc())
        return None

class YoutubeDownloader:
    def __init__(self, url):
        self.url = url
        self.handler = RequestHandler("https://master-cdn.dl-api.com/api/json")
        self.headers = {
            "Origin": "https://yt.yt1sapi.com",
            "Referer": "https://yt.yt1sapi.com/"
        }
        
    def downloadAudio(self, output_path=".", reqQuality:int=192):
        try:
            units = {"KB": 1, "MB": 1024, "GB": 1024**2}
            reqdata = {"ftype":"mp3","url":self.url}
            response = self.handler.post("/", reqdata, "yta", self.headers)
            if response:
                title = response["title"]
                filesize = response[reqQuality]["size"]
                size, unit = filesize.split()
                size = float(size)
                size_in_mb = size * units[unit]
                if size_in_mb < 50:
                    reqdata2 = {"hash":response[reqQuality]["audio_hash"]}
                    taskID = self.handler.post("/", reqdata2, "yt2", self.headers)
                    if taskID:
                        reqdata3 = {"taskId":taskID}
                        download_url = self.handler.post("/task", reqdata3, "yt3", self.headers)
                        response = requests.get(downloadurl)
                        audiobytes = response.content
                        return audiobytes, title
        except:
            logging.error(traceback.format_exc())
        return None, None

class ValidationError(ValueError):
    """
    Raised when a validator fails to validate its input.
    """

    def __init__(self, message="", *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)


class CustomCacheHandler(CacheHandler):
    def __init__(self):
        self.cache_path = None

    def get_cached_token(self):
        cached_token = os.environ.get("MY_API_TOKEN")
        return eval(cached_token) if cached_token else None

    def save_token_to_cache(self, token_info):
        os.environ["MY_API_TOKEN"] = str(token_info)


def is_valid_spotify_url(url):
    """
    Verify if the given URL is a valid Spotify track URL.
    """
    parsed_url = urlparse(url)
    return (
        parsed_url.scheme in ["http", "https"]
        and "open.spotify.com" in parsed_url.netloc
    )


def get_song_metadata(track_info, sp):
    track_name = track_info["name"]
    album_name = track_info["album"]["name"]
    release_date = track_info["album"]["release_date"]
    artists = [artist["name"] for artist in track_info["artists"]]
    album_artists = [artist["name"] for artist in track_info["album"]["artists"]]
    genres = sp.artist(track_info["artists"][0]["id"])["genres"]
    cover_art_url = track_info["album"]["images"][0]["url"]
    data = {
        "track_name": track_name,
        "album_name": album_name,
        "release_date": release_date,
        "artists": artists,
        "album_artists": album_artists,
        "genres": genres,
        "cover_art_url": cover_art_url,
    }
    return data


def search_track(track_name, artist_name):
    try:
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
    except Exception as e:
        logging.error(traceback.format_exc())
        return None


def get_lyrics(track_id):
    try:
        base_url = "https://api.musixmatch.com/ws/1.1/"
        endpoint = "track.lyrics.get"

        params = {
            "track_id": track_id,
            "apikey": api_key,
        }

        response = requests.get(base_url + endpoint, params=params)
        data = response.json()

        if response.status_code == 200:
            if data["message"]["body"] != []:
                lyrics = data["message"]["body"]["lyrics"]["lyrics_body"]
                return lyrics
            return None
        else:
            return None
    except Exception as e:
        logging.error(traceback.format_exc())
        return None


def add_mdata(audio_file, metadata):
    try:
        audio_file.seek(0)
        tags = ID3()
        cover_image_data = BytesIO(requests.get(metadata["cover_art_url"]).content)
        tags["TIT2"] = TIT2(encoding=3, text=metadata["track_name"])
        tags["TPE1"] = TPE1(encoding=3, text=metadata["artists"])
        tags["TALB"] = TALB(encoding=3, text=metadata["album_name"])
        tags["TDRC"] = TDRC(encoding=3, text=metadata["release_date"])
        tags["TCON"] = TCON(encoding=3, text=metadata["genres"])
        if "album_artists" in metadata:
            tags["TPE2"] = TPE2(encoding=3, text=metadata["album_artists"])
        tags["APIC"] = APIC(
            encoding=0,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=cover_image_data.getvalue(),
        )
        tags.save(audio_file)
        audio_file.seek(0)
        return audio_file
    except Exception as e:
        logging.error(traceback.format_exc())
        return None


def format_duration(milliseconds):
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    formatted_duration = ""
    if hours > 0:
        formatted_duration += f"{hours}h "
    if minutes > 0:
        formatted_duration += f"{minutes}m "
    formatted_duration += f"{seconds}s"

    return formatted_duration.strip()


def upload_file(f, dropbox_path):
    try:
        dbx = dropbox.Dropbox(
            app_key=ACCESS_KEY,
            app_secret=ACCESS_SECRET,
            oauth2_refresh_token=ACCESS_TOKEN,
        )
        response = dbx.files_upload(f.read(), dropbox_path, autorename=True)
        time.sleep(1.0)
        shared_link_metadata = dbx.sharing_create_shared_link(
            path=response.path_display
        )
        direct_link = shared_link_metadata.url.replace("&dl=0", "&dl=1")
        direct_link2 = direct_link.replace(
            "https://www.dropbox.com", "https://dl.dropboxusercontent.com"
        )
        return direct_link, direct_link2
    except dropbox.exceptions.ApiError:
        pass
    except Exception as e:
        logging.error(traceback.format_exc())


def delete_file(dropbox_path):
    try:
        dbx = dropbox.Dropbox(
            app_key=ACCESS_KEY,
            app_secret=ACCESS_SECRET,
            oauth2_refresh_token=ACCESS_TOKEN,
        )
        dbx.files_delete(dropbox_path)
    except Exception as e:
        logging.error(traceback.format_exc())
    return


def get_mp3(url):
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            gid = data["result"]["gid"]
            tid = data["result"]["id"]
            filename = data["result"]["name"] + ".mp3"
            url2 = f"https://api.fabdl.com/spotify/mp3-convert-task/{gid}/{tid}"
            response2 = requests.get(url2)
            if response2.ok:
                data2 = response2.json()
                statusid = data2["result"]["status"]
                if statusid != 3:
                    headers = {
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip",
                        "Referer": "https://spotifydown.com/",
                        "Origin": "https://spotifydown.com",
                    }
                    baseurl = "https://api.spotifydown.com/download/" + tid
                    response3 = requests.get(baseurl, headers=headers)
                    if response3.ok:
                        try:
                            data = response3.json()
                        except requests.exceptions.JSONDecodeError:
                            return None, None
                        if data["success"]:
                            download_url = data["link"]
                            response4 = requests.get(download_url)
                            if response4.ok:
                                audiobytes = response4.content
                                return audiobytes, filename
                    return None, None
                download_url = "https://api.fabdl.com" + data2["result"]["download_url"]
                response3 = requests.get(download_url)
                if response3.ok:
                    audiobytes = response3.content
                    return audiobytes, filename
                else:
                    return None, None
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        logging.error(traceback.format_exc())
        return None, None
