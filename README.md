# Spotify Playlist Downloader with Zip Archive

This program allows you to download audio tracks from a Spotify playlist, save them as MP3 files, and create a zip archive of the downloaded songs. It utilizes the Spotify Web API and yt-dlp (YouTube-DL compatible). Follow the steps below to use the program successfully.

## Prerequisites

Before you begin, make sure you have the following requirements in place:

- Python 3.7 or later installed on your system.
- Spotify Developer Account: You need to create a Spotify Developer account and obtain your `CLIENT_ID` and `CLIENT_SECRET`.
- yt-dlp: Make sure you have yt-dlp installed. You can install it using `pip`:

  ```bash
  pip install yt-dlp
  ```

## Installation

1. Clone this repository to your local machine or download the files.

2. Install the required Python packages:

   ```bash
   pip install spotipy flask
   ```

## Setup

1. Set your Spotify `CLIENT_ID` and `CLIENT_SECRET` environment variables:

   ```bash
   export CLIENT_ID='your_client_id'
   export CLIENT_SECRET='your_client_secret'
   ```

2. Create a cache directory for Spotify tokens:

   ```bash
   mkdir .spotify_cache
   ```

3. Install FFmpeg: Make sure FFmpeg is installed on your system. You can download it from the official website: [FFmpeg](https://ffmpeg.org/download.html).

## Usage

1. Run the program:

   ```bash
   python spotify_playlist_downloader.py
   ```

2. Open a web browser and navigate to `http://localhost:8080/` to keep the server alive.

3. Enter the Spotify playlist URL when prompted.

4. The program will start downloading the audio tracks from the playlist and saving them as MP3 files in the `songs` directory.

5. Once the download is completed, the program will create a zip archive of the downloaded songs and remove the `songs` directory.

6. You will see the message "Process completed!".

## Notes

- The downloaded MP3 files will be saved in the `songs` directory, and the zip archive will be named `songs.zip`.
- If a song is already downloaded, the program will skip it and display a message.
- Make sure to comply with Spotify's terms of use and only download content that you have the right to access.

## Disclaimer

This program is intended for educational and personal use only. The developers of this program are not responsible for any unauthorized or illegal use of the downloaded content. Please ensure you have the right to access and download the content before using this program.
