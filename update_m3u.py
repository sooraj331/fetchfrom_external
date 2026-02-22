import requests

CHANNELS_URL = "https://iptv-org.github.io/api/channels.json"
FEEDS_URL    = "https://iptv-org.github.io/api/feeds.json"
LOGOS_URL    = "https://iptv-org.github.io/api/logos.json"
STREAMS_URL  = "https://iptv-org.github.io/api/streams.json"
LANGUAGES_URL= "https://iptv-org.github.io/api/languages.json"

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
    languages_map = fetch_json(LANGUAGES_URL)

    # Map language codes to full name
    lang_code_to_name = {l["code"]: l["name"] for l in languages_map if "code" in l and "name" in l}

    # Map channel id to languages (full names)
    channel_languages = {}
    for feed in feeds:
        cid = feed.get("channel")
        if not cid:
            continue
        lang_field = feed.get("language", "")
        lang_name = ""
        if isinstance(lang_field, dict):
            code = lang_field.get("code", "")
            lang_name = lang_code_to_name.get(code, code)
        elif isinstance(lang_field, str):
            lang_name = lang_code_to_name.get(lang_field, lang_field)
        elif isinstance(lang_field, list):
            lang_list = []
            for l in lang_field:
                if isinstance(l, dict):
                    code = l.get("code", "")
                    lang_list.append(lang_code_to_name.get(code, code))
                else:
                    lang_list.append(lang_code_to_name.get(str(l), str(l)))
            lang_name = ",".join(lang_list)
        if lang_name:
            channel_languages.setdefault(cid, []).append(lang_name)

    # Logos
    channel_logos = {logo["channel"]: logo.get("url", "") for logo in logos if "channel" in logo}

    # Streams with user_agent and referrer
    channel_streams = {}
    for s in streams:
        cid = s.get("channel")
        url = s.get("url", "")
        if cid and url:
            ua = s.get("user_agent", "")
            ref = s.get("referrer", "")
            channel_streams[cid] = {"url": url, "user_agent": ua, "referrer": ref}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        count = 0
        for ch in channels:
            cid = ch.get("id")
            name = ch.get("name", "")
            country = ch.get("country", "")
            category = ch.get("categories", [])

            stream_info = channel_streams.get(cid)
            if not stream_info:
                continue

            url = stream_info["url"]
            user_agent = stream_info.get("user_agent", "")
            referrer = stream_info.get("referrer", "")

            languages = ",".join(channel_languages.get(cid, []))
            logo = channel_logos.get(cid, "")
            group_title = ",".join(category) if category else "Other"

            f.write(
                f'#EXTINF:-1 tvg-id="{cid}" '
                f'tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'tvg-country="{country}" '
                f'tvg-language="{languages}" '
                f'group-title="{group_title}" '
                f'http-user-agent="{user_agent}" '
                f'http-referrer="{referrer}",{name}\n'
            )
            f.write(f"{url}\n\n")
            count += 1

    print(f"M3U file created: {OUTPUT_FILE} ({count} channels)")

if __name__ == "__main__":
    main()
