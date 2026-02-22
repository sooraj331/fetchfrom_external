import requests
from bs4 import BeautifulSoup
import re

# Configuration
URL = "https://freeiptv2023-d.ottc.xyz/index.php?action=view"
OUTPUT_FILE = "playlist.m3u"

def get_m3u():
    try:
        # 1. Fetch the webpage
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        
        # 2. Parse HTML to find the input value
        soup = BeautifulSoup(response.text, 'html.parser')
        m3u_input = soup.find('input', {'id': 'm3uLink'})
        
        if not m3u_input:
            print("Could not find the m3uLink ID on the page.")
            return

        m3u_url = m3u_input.get('value')
        print(f"Found URL: {m3u_url}")

        # 3. Download the M3U content
        m3u_content = requests.get(m3u_url, timeout=60)
        m3u_content.raise_for_status()

        # 4. Save to file
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(m3u_content.content)
        print("Successfully updated playlist.m3u")

    except Exception as e:
        print(f"Error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    get_m3u()
