import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def build_geo_rss():
    url = "https://www.geo.fr/histoire"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        fg = FeedGenerator()
        fg.title("GEO.fr - Histoire")
        fg.link(href=url, rel="alternate")
        fg.description("Flux RSS généré automatiquement pour GEO Histoire")
        fg.language("fr")

        seen_links = set()
        ignored_keywords = [
            "charte", "auteurs", "équipe", "equipe", "consentement", 
            "accessibilité", "accessibilite", "mentions", "contact", 
            "cookies", "cgv", "cgu", "savoir plus", "suivez-nous"
        ]

        for a_tag in soup.find_all("a", href=True):
            title = a_tag.get_text(strip=True)
            href = a_tag["href"]

            if not title or len(title) < 15:
                continue

            if any(bad in title.lower() for bad in ignored_keywords):
                continue

            if href.startswith("/"):
                full_url = f"https://www.geo.fr{href}"
            elif href.startswith("https://www.geo.fr"):
                full_url = href
            else:
                continue

            if "-" in href and full_url not in seen_links:
                seen_links.add(full_url)

                fe = fg.add_entry()
                fe.title(title)
                fe.link(href=full_url)
                fe.id(full_url)
                fe.description(title)

        fg.rss_file("geo_histoire.xml", pretty=True)
        print("✓ Flux GEO Histoire nettoyé et généré avec succès.")
    except Exception as e:
        print(f"Erreur GEO Histoire: {e}")

if __name__ == "__main__":
    build_geo_rss()
