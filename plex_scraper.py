#!/usr/bin/env python3
import requests
import json
import gzip
import os
from datetime import datetime

# Configuration
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
CHANNELS_URL = "https://i.mjh.nz/Plex/.channels.json.gz"
ANONYMOUS_URL = "https://clients.plex.tv/api/v2/users/anonymous"
APP_URL = "https://app.plex.tv"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "X-Plex-Token": PLEX_TOKEN if PLEX_TOKEN else ""
}

def fetch_anonymous_user():
    print(f"Fetching anonymous user data from {ANONYMOUS_URL}")
    try:
        response = requests.get(ANONYMOUS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print(f"Anonymous user data fetched successfully: {response.status_code}")
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching anonymous user data: {e}")
        return None

def fetch_channels():
    print(f"Fetching channels data from {CHANNELS_URL}")
    try:
        response = requests.get(CHANNELS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print(f"Channels data downloaded: {response.status_code}")
        
        decompressed_data = gzip.decompress(response.content)
        channels_data = json.loads(decompressed_data.decode("utf-8"))
        print(f"Channels data decompressed and parsed successfully")
        return channels_data
    except (requests.RequestException, json.JSONDecodeError, gzip.BadGzipFile) as e:
        print(f"Error fetching or processing channels data: {e}")
        return None

def save_data(data, filename):
    if data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{filename}_{timestamp}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Saved data to {output_filename}")
    else:
        print(f"No data to save for {filename}")

def main():
    if not PLEX_TOKEN:
        print("PLEX_TOKEN not set. Please configure it in GitHub Secrets.")
        return

    print("Starting Plex scraper...")
    anonymous_data = fetch_anonymous_user()
    save_data(anonymous_data, "anonymous_user")
    channels_data = fetch_channels()
    save_data(channels_data, "plex_channels")
    print("Plex scraping completed.")

if __name__ == "__main__":
    main()
