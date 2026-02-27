import re
import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

FILE_PATH = "channels.m3u"
MAX_THREADS = 50   # You can increase to 80 if VPS is strong

# =====================================
# 🔎 FAST Stream Checker
# =====================================
def is_stream_valid(url):
    try:
        # Use HEAD (much faster than GET)
        r = requests.head(url, timeout=6, allow_redirects=True)

        # Keep these status codes
        if r.status_code in (200,451):   # Removed 404,403
            return True

        return False

    except requests.exceptions.RequestException:
        return False


# =====================================
# 📖 Parse M3U
# =====================================
def parse_m3u(file_path):
    channels = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'(#EXTINF:.*?,(.*?)\n(.*?)(?=\n#EXTINF|$))', re.DOTALL)
    matches = pattern.findall(content)

    for full_block, name, url in matches:
        url = url.strip()
        lang_match = re.search(r'tvg-language="(.*?)"', full_block)
        lang = lang_match.group(1) if lang_match else "Unknown"

        channels.append({
            "inf_line": full_block.split('\n')[0],
            "name": name.strip(),
            "url": url,
            "language": lang
        })

    return channels


# =====================================
# 🚀 Main
# =====================================
def main():
    print(f"📖 Reading {FILE_PATH}...")
    all_channels = parse_m3u(FILE_PATH)

    print(f"🔎 Checking {len(all_channels)} streams using {MAX_THREADS} threads...")

    working_channels = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_channel = {
            executor.submit(is_stream_valid, ch["url"]): ch
            for ch in all_channels
        }

        for future in as_completed(future_to_channel):
            ch = future_to_channel[future]
            if future.result():
                working_channels.append(ch)

    print(f"✅ Valid streams kept: {len(working_channels)}")

    # Remove duplicates
    unique_channels = []
    seen = set()

    for ch in working_channels:
        if ch["url"] not in seen:
            unique_channels.append(ch)
            seen.add(ch["url"])

    # Language count
    lang_counts = Counter(ch['language'] for ch in unique_channels)

    # Overwrite file
    print("✍️ Writing cleaned file...")
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for ch in unique_channels:
            inf = ch['inf_line']
            lang = ch['language']

            if lang_counts[lang] <= 5:
                inf = re.sub(r'tvg-language=".*?"', 'tvg-language="Unknown"', inf)

            f.write(f"\n{inf},{ch['name']}\n{ch['url']}\n")

    print("🎉 Done! Dead removed, 404 kept.")


if __name__ == "__main__":
    main()
