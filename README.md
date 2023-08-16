# Spotify Playlist Downloader

This Python program allows you to download songs from a Spotify playlist and create a zip file containing those songs. It uses the Spotify API to fetch playlist tracks and yt-dlp to download corresponding audio files from YouTube.

# What's New in v1.2

We're excited to introduce several enhancements and improvements in version 1.2 of the Spotify Playlist Downloader!

### Faster Download with Threading

> In this update, we've introduced threading to speed up the download process. Now, multiple songs are downloaded simultaneously, resulting in a significantly faster overall download experience.

### Direct Download in .mp3 Format

> Previously, the program downloaded songs in the .webm format and then converted them to .mp3. This conversion step added unnecessary time. With v1.2, songs are now directly downloaded in the .mp3 format, eliminating the need for conversion and further improving the efficiency of the download process.

### Enhanced Console Logs

> We've revamped the program's console logs to be cleaner and more informative. You'll now get clearer progress updates and status messages, making it easier to track the download process and any potential errors.

### Improved Interactivity

> Version 1.2 introduces a more interactive experience. You can now simply enter the Spotify playlist URL and let the program handle the rest. The prompts and messages guide you through the process, making it even more user-friendly.

Stay tuned for more updates and features in future releases!

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
