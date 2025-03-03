#!/usr/bin/env python3
import requests
import json
import gzip
from datetime import datetime

# Configuration
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
CHANNELS_URL = "https://i.mjh.nz/Plex/.channels.json.gz"

# Headers (no token needed)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json"
}

def fetch_channels():
    """Fetch and decompress the channels JSON from the provided URL."""
    print(f"Fetching channels data from {CHANNELS_URL}")
    try:
        response = requests.get(CHANNELS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        print(f"Channels data downloaded: {response.status_code}")
        
        # Decompress the gzip content
        decompressed_data = gzip.decompress(response.content)
        channels_data = json.loads(decompressed_data.decode("utf-8"))
        print(f"Channels data decompressed and parsed successfully")
        return channels_data
    except (requests.RequestException, json.JSONDecodeError, gzip.BadGzipFile) as e:
        print(f"Error fetching or processing channels data: {e}")
        return None

def save_data(data, filename):
    """Save data to a JSON file with a timestamp."""
    if data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{filename}_{timestamp}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Saved data to {output_filename}")
    else:
        print(f"No data to save for {filename}")

def main():
    """Main function to run the Plex scraper."""
    print("Starting Plex scraper...")
    
    # Fetch and save channels data
    channels_data = fetch_channels()
    save_data(channels_data, "plex_channels")
    
    print("Plex scraping completed.")

if __name__ == "__main__":
    main()
