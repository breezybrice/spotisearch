#!/usr/bin/env python
# coding: utf-8

import base64
import datetime
import authhelp as auth
from urllib.parse import urlencode
import requests
import json

# SpotifyAPI client using Client Credentials Auth Flow
# Authentication Process. Uses helpers.py and .env file

"""
Creating an instance
spotify = SpotifyAPI(client_id, client_secret)

"""

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    redirect_uri = None
    token_url = "https://accounts.spotify.com/api/token"
    
    def __init__(self, client_id, client_secret, redirect_uri, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_client_credentials(self):
        # Auth Step 1: Converts clent_creds into a 'base64' encoded string.
        # Encodes to bytes -> b64. Then decodes bytes.  
        # In preparation for headers.
        
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_headers(self):
        #Auth Step 2: Add client_creds to Headers

        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def get_token_data(self, code):
        # Auth Step 3: Add Body Parameters of the Auth POST Request
        # in Requests, 'data' is the variable used for passing a dict to request body
        return {
            "grant_type": "authorization_code",
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        } 
    
    def perform_auth(self, code):                     # Request Authorization - getting access token in return
        token_url = self.token_url              # Endpoint to Request Access Token 
        token_data = self.get_token_data(code)      # Body Parameters of request
        token_headers = self.get_token_headers() # Headers with client credentials

        r = requests.post(token_url, data=token_data, headers=token_headers) #Auth POST Request
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")

        token = r.json() # JSON Response with access_token, token_type, and token expiration time
        auth.store_tokens(token)
       
        print(f'{r.status_code} - Successfully completed Auth flow!')
        return True
    
    ##################### Using the Access Token #####################

    def get_access_token(self):
        # Return Access Token or Refresh Access Token
        token = auth.get_tokens()
        access_token = token['access_token']
        expires = token['expires_in'] #seconds
        # token = self.access_token
        # expires = self.access_token_expires
        now = datetime.datetime.now()
        exp = now + datetime.timedelta(seconds=expires)
        #exp = now + datetime.datetime.fromtimestamp(expires)
        if exp < now:
            self.perform_auth()             # Performing Auth if token expired
            return self.get_access_token()
        elif access_token == None:
            self.perform_auth()             # Performing Auth if there is no token
            return self.get_access_token() 
        return access_token                        # Return access_token
    
    def refresh_tokens(self):
        # Refresh expired token and store in json file
        token_url = self.token_url
        tokens = auth.get_tokens()
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']
        }
        base64encoded = str(base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode('ascii')), 'ascii')
        headers = {'Authorization': f'Basic {base64encoded}'}

        # post request for new tokens
        r = requests.post(token_url, data=payload, headers=headers)
        response = r.json()
        auth.store_refresh_tokens(response['access_token'], tokens['refresh_token'], response['expires_in'])

        print('Tokens refreshed!')
        return 
    
    def get_resource_header(self):
        # Add Access Token to Headers of all API calls
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers
        

                    #########
        ########## Resources ##########
                    #########


    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        # General Resource function used in other API calls // Get Artist, Get Album
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    
    def get_artistAlbums(self, lookup_id, resource_type1='artists', resource_type2='albums', version='v1'):
        # General Resource function used in other API calls // Get Artist's Albums
        endpoint = f"https://api.spotify.com/{version}/{resource_type1}/{lookup_id}/{resource_type2}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()    
    
    def get_playlistItems(self, lookup_id, resource_type1='playlists', resource_type2='tracks', version='v1'):
        # General Resource function used in other API calls // Get Playlist Items
        endpoint = f"https://api.spotify.com/{version}/{resource_type1}/{lookup_id}/{resource_type2}?limit=50"
        headers = self.get_resource_header()
        
        r = requests.get(endpoint, headers=headers)
       
        tracks = []
        data = r.json()

        tracks += data['items']

        # The JSON data returned has a 'next' item that has a link 
        # to the next page of results. This loop adds each page of 
        # items to the list after sending a GET request to the next page.
        url = data['next']

        while url:
            response = requests.get(url, headers=headers)
            data = response.json()
            tracks += data['items']
            url = data['next']

        if r.status_code not in range(200, 299):
            return {}
        return tracks
        #return r.json()  

    def get_artist_albums(self, _id):
        return self.get_artistAlbums(_id) 

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')
    
    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')
    

    def get_album_tracks(self, _id):
        pass

    def track_audio_features(self, _id):
        return self.get_resource(_id, resource_type='audio-features')
    
    def get_playlist_items(self, _id):
        return self.get_playlistItems(_id)

        

        # Search For Artist Info

    def base_search(self, query_params): # type
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        # if r.status_code not in range(200, 299):  
            # return {}
        return r.json()
    
    def search(self, query=None, operator=None, operator_query=None, search_type='artist' ):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        print(query_params)
        return self.base_search(query_params)
