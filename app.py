from flask import Flask, redirect, request, render_template, url_for, session
from dotenv import load_dotenv
from spotify_client import SpotifyAPI
import helpers as hp
import numpy as np
import requests
import json
import os

# Authentication Process. Uses authhelp.py and .env file

load_dotenv() #load env variables from the .env file
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
USER_ID = os.getenv('SPOTIFY_USER_ID')

SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
MY_FOLLOWED_ARTISTS_URL = 'https://api.spotify.com/v1/me/following?type=artist'
GET_ARTISTS_ALBUMS = 'https://api.spotify.com/v1/artists/{id}/albums'



app = Flask(__name__)

@app.route('/')
def login():
    return render_template('index.html')

@app.route('/auth')
def request_auth():
    # Authorizes the User by logging in. Asks user to authorize access to the defines scopes.
    # After accepting the request, user is redirected to REDIRECT_URI callback and given
    # two query parameters: (auth) code and state. Can be found in callback URL directly.
    url = 'https://accounts.spotify.com/authorize'
    scope = 'user-top-read playlist-modify-public playlist-modify-private user-follow-read'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': 'state',
        'scope': scope
    }
    r = requests.get(url, params=params)
    return redirect(r.url)
    # return redirect(f'https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={scope}&redirect_uri={REDIRECT_URI}')

@app.route('/callback')
def callback():
    # The REDIRECT_URI callback. Given two query parameters: (auth) 'code' and state. 
    # Can be found in callback URL directly.
    
    if request.args.get('error'):
        error_msg = request.args.get('error')
        raise ValueError(error_msg)
    
    code = request.args.get('code') # Retrieves 'code' from parsed URL parameters in callback URL
    
    return render_template('loading.html', code=code)

################### Create Functions with Authorized Client Object ####################


# Take Code from Callback. Input into Client. Client requests API Access Tokens


# Search passthru for form input text
@app.route('/search/<code>', methods=['GET', 'POST'])
def search(code):
    code = code
    search=request.form.get('search')
    playlist=request.form.get('playlist')

    if search is not None:
        return redirect(url_for('fetch_data', code=code, search=search))
    elif playlist is not None:
        return redirect(url_for('playlist_tracks', code=code, playlist=playlist))
    
# Route for artist search. Saves artist name and id to JSON file
@app.route('/fetch_data/<code>/<search>')
def fetch_data(code, search):
    
    code=code

    client = SpotifyAPI(
        CLIENT_ID, 
        CLIENT_SECRET, 
        REDIRECT_URI
    )
    client.get_token_data(code)

    client.perform_auth(code)
    client.get_access_token()
    artistSearch = client.search(search)
    
    artist_name = artistSearch['artists']['items'][0]['name']
    artist_id = artistSearch['artists']['items'][0]['id']


    # Load existing artist_dict from the JSON file
    with open('artist_info.json', 'r') as infile:
        artist_dict = json.load(infile)

    # Add a new key-value pair to the dictionary, checking for duplicates
    if artist_name not in artist_dict:
        artist_dict[artist_name] = artist_id

    # Write the updated dictionary back to the JSON file
    with open('artist_info.json', 'w') as outfile:
        json.dump(artist_dict, outfile)

    return artist_dict

# Returns track information from a specified playlist id
@app.route('/playlist_tracks/<code>/<playlist>')
def playlist_tracks(code, playlist):
    
    code=code

    client = SpotifyAPI(
        CLIENT_ID, 
        CLIENT_SECRET, 
        REDIRECT_URI
    )
    client.get_token_data(code)

    client.perform_auth(code)
    client.get_access_token()
    playlistItems = client.get_playlist_items(playlist)
    


    # create a list to store the track data
    tracks = []

    # iterate through each item and extract the track data
    #for item in playlistItems['items']:
    for item in playlistItems:
        track_name = item['track']['name']
        track_id = item['track']['id']
        artist_name = item['track']['album']['artists'][0]['name']
        artist_id = item['track']['album']['artists'][0]['id']
        album_name = item['track']['album']['name']
        album_id = item['track']['album']['id']


        audioFeatures = client.track_audio_features(track_id)
        key = audioFeatures['key']
        mode = audioFeatures['mode']
        tempo = audioFeatures['tempo']
        valence = audioFeatures['valence']
        danceability = audioFeatures['danceability']
        energy = audioFeatures['energy']
        instrumentalness = audioFeatures['instrumentalness']

        # add the track data to the list
        tracks.append({
            'track_name': track_name,
            'track_id': track_id,
            'artist_name': artist_name,
            'artist_id': artist_id,
            'album_name': album_name,
            'album_id': album_id,
            'key': key,
            'mode': mode,
            'tempo': tempo,
            'valence': valence,
            'danceability': danceability,
            'energy': energy,
            'instrumentalness': instrumentalness
        })


        #This loop removes quotes in the dictionary values of the tracks list, which resolves 
        # an error of values not showing up in the HTML table
        for item in tracks:
            for key, value in item.items():
                if isinstance(value, str):
                    item[key] = value.replace('"', '')


    # Spotify gives the key of the song in pitch class notation
    # This loop replaces the song's pitch number with key note letter
    pitch_class = {
        0: 'C', 1: 'C#/Db', 2: 'D', 3: 'D#/Eb', 4: 'E', 5: 'F', 
        6: 'F#/Gb', 7: 'G', 8: 'G#/Ab', 9: 'A', 10: 'A#/Bb', 11: 'B'
    }
    
    for item in tracks:
        key_value = item['key']  #Number value of key 
        note_value = pitch_class[key_value]  
        item['key'] = str(note_value)



    # Spotify gives the modes as integers. This loop replaces 
    # the int value with its string      
    modes = {
        0: 'Major',
        1: 'Minor'
    }

    for item in tracks:
        mode_value = item['mode']   
        mode_str = modes[mode_value]
        item['mode'] = mode_str
    

    #return tracks    
    return render_template('playlist_tracks.html', tracks=tracks)


############## Future Features ##############
"""

# Returns artists albums using artist id
@app.route('/get_artist_albums/<code>')
def get_artist_albums(code):

    code=code

    client = SpotifyAPI(
        CLIENT_ID, 
        CLIENT_SECRET, 
        REDIRECT_URI
    )
    client.get_token_data(code)

    client.perform_auth(code)
    client.get_access_token()
    album = client.get_artist_albums('album id')
    
    return album

# Returns album info using album id
@app.route('/get_album/<code>')
def get_album(code):
    client = SpotifyAPI(
        CLIENT_ID, 
        CLIENT_SECRET, 
        REDIRECT_URI
    )
    client.get_token_data(code)

    client.perform_auth(code)
    client.get_access_token()
    album = client.get_album('album id')
    
    return album

# Returns artist info using artist id
@app.route('/get_artist/<code>')
def get_artist(code):
    client = SpotifyAPI(
        CLIENT_ID, 
        CLIENT_SECRET, 
        REDIRECT_URI
    )
    client.get_token_data(code)

    client.perform_auth(code)
    client.get_access_token()
    artist = client.get_artist('artist id')
    
    return artist

"""    


if __name__ == '__main__':
    app.run()