from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited = set()
results = []

def normalize_url(url):
    parsed = urlparse(url)
    parsed = parsed._replace(fragment='', query='')
    clean_url = parsed.geturl()
    if clean_url.endswith('/') and parsed.path != '/':
        clean_url = clean_url[:-1]
    return clean_url

def get_internal_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(base_url).netloc
    internal_links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        normalized_url = normalize_url(full_url)
        if urlparse(normalized_url).netloc == domain:
            internal_links.add(normalized_url)
    return internal_links

async def inject_axe_and_run(page, url):
    try:
        await page.addScriptTag(path="./axe.min.js")

        result = await page.evaluate("""
            async () => {
                return await axe.run(document, {
                    runOnly: {
                        type: 'tag',
                        values: [
                            'wcag2a',
                            'wcag2aa',
                            'wcag2aaa',
                            'wcag21a',
                            'wcag21aa',
                            'wcag22aa',
                            'best-practice',
                            'wcag2a-obsolete',
                            'ACT',
                            'section508',
                            'section508.*.*',
                            'TTv5',
                            'TT*.*',
                            'EN-301-549',
                            'EN-9.*',
                            'experimental',
                            'cat.*',
                            'wcag***'
                        ]
                    }
                });
            }
        """)

        summary = {
            "url": url,
            "summary": {
                "violationsFound": len(result["violations"]),
                "incomplete": len(result["incomplete"]),
                "inapplicable": len(result["inapplicable"]),
                "score": round(100 - (len(result["violations"]) / max(1, (len(result["violations"]) + len(result["incomplete"]))) * 100))
            },
            "violations": result["violations"],
            "passes": result["passes"],
            "incomplete": result["incomplete"],
            "inapplicable": result["inapplicable"]
        }

        results.append(summary)
        print(f"Scanned: {url} - Violations: {len(result['violations'])}")
    except Exception as e:
        print(f"Error running axe on {url}: {e}")

async def crawl(page, url, max_pages=50):
    if len(visited) >= max_pages:
        return

    normalized = normalize_url(url)
    if normalized in visited:
        return

    visited.add(normalized)

    try:
        response = await page.goto(normalized, {'waitUntil': 'domcontentloaded'})
        if not response or not response.ok:
            print(f"Failed to load {url}")
            return

        await inject_axe_and_run(page, normalized)

        html = await page.content()
        links = get_internal_links(html, normalized)

        for link in links:
            if link not in visited:
                await crawl(page, link, max_pages)

    except Exception as e:
        print(f"Error crawling {url}: {e}")
