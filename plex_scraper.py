#!/usr/bin/env python3
import requests
import json
import gzip
from datetime import datetime

# Configuration
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
CHANNELS_URL = "https://i.mjh.nz/Plex/.channels.json.gz"
EPG_URL = "https://iptv-org.github.io/epg/guides/usa.xml"  # Public EPG for US channels

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

def map_tvg_id(channel_name):
    """Map channel names to IPTV-org EPG tvg-ids (basic heuristic)."""
    name_lower = channel_name.lower()
    if "abc" in name_lower:
        return "ABC.us"
    elif "cbs" in name_lower:
        return "CBS.us"
    elif "nbc" in name_lower:
        return "NBC.us"
    elif "fox" in name_lower:
        return "FOX.us"
    else:
        return f"plex_{name_lower.replace(' ', '_')}"

def generate_m3u(channels_data, filename):
    """Generate an M3U playlist file with EPG tags."""
    if not channels_data:
        print("No channels data to generate M3U.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{filename}_{timestamp}.m3u"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U url-tvg="{EPG_URL}"\n')  # Fixed: Complete f-string
        
        for channel_id, channel_info in channels_data.items():
            name = channel_info.get("name", "Unknown Channel")
            url = channel_info.get("url", "")
            if not url:
                continue
            
            tvg_id = map_tvg_id(name)
            f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}",{name}\n')
            f.write(f"{url}\n")
    
    print(f"Saved M3U playlist to {output_filename}")

def main():
    """Main function to run the Plex scraper and generate an M3U playlist."""
    print("Starting Plex scraper...")
    
    channels_data = fetch_channels()
    generate_m3u(channels_data, "plex_channels")
    
    print("Plex scraping completed.")

if __name__ == "__main__":
    main()
