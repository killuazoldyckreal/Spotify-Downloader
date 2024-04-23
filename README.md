# Spotify Playlist Downloader

This Python-based web application allows users to download songs from Spotify by providing a song URL or name query. It fetches songs from Spotify using API services, adds metadata to the songs, and delivers them in .mp3 format.

## What's New in v1.3

In version 1.3 of the Spotify Playlist Downloader, we've introduced several significant enhancements and features:

[Demo](https://spotifydownloader-killua.onrender.com)

### Web Page Setup 
> Implemented a web page interface for users to input Spotify song URLs or names for downloading.

### API Service Integration 
> Removed yt-dlp support and integrated other API services for fetching songs, ensuring a seamless download experience.

### Metadata Addition 
> Added metadata to downloaded songs before delivering the .mp3 files to users, enhancing the overall user experience.

### Security Enhancements 
> Implemented security features such as CSRF tokens and restricted request origins for improved security.

### Storage Cleanup 
> Implemented storage cleanup functionality to delete files after sending them to users, ensuring efficient use of storage resources.

### Environment Variables 
> Moved sensitive information such as API keys and tokens to a separate .env file for improved security and ease of configuration.

### Multiple API Setup 
> Configured two APIs to fetch songs, providing redundancy and ensuring robustness in case one API fails.

### Playlist Download Removal 
> Removed the playlist download feature along with threading, with plans to incorporate it in future releases.

## Requirements

- Python 3.x
- Flask
- Required Python libraries are listed in the `requirements.txt` file.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/spotify-downloader.git
   cd spotify-downloader
   ```

2. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

3. Obtain API credentials:
   - Create a Spotify Developer account and obtain your `CLIENT_ID` and `CLIENT_SECRET`.
   - Create a Dropbox Developer account and obtain your `DROPBOX_KEY`, `DROPBOX_TOKEN` and `DROPBOX_SECRET`.
   - Create Musixmatch Developer account and obtain your `Musixmatch API_KEY`.
   - Leave `MY_API_TOKEN` value empty, it's value will keep updating by itself.

4. Set up environment variables by creating a `.env` file in the project root directory and populating it with the following information:

   ```plaintext
   API_KEY="Musixmatch API KEY"
   CLIENT_ID="Spotify CLIENT_ID"
   CLIENT_SECRET="Spotify CLIENT_SECRET"
   DROPBOX_KEY="DROPBOX API KEY"
   DROPBOX_RTOKEN="DROPBOX API TOKEN"
   DROPBOX_SECRET="DROPBOX SECRET"
   MY_API_TOKEN="{'access_token': 'Spotify token', 'token_type': 'Bearer', 'expires_in': 3600, 'expires_at': 1705400098}"
   FLASK_DEBUG=True
   ```

5. Run the Flask server:

   ```bash
   python app.py
   ```

## Usage

1. Navigate to the web page and enter the Spotify song URL or name in the provided input field. 
2. Click the "Download" button to initiate the download process.
3. Once the song is downloaded, it will be delivered in .mp3 format with metadata added.

## Acknowledgments

This program uses the following APIs and libraries:
### APIs
- [Spotipy](https://spotipy.readthedocs.io/): Spotify Web API client.
- [Musixmatch](https://developer.musixmatch.com/documentation): Musixmatch API.
- [Dropbox](https://dropbox.github.io/dropbox-api-v2-explorer): Dropbox API.
### Libraries
Flask, Spotipy

## Disclaimer

This application is intended for educational and personal use only. Respect copyright and intellectual property rights when downloading and using content from Spotify.

## License

This project is licensed under the [MIT License](LICENSE).
