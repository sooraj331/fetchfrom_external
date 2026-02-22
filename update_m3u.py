from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

URL = "https://freeiptv2023-d.ottc.xyz/index.php?action=view"

def get_m3u_link():
    options = Options()
    options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)

        wait = WebDriverWait(driver, 20)
        element = wait.until(
            EC.presence_of_element_located((By.ID, "m3uLink"))
        )

        return element.get_attribute("value")

    finally:
        driver.quit()

def download_m3u(m3u_url):
    response = requests.get(m3u_url, timeout=30)
    response.raise_for_status()

    with open("index.m3u", "w", encoding="utf-8") as f:
        f.write(response.text)

if __name__ == "__main__":
    link = get_m3u_link()
    print("Found:", link)
    download_m3u(link)
