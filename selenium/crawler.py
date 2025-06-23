from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from axe_selenium_python import Axe
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

visited = set()
results = []
max_pages = 100

def normalize_url(url):
    parsed = urlparse(url)
    parsed = parsed._replace(fragment='', query='')
    clean_url = parsed.geturl()
    if clean_url.endswith('/') and parsed.path != '/':
        clean_url = clean_url[:-1]
    return clean_url

def get_internal_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    domain = urlparse(base_url).netloc
    internal_links = set()

    for a in soup.find_all("a", href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        normalized_url = normalize_url(full_url)
        parsed = urlparse(normalized_url)

        if parsed.netloc == domain and parsed.scheme in ("http", "https"):
            internal_links.add(normalized_url)
    return internal_links

def run_accessibility_test(driver, url):
    axe = Axe(driver)
    axe.inject()
    result = axe.run()

    summary = {
        "url": url,
        "summary": {
            "violationsFound": len(result["violations"]),
            "passes": len(result["passes"]),
            "incomplete": len(result["incomplete"]),
            "inapplicable": len(result["inapplicable"]),
            "score": round(
                len(result["passes"]) / max(
                    len(result["passes"]) + len(result["violations"]) + len(result["incomplete"]), 1
                ) * 100
            )
        },
        "violations": result["violations"],
        "passes": result["passes"],
        "incomplete": result["incomplete"],
        "inapplicable": result["inapplicable"]
    }
    results.append(summary)
    print(f"Scanned: {url} - Violations: {len(result['violations'])}")

def crawl(driver, url, max_pages=max_pages):
    if len(visited) >= max_pages:
        return

    normalized = normalize_url(url)
    if normalized in visited:
        return

    visited.add(normalized)
    try:
        driver.get(normalized)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        run_accessibility_test(driver, normalized)

        internal_links = get_internal_links(driver.page_source, normalized)

        for link in internal_links:
            if link not in visited:
                crawl(driver, link, max_pages=max_pages)

    except Exception as e:
        print(f"Failed to crawl {url}: {e}")
