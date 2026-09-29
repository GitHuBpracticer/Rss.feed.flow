import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

def build_geo_rss():
    url = "https://www.geo.fr/histoire"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    fg = FeedGenerator()
    fg.title("GEO.fr - Histoire")
    fg.link(href=url, rel="alternate")
    fg.description("Flux RSS généré automatiquement via GitHub Actions")
    fg.language("fr")

    seen_links = set()

    for a_tag in soup.find_all("a", href=True):
        title = a_tag.get_text(strip=True)
        href = a_tag["href"]

        if title and len(title) > 20 and href.startswith("/"):
            full_url = f"https://www.geo.fr{href}"

            if full_url not in seen_links:
                seen_links.add(full_url)

                parent = a_tag.find_parent(["article", "div"])
                desc = ""
                if parent:
                    p_tag = parent.find("p")
                    if p_tag:
                        desc = p_tag.get_text(strip=True)

                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=full_url)
                fe.id(full_url)
                fe.description(desc if desc else title)

    fg.rss_file("geo_histoire.xml", pretty=True)

if __name__ == "__main__":
    build_geo_rss()
  
