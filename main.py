import time
import requests
from bs4 import BeautifulSoup
import subprocess
import re
import sys
import json
import os
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

def search_imdb(title):
    url = f"https://v2.sg.media-imdb.com/suggestion/{title[0].lower()}/{title.lower().replace(' ', '_')}.json"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(" Failed to search IMDb.")
        sys.exit(1)
    data = res.json()
    results = data.get('d', [])
    top5 = [r for r in results if 'id' in r and 'l' in r and 'y' in r][:5]
    return top5

def choose_movie(movies):
    print("\n Top Results:\n")
    headers = ["No", "Title", "Year", "IMDb ID"]
    rows = [[idx + 1, m['l'], m.get('y', 'N/A'), m['id']] for idx, m in enumerate(movies)]

    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*([headers] + rows))]

    def format_row(row):
        return "".join(f"  {str(cell).ljust(width)}" for cell, width in zip(row, col_widths))

    print(format_row(headers))
    print("".join(f"  {'-' * width}" for width in col_widths))
    for row in rows:
        print(format_row(row))

    choice = int(input("\n  Select a movie (1-5): ")) - 1
    return movies[choice]['id']

def get_edgedelivery_link(imdb_id):
    base_url = "https://vidsrcme.vidsrc.icu/embed/movie?imdb="
    video_url = f"{base_url}{imdb_id}&autoplay=1"
    
    res = requests.get(video_url, headers=HEADERS)
    if res.status_code != 200:
        print("  Failed to fetch movie page.")
        sys.exit(1)

    soup = BeautifulSoup(res.text, 'html.parser')
    iframe = soup.find('iframe')
    if iframe and 'src' in iframe.attrs:
        link = iframe['src']
        return 'https:' + link if link.startswith('//') else link
    print("No iframe video link found.")
    sys.exit(1)

def write_to_input_file(link):
    with open("input.txt", "w") as f:
        f.write(link)

def run_node_extractor():
    subprocess.run(['node', '.'])

def read_output(file_path='output.txt'):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None
    except IOError:
        print(f"An error occurred while reading the file {file_path}.")
        return None

def play_in_mpv(link):
#      subprocess.run(['vlc', '-f', link])
      subprocess.run(['mpv', '--quiet', '--no-terminal', link])

def main():
    title = input("\nEnter movie title: ").strip()
    results = search_imdb(title)
    imdb_id = choose_movie(results)
    print(f"\n Selected IMDb ID: {imdb_id}\n")

    site_url = get_edgedelivery_link(imdb_id)
    print(f" Movie found successfully.\n")

    write_to_input_file(site_url)
    run_node_extractor()

    stream_link = read_output()
    if stream_link:
        print(" Launching player...\n")
        play_in_mpv(stream_link)
        open("output.txt", "w").close()
    else:
        print("\nSorry, Unable to fetch stream at the moment. You can watch the movie using the link!\n")

if __name__ == "__main__":
    main()

