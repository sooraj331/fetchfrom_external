from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time

URL = "https://freeiptv2023-d.ottc.xyz/index.php?action=view"

def get_m3u_link():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(URL)

        # Wait until input field loads
        wait = WebDriverWait(driver, 20)
        element = wait.until(
            EC.presence_of_element_located((By.ID, "m3uLink"))
        )

        m3u_url = element.get_attribute("value")
        print("M3U URL Found:", m3u_url)

        return m3u_url

    finally:
        driver.quit()


def download_m3u(m3u_url):
    response = requests.get(m3u_url, timeout=30)
    response.raise_for_status()

    with open("index.m3u", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("M3U file saved successfully.")


if __name__ == "__main__":
    link = get_m3u_link()
    download_m3u(link)
