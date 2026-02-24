import re
from collections import Counter

# Since both files are in the main root, we use the same name
FILE_PATH = "channels.m3u"

def parse_m3u(file_path):
    """Parses M3U into a list of dictionaries."""
    channels = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to capture the #EXTINF line and the URL that follows it
        pattern = re.compile(r'(#EXTINF:.*?,(.*?)\n(.*?)(?=\n#EXTINF|$))', re.DOTALL)
        matches = pattern.findall(content)
        
        for full_block, name, url in matches:
            url = url.strip()
            # Extract language from the metadata
            lang_match = re.search(r'tvg-language="(.*?)"', full_block)
            lang = lang_match.group(1) if lang_match else "Unknown"
            
            channels.append({
                "inf_line": full_block.split('\n')[0], # The #EXTINF line
                "name": name.strip(),
                "url": url,
                "language": lang
            })
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found in the root directory.")
    return channels

def main():
    print(f"📖 Reading and processing {FILE_PATH}...")
    all_channels = parse_m3u(FILE_PATH)
    
    if not all_channels:
        return

    # 1. Remove Duplicate Streaming Links (m3u8)
    unique_channels = []
    seen_urls = set()
    for ch in all_channels:
        if ch['url'] not in seen_urls:
            unique_channels.append(ch)
            seen_urls.add(ch['url'])
    
    # 2. Count languages only for the unique channels
    lang_counts = Counter(ch['language'] for ch in unique_channels)
    
    # 3. Overwrite the SAME file with refined data
    print(f"✍️  Overwriting {FILE_PATH} with refined data...")
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for ch in unique_channels:
            inf = ch['inf_line']
            lang = ch['language']
            
            # If language appears 3 or fewer times, change to Unknown
            if lang_counts[lang] <= 3:
                inf = re.sub(r'tvg-language=".*?"', 'tvg-language="Unknown"', inf)
            
            f.write(f"\n{inf},{ch['name']}\n{ch['url']}\n")

    print(f"✅ Done! {FILE_PATH} has been updated and cleaned.")

if __name__ == "__main__":
    main()
