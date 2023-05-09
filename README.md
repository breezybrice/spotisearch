# Spotisearch

Spotisearch is a web application that allows users to retrieve information about tracks in a Spotify playlist. Users simply need to enter the playlist ID of the playlist they wish to analyze, and the app will return details about each track in the playlist, including its name, artist, album, key and much more.

## Installation

To install Spotisearch, you'll need to take the following steps:

1. Clone the repository to your local machine using `git clone https://github.com/breezybrice/spotisearch.git`.
2. Install the necessary dependencies by running `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory of the project, and add your Spotify API credentials to it in the following format:

```
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_USER_ID=
SPOTIFY_REDIRECT_URI='http://127.0.0.1:5000/callback'
```
* an .env example file is included for your convenience

4. Start the server by running `app.py`, and navigate to `http://localhost:5000` in your web browser to use the app.

## Roadmap

Here are some features that we're planning to add in future releases of Spotisearch:

- Search for Artists.
- Get Album Info.
- Get Artist info.
- Option to export track data as a CSV file.



We hope you find Spotisearch useful, and we welcome any feedback or contributions to the project!
