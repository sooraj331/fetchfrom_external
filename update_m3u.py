import asyncio
from playwright.async_api import async_playwright

async def get_m3u():
    async with async_playwright() as p:
        # Launch a real browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print("Opening website with real browser...")
            await page.goto("https://freeiptv2023-d.ottc.xyz/index.php?action=view", wait_until="networkidle", timeout=60000)
            
            # Wait specifically for the input box to appear
            print("Waiting for the link to load...")
            await page.wait_for_selector("#m3uLink", timeout=15000)
            
            # Get the value
            m3u_url = await page.get_attribute("#m3uLink", "value")
            
            if m3u_url:
                print(f"Success! Found URL: {m3u_url}")
                # Download the content
                response = await page.request.get(m3u_url)
                content = await response.body()
                
                with open("playlist.m3u", "wb") as f:
                    f.write(content)
                print("File saved successfully.")
            else:
                print("Found input but it was empty.")

        except Exception as e:
            print(f"Browser error: {e}")
            # Take a screenshot if it fails so you can see why
            await page.screenshot(path="error_debug.png")
            exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(get_m3u())
