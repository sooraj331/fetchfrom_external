import requests
from collections import Counter

# API Endpoints
BASE_URL = "https://iptv-org.github.io/api"
CHANNELS_URL = f"{BASE_URL}/channels.json"
FEEDS_URL    = f"{BASE_URL}/feeds.json"
LOGOS_URL    = f"{BASE_URL}/logos.json"
STREAMS_URL  = f"{BASE_URL}/streams.json"
LANGUAGES_URL= f"{BASE_URL}/languages.json"

OUTPUT_FILE = "channels.m3u"

def fetch_json(session, url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = session.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f" Error fetching {url}: {e}")
        return []

def main():
    session = requests.Session()
    
    print("🛰️  Fetching JSON data...")
    channels = fetch_json(session, CHANNELS_URL)
    feeds    = fetch_json(session, FEEDS_URL)
    logos    = fetch_json(session, LOGOS_URL)
    streams  = fetch_json(session, STREAMS_URL)
    languages_map = fetch_json(session, LANGUAGES_URL)

    # 1. Map language codes to names
    lang_code_to_name = {l["code"]: l["name"] for l in languages_map if "code" in l}

    # 2. Map channel ID to their Primary Language & Count occurrences
    channel_primary_lang = {}
    lang_usage_counter = Counter()

    for feed in feeds:
        cid = feed.get("channel")
        if not cid or cid in channel_primary_lang:
            continue
        
        raw_langs = feed.get("languages") or []
        if isinstance(raw_langs, list) and raw_langs:
            code = raw_langs[0]
            lang_name = lang_code_to_name.get(code, code)
            channel_primary_lang[cid] = lang_name
            # Count how many channels use this language
            lang_usage_counter[lang_name] += 1

    # 3. Map Logos and Streams
    channel_logos = {logo["channel"]: logo.get("url", "") for logo in logos if "channel" in logo}
    channel_streams = {}
    for s in streams:
        cid = s.get("channel")
        if cid and s.get("url"):
            channel_streams.setdefault(cid, []).append(s)

    # 4. Generate the M3U File
    print(f"📝 Creating {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        count = 0
        
        for ch in channels:
            cid = ch.get("id")
            if cid not in channel_streams:
                continue

            name = ch.get("name", "Unknown Channel")
            logo = channel_logos.get(cid, "")
            country = ch.get("country", "")
            
            # --- LANGUAGE FILTERING LOGIC ---
            lang = channel_primary_lang.get(cid, "Unknown")
            
            # If the language appears 3 or fewer times, label it as "Unknown"
            if lang_usage_counter[lang] <= 3:
                display_lang = "Unknown"
            else:
                display_lang = lang
            # --------------------------------

            categories = ch.get("categories", [])
            group_title = categories[0].replace("-", " ").title() if categories else "General"

            for stream in channel_streams[cid]:
                url = stream["url"]
                ua = stream.get("user_agent", "")
                ref = stream.get("referrer", "")

                line = (f'#EXTINF:-1 tvg-id="{cid}" tvg-name="{name}" '
                        f'tvg-logo="{logo}" tvg-country="{country}" '
                        f'tvg-language="{display_lang}" group-title="{group_title}"')
                
                if ua: line += f' http-user-agent="{ua}"'
                if ref: line += f' http-referrer="{ref}"'
                
                f.write(f"\n{line},{name}\n{url}\n")
                count += 1

    print(f"✨ Success! Saved {count} entries.")
    print(f"💡 Languages with <= 3 channels were moved to 'Unknown'.")

if __name__ == "__main__":
    main()
