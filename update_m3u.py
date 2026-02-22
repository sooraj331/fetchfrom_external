import requests

API_URL = "https://iptv-org.github.io/api/channels.json"
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
            logo = ch.get("logo", "")
            url = ch.get("url", "")

            languages = ",".join([l["name"] for l in ch.get("languages", [])])
            categories = ",".join(ch.get("categories", []))

            if not url:
                continue

            f.write(
                f'#EXTINF:-1 '
                f'tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'tvg-country="{country}" '
                f'tvg-language="{languages}" '
                f'tvg-category="{categories}",'
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
