import os
import requests
from bs4 import BeautifulSoup

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
        file.write(f"{i + 1}. {songs[i]} by {artists[i]}\n")