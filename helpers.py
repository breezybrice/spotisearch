from flask import redirect
import webbrowser
import requests
import json

# open browser at address where app is running locally
def open_browser():
    try:
        url = 'http://127.0.0.1:5000/'
        webbrowser.open(url)
    except Exception:
        print('You need to manually open your browser and navigate to: http://127.0.0.1:5000/')

# store track_uris in a dictionary
def store_track_uris(track_uris):
    uri_dict = {'uris': track_uris}
    with open('track_uris.json', 'w') as outfile:
        json.dump(uri_dict, outfile)

# retrieve track_uris
def get_track_uris():
    with open('track_uris.json', 'r') as openfile:
        uri_dict = json.load(openfile)
    return uri_dict

# post request to add tracks to playlist
def add_tracks(tokens, playlist_id, tracks_list):
    uri = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {tokens["access_token"]}', 'Content-Type': 'application/json'}
    payload = {'uris': tracks_list}
    r = requests.post(uri, headers=headers, data=json.dumps(payload))
