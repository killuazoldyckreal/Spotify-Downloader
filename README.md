# Spotify Playlist Downloader

This Python program allows you to download songs from a Spotify playlist and create a zip file containing those songs. It uses the Spotify API to fetch playlist tracks and yt-dlp to download corresponding audio files from YouTube.

## Requirements

- Python 3.x
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

3. Obtain Spotify API credentials:
   - Create a Spotify Developer account and obtain your `CLIENT_ID` and `CLIENT_SECRET`.

4. Set environment variables:
   ```bash
   export CLIENT_ID=your_spotify_client_id
   export CLIENT_SECRET=your_spotify_client_secret
   ```

5. Run the program:

   ```bash
   python main.py
   ```

## Usage

1. Enter the Spotify playlist URL and follow the prompts.

2. The program will download the songs from the playlist and create a zip file.

## Acknowledgments

This program uses the following libraries:
- [Spotipy](https://spotipy.readthedocs.io/): Spotify Web API client.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp): YouTube downloader with additional features.

## Disclaimer

This program is intended for educational and personal use only. Please respect copyright and intellectual property rights when downloading and using content from Spotify and YouTube.

## License

This project is licensed under the [MIT License](LICENSE).
