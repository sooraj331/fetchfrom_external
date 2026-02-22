import requests
from bs4 import BeautifulSoup
import base64
import os

# 1️⃣ Fetch webpage
page_url = "https://freeiptv2023-d.ottc.xyz/index.php?action=view"
r = requests.get(page_url)
soup = BeautifulSoup(r.text, "html.parser")

# 2️⃣ Extract M3U link
m3u_input = soup.find("input", {"id": "m3uLink"})
m3u_url = m3u_input["value"]

print("Found M3U:", m3u_url)

# 3️⃣ Download M3U content
m3u_content = requests.get(m3u_url).text

# 4️⃣ Save locally
with open("index.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)

print("M3U updated successfully.")
