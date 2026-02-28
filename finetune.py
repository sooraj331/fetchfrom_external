import re
import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

FILE_PATH = "channels.m3u"
MAX_THREADS = 50   # You can increase to 80 if VPS is strong

# Standard User-Agent to mimic a real browser/player
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# =====================================
# 🔎 FAST Stream Checker
# =====================================
def is_stream_valid(url):
    try:
        # Using HEAD + User-Agent for speed and compatibility
        r = requests.head(url, headers=HEADERS, timeout=6, allow_redirects=True)

        # Strictly check for HTTP 200 OK
        if r.status_code == 200:
            return True

        return False

    except requests.exceptions.RequestException:
        return False


# =====================================
# 📖 Parse M3U
# =====================================
def parse_m3u(file_path):
    channels = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found.")
        return []

    # Improved regex to capture the full info line and URL block
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
    
    if not all_channels:
        return

    print(f"🔎 Checking {len(all_channels)} streams (Accepting 200 OK only)...")

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

    # Remove duplicates based on URL
    unique_channels = []
    seen = set()
    for ch in working_channels:
        if ch["url"] not in seen:
            unique_channels.append(ch)
            seen.add(ch["url"])

    print(f"✅ Valid unique streams kept: {len(unique_channels)}")

    # Language count logic
    lang_counts = Counter(ch['language'] for ch in unique_channels)

    # Overwrite file
    print("✍️ Writing cleaned file...")
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for ch in unique_channels:
            inf = ch['inf_line']
            lang = ch['language']

            # Simplify low-frequency languages
            if lang_counts[lang] <= 5:
                inf = re.sub(r'tvg-language=".*?"', 'tvg-language="Unknown"', inf)

            f.write(f"\n{inf},{ch['name']}\n{ch['url']}\n")

    print(f"🎉 Done! Only 'HTTP 200' streams remain in {FILE_PATH}.")


if __name__ == "__main__":
    main()
