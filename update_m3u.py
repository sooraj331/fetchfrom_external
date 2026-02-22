import cloudscraper
from bs4 import BeautifulSoup
import sys

URL = "https://freeiptv2023-d.ottc.xyz/index.php?action=view"
OUTPUT_FILE = "playlist.m3u"

def get_m3u():
    # cloudscraper bypasses Cloudflare challenges automatically
    scraper = cloudscraper.create_scraper()
    
    try:
        print("Fetching page through Cloudflare...")
        response = scraper.get(URL, timeout=30)
        
        if response.status_code != 200:
            print(f"Failed to load page. Status: {response.status_code}")
            sys.exit(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the input field
        m3u_input = soup.find('input', {'id': 'm3uLink'})
        
        if not m3u_input:
            # Debugging: Print a bit of the HTML to see what the script actually sees
            print("HTML structure received, but 'm3uLink' not found.")
            print("Possible bot protection blocked the content.")
            sys.exit(1)

        m3u_url = m3u_input.get('value')
        print(f"Success! Found URL: {m3u_url}")

        # Download the file
        print("Downloading M3U file...")
        m3u_response = scraper.get(m3u_url, timeout=60)
        
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(m3u_response.content)
        
        print("File saved successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_m3u()
