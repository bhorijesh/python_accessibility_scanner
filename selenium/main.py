from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
from crawler import crawl, results

START_URL = "https://Example.com/"
MAX_PAGES = 100

def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        crawl(driver, START_URL, max_pages=MAX_PAGES)

        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\nCrawling finished: {len(results)} pages scanned.")
        print("Report saved to accessibility_report.json")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
