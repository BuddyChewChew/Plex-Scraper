import requests
from bs4 import BeautifulSoup
import json
import re
import os
from urllib.parse import urlparse, urlunparse, unquote
from datetime import datetime
import unicodedata
import urllib3

# Disable the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_plex_data(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, verify=False, timeout=20)
            response.encoding = 'utf-8'
            if response.status_code != 200:
                print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
                continue

            html_content = response.content.decode('utf-8', errors='replace')
            soup = BeautifulSoup(html_content, "html.parser")

            script_tags = soup.find_all("script")
            target_script = None
            for script in script_tags:
                if script.string and script.string.strip().startswith("window.__data"):
                    target_script = script.string
                    break

            if not target_script:
                print("Error: Could not locate the JSON-like data in the page.")
                continue

            start_index = target_script.find("{")
            end_index = target_script.rfind("}") + 1
            json_string = target_script[start_index:end_index]
            json_string = json_string.encode('utf-8', errors='replace').decode('utf-8')
            json_string = json_string.replace('undefined', 'null')
            json_string = re.sub(r'new Date\("([^"]*)"\)', r'"\1"', json_string)
            data = json.loads(json_string)
            return data
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
    return []

def create_m3u_playlist(data, country):
    sorted_data = sorted(data, key=lambda x: x.get('title', '').lower())
    playlist = f"#EXTM3U url-tvg=\"https://plex.tv/epg.xml\"\n"
    playlist += f"# Generated on {datetime.now().isoformat()}\n"
    seen_urls = set()

    for elem in sorted_data:
        channel_name = elem.get('title', 'Unknown Channel')
        channel_name = channel_name.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        stream_url = unquote(elem['video_resources'][0]['manifest']['url']) if elem.get('video_resources') else ''
        clean_url = urlunparse(urlparse(stream_url)._replace(query='', fragment=''))
        tvg_id = str(elem.get('content_id', ''))
        logo_url = elem.get('images', {}).get('thumbnail', [None])[0]
        group_title = elem.get('group', 'Other')
        group_title = group_title.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

        if clean_url and clean_url not in seen_urls:
            playlist += f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo_url}" group-title="{group_title}",{channel_name}\n{clean_url}\n'
            seen_urls.add(clean_url)

    return playlist

def save_file(content, filename):
    file_path = os.path.join(os.getcwd(), filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"File saved: {file_path}")

def main():
    url = "https://plex.tv/live"
    json_data = fetch_plex_data(url)
    if not json_data:
        print("Failed to fetch data.")
        return

    m3u_playlist = create_m3u_playlist(json_data, "us")
    save_file(m3u_playlist, "plex_playlist.m3u")

if __name__ == "__main__":
    main()
