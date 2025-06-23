import asyncio
import json
from pyppeteer import launch
from crawler import crawl, results
import time

START_URL = "https:Example.com/"
MAX_PAGES = 100

async def main():
    start = time.time()
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()

    await crawl(page, START_URL, max_pages=MAX_PAGES)

    await browser.close()

    with open("accessibility_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    end = time.time()
    elapsed = (end - start)/60  
    print(f"Accessibility scan completed in {elapsed:.2f} minutes.")

    print(f"\nFinished. {len(results)} pages scanned.")
    print("Report saved to accessibility_report.json")

if __name__ == "__main__":
    asyncio.run(main())
