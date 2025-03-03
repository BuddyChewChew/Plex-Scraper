#!/usr/bin/env python3
import requests
import json
import gzip
from datetime import datetime

# Configuration
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
CHANNELS_URL = "https://i.mjh.nz/Plex/.channels.json.gz"
EPG_URL = "http://example.com/epg.xml"  # Replace with a real EPG URL if available

# Headers
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
        
        decompressed_data = gzip.decompress(response.content)
        channels_data = json.loads(decompressed_data.decode("utf-8"))
        print(f"Channels data decompressed and parsed successfully")
        return channels_data
    except (requests.RequestException, json.JSONDecodeError, gzip.BadGzipFile) as e:
        print(f"Error fetching or processing channels data: {e}")
        return None

def generate_m3u(channels_data, filename):
    """Generate an M3U playlist file from the channels data."""
    if not channels_data:
        print("No channels data to generate M3U.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{filename}_{timestamp}.m3u"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")  # M3U header
        
        # Add EPG URL if provided
        if EPG_URL:
            f.write(f'#EXTM3U url-t
