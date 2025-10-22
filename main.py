import os
import requests
import spotipy
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
USERNAME = os.getenv("SPOTIFY_USERNAME")
REDIRECT_URI = "https://example.com"


def authenticate_spotify():
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="playlist-modify-private",
            username=USERNAME,
            show_dialog=True,
            cache_path="token.txt"
        )
    )
    if sp is None:
        print("Authentication failed.")
        return
    else:
        return sp


# Prompt the user for a date
date_requested = input("Enter the date you want to use for the Billboard Top 100 list (YYYY-MM-DD): ")
filename = f"top_100_{date_requested}.html"

# Check if the file already exists to avoid multiple requests
if os.path.exists(filename):
    with open(filename, "r") as file:
        web_page = file.read()
else:
    # Make a request to the Billboard website
    url = f"https://www.billboard.com/charts/hot-100/{date_requested}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    web_page = response.text
    # Save the web page HTML contents to a file
    with open(filename, "w") as file:
        file.write(web_page)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(web_page, "html.parser")
songs = [song.get_text(strip=True) for song in soup.select("li ul li h3")]
artists = [artist.get_text(strip=True) for artist in soup.select("li ul li h3 + span")]

# Save the songs and artists to a text file
with open("songs.txt", "w", encoding="utf-8") as file:
    for i in range(len(songs)):
    # for song in songs:
        file.write(f"{i + 1}. {songs[i]} by {artists[i]}\n")
        # file.write(f"{song}\n")

# Authenticate with Spotify
sp = authenticate_spotify()
user_id = sp.current_user()["id"]

if sp is None:
    exit()

song_uris = []

for song in songs:
    song_query = f"track:{song} year:{date_requested.split('-')[0]}"
    results = sp.search(q=song_query, type="track")

    if results['tracks']['items']:
        first_track = results['tracks']['items'][0]
        song_uris.append(first_track['uri'])
        print(f"Found track: {first_track['name']} by {first_track['artists'][0]['name']}")
    else:
        print(f"No results found for: {song}")

print(f"Total tracks found: {len(song_uris)}")

# Create a new private playlist
playlist_name = f"Billboard Top 100: {date_requested}"
playlist_description = f"Top 100 songs from Billboard on {date_requested}"

spotify_playlist = sp.user_playlist_create(
    user=user_id,
    name=playlist_name,
    public=False,
    description=playlist_description
    )

playlist_id = spotify_playlist['id']

# Add songs to the newly created playlist
if song_uris:
    sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=song_uris)
    print(f"Added {len(song_uris)} songs to the playlist '{playlist_name}'.")