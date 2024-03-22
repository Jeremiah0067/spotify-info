from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import csv

load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')


def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
    
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization' : 'Basic ' + auth_base64,
         'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type':'client_credentials'}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {'Authorization': "Bearer " + token}

def search_for_artist(token, artist_name):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_results = json.loads(result.content)
    return json_results

def get_artist_info(token, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = get_auth_header(token)
    
    response = get(url, headers=headers)
    artist_info = response.json()
    return artist_info

def get_artist_tracks(token, artist_id):
    url = f'https://api.spotify.com/v1/artists/{artist_id}/albums' 
    headers = get_auth_header(token)
    params = {'market':'US'}
    
    response = get(url, headers=headers, params=params)
    albums_data = response.json()['items']
    
    tracks = []
    for album in albums_data:
        album_id = album['id']
        album_tracks = get_album_tracks(token, album_id)
        tracks.extend(album_tracks)
    
    return tracks

def get_album_tracks(token, album_id):
    url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
    headers = get_auth_header(token)
    
    response = get(url, headers=headers)
    tracks_data = response.json()['items']
    
    return tracks_data

def save_artist_data(artist_name, artist_info, tracks):
    with open(f'{artist_name}_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Artist Name', 'Artist ID', 'Artist Followers', 'Track Name', 'Track ID', 'Album Name', 'Album ID']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for track in tracks:
            if 'album' in track and 'name' in track['album']:
                album_name = track['album']['name']
                album_id = track['album']['id']
                
            else:
                album_name = 'N/A'
                album_id = 'N/A'
            writer.writerow({
                'Artist Name': artist_name,
                'Artist ID': artist_info['id'],
                'Artist Followers': artist_info['followers']['total'],
                'Track Name': track['name'],
                'Track ID': track['id'],
                'Album Name': album_name,
                'Album ID': album_id
            })

# Main function
def main():
    artist_name = input("Enter artist name: ")
    token = get_token()
    search_results = search_for_artist(token, artist_name)
    
    if 'artists' in search_results and 'items' in search_results['artists']:
        artist = search_results['artists']['items'][0]  # Assuming the first artist in the search results
        artist_id = artist['id']
        artist_info = get_artist_info(token, artist_id)
        tracks = get_artist_tracks(token, artist_id)
        
        if tracks:
            save_artist_data(artist_name, artist_info, tracks)
            print(f"Artist data for {artist_name} saved to '{artist_name}_data.csv'")
        else:
            print("No tracks found for the artist.")
    else:
        print("Artist not found.")

if __name__ == "__main__":
    main()
