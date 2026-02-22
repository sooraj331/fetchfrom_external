import requests
import datetime

# IPTV-org API
API_URL = "https://iptv-org.github.io/api/channels.json"

# Output file
OUTPUT_FILE = "channels.m3u"

def fetch_channels():
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()

def create_m3u(channels):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        for ch in channels:
            name = ch.get("name", "")
            country = ch.get("country", "")
            language = ",".join([l["name"] for l in ch.get("languages", [])])
            category = ",".join(ch.get("categories", []))
            url = ch.get("url", "")

            if not url:
                continue

            f.write(
                f'#EXTINF:-1 tvg-name="{name}" '
                f'tvg-country="{country}" '
                f'tvg-language="{language}" '
                f'tvg-category="{category}",'
                f'{name}\n'
            )
            f.write(f"{url}\n\n")

def main():
    print("Fetching channels...")
    channels = fetch_channels()
    print(f"Total channels: {len(channels)}")

    create_m3u(channels)
    print("M3U file created successfully.")

if __name__ == "__main__":
    main()
