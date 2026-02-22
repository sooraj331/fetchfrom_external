import asyncio
from playwright.async_api import async_playwright
import sys

async def get_m3u():
    async with async_playwright() as p:
        # Launch browser with a specific window size to look like a desktop
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print("Navigating to website...")
            # We use 'domcontentloaded' instead of 'networkidle' to avoid timing out on slow background scripts
            await page.goto("https://freeiptv2023-d.ottc.xyz/index.php?action=view", 
                            wait_until="domcontentloaded", 
                            timeout=90000)
            
            print("Waiting for the M3U link element...")
            # Wait for the specific ID to appear in the HTML
            selector = "input#m3uLink"
            await page.wait_for_selector(selector, state="attached", timeout=30000)
            
            m3u_url = await page.get_attribute(selector, "value")
            
            if m3u_url:
                print(f"Found URL: {m3u_url}")
                # Use the browser's internal context to download to bypass protection
                response = await page.goto(m3u_url)
                content = await response.body()
                
                with open("playlist.m3u", "wb") as f:
                    f.write(content)
                print("Success: playlist.m3u saved.")
            else:
                print("Error: Link found but value is empty.")
                sys.exit(1)

        except Exception as e:
            print(f"Failed: {e}")
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(get_m3u())
