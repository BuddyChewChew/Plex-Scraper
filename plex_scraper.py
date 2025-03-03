#!/usr/bin/env python3
import requests
import json
import gzip
from datetime import datetime, UTC

# Configuration
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
CHANNELS_URL = "https://github.com/matthuisman/i.mjh.nz/raw/refs/heads/master/Plex/.channels.json.gz"
EPG_FILE = "epg.xml"  # Local EPG file to be generated

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
        # Access the 'channels' key
        channel_list = channels_data.get("channels", {})
        print(f"Channels data decompressed and parsed successfully. Found {len(channel_list)} channels.")
        return channel_list
    except (requests.RequestException, json.JSONDecodeError, gzip.BadGzipFile) as e:
        print(f"Error fetching or processing channels data: {e}")
        return None

def generate_m3u(channels_data, filename):
    """Generate an M3U playlist file with EPG tags."""
    if not channels_data:
        print("No channels data to generate M3U.")
        return None

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_filename = f"{filename}_{timestamp}.m3u"
    
    channels_added = 0
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U url-tvg="{EPG_FILE}"\n')
        
        for channel_id, channel_info in channels_data.items():
            name = channel_info.get("name", "Unknown Channel")
            url = channel_info.get("url", "")
            print(f"Processing channel: {channel_id}, Name: {name}, URL: {url}")
            if not url:
                print(f"Skipping {channel_id}: No URL provided.")
                continue
            
            f.write(f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name}",{name}\n')
            f.write(f"{url}\n")
            channels_added += 1
    
    print(f"Saved M3U playlist to {output_filename} with {channels_added} channels.")
    return output_filename

def generate_basic_epg(channels_data, filename):
    """Generate a basic EPG XML file with static entries."""
    if not channels_data:
        print("No channels data to generate EPG.")
        return None

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_filename = f"{filename}_{timestamp}.xml"
    
    today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = today.strftime("%Y%m%d%H%M%S +0000")
    end_time = today.replace(hour=23, minute=59, second=59).strftime("%Y%m%d%H%M%S +0000")
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')
        f.write('<tv>\n')
        
        for channel_id, channel_info in channels_data.items():
            name = channel_info.get("name", "Unknown Channel")
            f.write(f'  <channel id="{channel_id}">\n')
            f.write(f'    <display-name>{name}</display-name>\n')
            f.write('  </channel>\n')
            f.write(f'  <programme start="{start_time}" stop="{end_time}" channel="{channel_id}">\n')
            f.write(f'    <title>{name} Live</title>\n')
            f.write(f'    <desc>Live streaming content from {name}</desc>\n')
            f.write('  </programme>\n')
        
        f.write('</tv>\n')
    
    print(f"Saved basic EPG to {output_filename}")
    return output_filename

def main():
    """Main function to run the Plex scraper and generate M3U and EPG."""
    print("Starting Plex scraper...")
    
    channels_data = fetch_channels()
    if channels_data:
        m3u_file = generate_m3u(channels_data, "plex_channels")
        epg_file = generate_basic_epg(channels_data, "epg")
    else:
        print("Failed to fetch channels, no files generated.")
    
    print("Plex scraping completed.")

if __name__ == "__main__":
    main()
