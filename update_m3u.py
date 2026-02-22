import requests

# API Endpoints
CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"
FEEDS_URL    = "https://iptv-org.github.io/api/feeds.json"
LOGOS_URL    = "https://iptv-org.github.io/api/logos.json"
STREAMS_URL  = "https://iptv-org.github.io/api/streams.json"
LANGUAGES_URL= "https://iptv-org.github.io/api/languages.json"

OUTPUT_FILE = "channels.m3u"

def fetch_json(url):
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f" Error fetching {url}: {e}")
        return []

def main():
    print("Fetching JSON data...")
    channels = fetch_json(CHANNELS_URL)
    feeds    = fetch_json(FEEDS_URL)
    logos    = fetch_json(LOGOS_URL)
    streams  = fetch_json(STREAMS_URL)
    languages_map = fetch_json(LANGUAGES_URL)

    # 1. Map language codes (e.g., "fra") to full names (e.g., "French")
    lang_code_to_name = {l["code"]: l["name"] for l in languages_map if "code" in l and "name" in l}

    # 2. Map channel ID to unique languages using the "languages" key from feeds.json
    channel_languages = {}
    for feed in feeds:
        cid = feed.get("channel")
        if not cid:
            continue
        
        # FIX: Accessing the plural "languages" key as seen in the API
        raw_langs = feed.get("languages", [])
        
        # Ensure we are working with a list
        if isinstance(raw_langs, str):
            raw_langs = [raw_langs]
            
        if cid not in channel_languages:
            channel_languages[cid] = set()

        for code in raw_langs:
            # Map code to name, fallback to code if not found
            name = lang_code_to_name.get(code, code)
            channel_languages[cid].add(name)

    # 3. Map Logos
    channel_logos = {logo["channel"]: logo.get("url", "") for logo in logos if "channel" in logo}

    # 4. Map Streams (handling multiple streams per channel)
    channel_streams = {}
    for s in streams:
        cid = s.get("channel")
        url = s.get("url", "")
        if cid and url:
            stream_data = {
                "url": url, 
                "user_agent": s.get("user_agent", ""), 
                "referrer": s.get("referrer", "")
            }
            channel_streams.setdefault(cid, []).append(stream_data)

    # 5. Generate the M3U File
    print(f"Creating {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        count = 0
        
        for ch in channels:
            cid = ch.get("id")
            
            # Skip if no stream exists for this channel
            if cid not in channel_streams:
                continue

            name = ch.get("name", "Unknown Channel")
            country = ch.get("country", "")
            logo = channel_logos.get(cid, "")
            
            # Convert set of languages to a comma-separated string
            langs_list = list(channel_languages.get(cid, []))
            languages_str = ",".join(langs_list)
            
            # Join categories
            categories = ch.get("categories", [])
            group_title = ";".join(categories) if categories else "Other"

            # Write an entry for every stream found for this channel
            for stream in channel_streams[cid]:
                url = stream["url"]
                ua = stream["user_agent"]
                ref = stream["referrer"]

                # Formatting the #EXTINF line
                # Note: http-user-agent and http-referrer help with stream compatibility
                line = (f'#EXTINF:-1 tvg-id="{cid}" '
                        f'tvg-name="{name}" '
                        f'tvg-logo="{logo}" '
                        f'tvg-country="{country}" '
                        f'tvg-language="{languages_str}" '
                        f'group-title="{group_title}"')
                
                if ua: line += f' http-user-agent="{ua}"'
                if ref: line += f' http-referrer="{ref}"'
                
                f.write(f"{line},{name}\n")
                f.write(f"{url}\n\n")
                count += 1

    print(f"Done! M3U file created with {count} entries.")

if __name__ == "__main__":
    main()
