import requests
from bs4 import BeautifulSoup
import sys

URL = "https://freeiptv2023-d.ottc.xyz/index.php?action=view"
OUTPUT_FILE = "playlist.m3u"

# Adding headers to look like a real Chrome browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_m3u():
    try:
        print("Connecting to website...")
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        m3u_input = soup.find('input', {'id': 'm3uLink'})
        
        if not m3u_input:
            print("Error: Could not find the 'm3uLink' ID on the page.")
            # We exit with 1 so GitHub Actions knows the scraper failed
            sys.exit(1)

        m3u_url = m3u_input.get('value')
        print(f"Success! Found URL: {m3u_url}")

        # Download the actual file
        print("Downloading M3U file...")
        m3u_content = requests.get(m3u_url, headers=HEADERS, timeout=60)
        m3u_content.raise_for_status()

        with open(OUTPUT_FILE, 'wb') as f:
            f.write(m3u_content.content)
        
        print(f"File saved successfully as {OUTPUT_FILE}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_m3u()
