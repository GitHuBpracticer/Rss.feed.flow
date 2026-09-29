import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

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
    fg.description("Flux RSS généré automatiquement pour GEO Histoire")
    fg.language("fr")

    seen_links = set()
    ignored_texts = ["prochaine page", "dernière page", "page précédente", "voir plus", "accueil"]

    for a_tag in soup.find_all("a", href=True):
        title = a_tag.get_text(strip=True)
        href = a_tag["href"]

        # Doit avoir un titre correct
        if not title or len(title) < 5:
            continue

        # Exclure la navigation
        if any(bad in title.lower() for bad in ignored_texts):
            continue

        # Construire l'URL complète
        if href.startswith("/"):
            full_url = f"https://www.geo.fr{href}"
        elif href.startswith("https://www.geo.fr"):
            full_url = href
        else:
            continue

        # Garder uniquement les liens vers des articles/rubriques
        if full_url not in seen_links:
            seen_links.add(full_url)

            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=full_url)
            fe.id(full_url)
            fe.description(title)

    fg.rss_file("geo_histoire.xml", pretty=True)

if __name__ == "__main__":
    build_geo_rss()
