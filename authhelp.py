import json


# get access/refresh tokens
def get_tokens():
    with open('tokens.json', 'r') as openfile:
        tokens = json.load(openfile)
    return tokens

# store access/refresh tokens
def store_tokens(response_data):
    tokens = {
        'access_token': response_data['access_token'],
        'refresh_token': response_data['refresh_token'],
        'expires_in': response_data['expires_in']
    }
    with open('tokens.json', 'w') as outfile:
        json.dump(tokens, outfile)

# recieving refreshed token
def store_refresh_tokens(access_token, refresh_token, expires_in):
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': expires_in
    }
    with open('tokens.json', 'w') as outfile:
        json.dump(tokens, outfile)

