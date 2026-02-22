import requests

CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"
FEEDS_URL    = "https://iptv-org.github.io/api/feeds.json"
LOGOS_URL    = "https://iptv-org.github.io/api/logos.json"
STREAMS_URL  = "https://iptv-org.github.io/api/streams.json"

OUTPUT_FILE = "channels.m3u"

def fetch_json(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def main():
    print("Fetching JSON data...")
    channels = fetch_json(CHANNELS_URL)
    feeds    = fetch_json(FEEDS_URL)
    logos    = fetch_json(LOGOS_URL)
    streams  = fetch_json(STREAMS_URL)

    print(f"Channels: {len(channels)}, Feeds: {len(feeds)}, Logos: {len(logos)}, Streams: {len(streams)}")

    # Map data by channel id
    channel_languages = {}
    for feed in feeds:
        cid = feed.get("channel")
        lang = feed.get("language", "")
        if cid and lang:
            if isinstance(lang, dict):
                lang_name = lang.get("name", "")
            else:
                lang_name = str(lang)
            if lang_name:
                channel_languages.setdefault(cid, []).append(lang_name)

    channel_logos = {logo["channel"]: logo.get("url", "") for logo in logos if "channel" in logo}
    channel_streams = {stream["channel"]: stream.get("url", "") for stream in streams if "channel" in stream}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        count = 0
        for ch in channels:
            cid = ch.get("id")
            name = ch.get("name", "")
            country = ch.get("country", "")
            url = channel_streams.get(cid, "")

            if not url:
                continue

            languages = ",".join(channel_languages.get(cid, []))
            logo = channel_logos.get(cid, "")

            f.write(
                f'#EXTINF:-1 tvg-id="{cid}" '
                f'tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'tvg-country="{country}" '
                f'tvg-language="{languages}",'
                f'{name}\n'
            )
            f.write(f"{url}\n\n")
            count += 1

    print(f"M3U file created: {OUTPUT_FILE} ({count} channels)")

if __name__ == "__main__":
    main()
