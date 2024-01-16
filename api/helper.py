from eyed3.id3.frames import ImageFrame
from PIL import Image
from io import BytesIO
import requests
import os, tempfile
from urllib.parse import urlparse
import eyed3

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

    def add_cover_art(self, audio_bytesio):
        metadata = self.metadata
        audio_bytesio.seek(0)  # Move the cursor to the beginning of the BytesIO object

        # Save the BytesIO content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
            temp_audio_file.write(audio_bytesio.read())
            temp_audio_file_path = temp_audio_file.name

        # Use eyed3.load to load the temporary audio file
        audiofile = eyed3.load(str(temp_audio_file_path))
        audiofile.tag.frame_set = []  # Clear existing frames

        if 'cover_art_url' in metadata:
            cover_url = metadata['cover_art_url']
            cover_data = requests.get(cover_url).content

            # You may want to resize the image to a reasonable size
            cover_image = Image.open(BytesIO(cover_data))
            cover_image.thumbnail((300, 300))

            # Create an ImageFrame with the cover image data
            cover_frame = ImageFrame(
                type=ImageFrame.FRONT_COVER,
                mime='image/jpeg',
                image_data=cover_image.tobytes()
            )

            # Add the ImageFrame to the audio file
            audiofile.tag.frame_set.append(cover_frame)

        # Save the modified audio file to a new BytesIO object
        output_bytesio = BytesIO()
        audiofile.tag.save(output_bytesio)

        # Remove the temporary audio file
        os.remove(temp_audio_file_path)

        return output_bytesio

