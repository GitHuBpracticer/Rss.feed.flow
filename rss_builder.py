import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. FLUX GEO HISTOIRE
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
        print("✓ Flux GEO Histoire généré avec succès.")
    except Exception as e:
        print(f"Erreur GEO Histoire: {e}")

# 2. FLUX PERMACULTURE (Permathèque)
def build_permathaque_rss():
    url = "https://permathaque.fr"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        fg = FeedGenerator()
        fg.title("Permathèque - Potager & Permaculture")
        fg.link(href=url, rel="alternate")
        fg.description("Guides et fiches pratiques de la Permathèque")
        fg.language("fr")

        seen_links = set()
        for a_tag in soup.find_all("a", href=True):
            title = a_tag.get_text(strip=True)
            href = a_tag["href"]

            if len(title) > 10 and ("/" in href):
                full_url = href if href.startswith("http") else f"https://permathaque.fr{href}"
                if full_url not in seen_links and "-" in href:
                    seen_links.add(full_url)
                    fe = fg.add_entry()
                    fe.title(title)
                    fe.link(href=full_url)
                    fe.id(full_url)

        fg.rss_file("permathaque.xml", pretty=True)
        print("✓ Flux Permathèque généré avec succès.")
    except Exception as e:
        print(f"Erreur Permathèque: {e}")

# 3. FLUX WEB3 & AIRDROPS
def build_web3_rss():
    url = "https://coinacademy.fr/crypto-airdrops/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        fg = FeedGenerator()
        fg.title("Web3 & Airdrops")
        fg.link(href=url, rel="alternate")
        fg.description("Opportunités et guides Airdrops Web3")
        fg.language("fr")

        seen_links = set()
        for a_tag in soup.find_all("a", href=True):
            title = a_tag.get_text(strip=True)
            href = a_tag["href"]

            if len(title) > 15 and "airdrop" in href.lower():
                full_url = href if href.startswith("http") else f"https://coinacademy.fr{href}"
                if full_url not in seen_links:
                    seen_links.add(full_url)
                    fe = fg.add_entry()
                    fe.title(title)
                    fe.link(href=full_url)
                    fe.id(full_url)

        fg.rss_file("web3_airdrops.xml", pretty=True)
        print("✓ Flux Web3/Airdrops généré avec succès.")
    except Exception as e:
        print(f"Erreur Web3: {e}")

# 4. FLUX MÉTÉO CÔTE-D'OR
def build_meteo_rss():
    url = "https://www.meteo-express.com/previsions/cote-dor"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        fg = FeedGenerator()
        fg.title("Météo - Côte-d'Or (21)")
        fg.link(href=url, rel="alternate")
        fg.description("Previsions et alertes météo pour la Côte-d'Or")
        fg.language("fr")

        seen_links = set()
        for a_tag in soup.find_all("a", href=True):
            title = a_tag.get_text(strip=True)
            href = a_tag["href"]

            if len(title) > 12 and ("cote-dor" in href.lower() or "bourgogne" in href.lower() or "alerte" in href.lower()):
                full_url = href if href.startswith("http") else f"https://www.meteo-express.com{href}"
                if full_url not in seen_links:
                    seen_links.add(full_url)
                    fe = fg.add_entry()
                    fe.title(title)
                    fe.link(href=full_url)
                    fe.id(full_url)

        fg.rss_file("meteo_cote_dor.xml", pretty=True)
        print("✓ Flux Météo Côte-d'Or généré avec succès.")
    except Exception as e:
        print(f"Erreur Météo: {e}")

# 5. FLUX TECH DIY & IA LOCALE
def build_tech_diy_rss():
    url = "https://www.lesnumeriques.com/intelligence-artificielle.html"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        fg = FeedGenerator()
        fg.title("Tech DIY, IA Locale & Open Source")
        fg.link(href=url, rel="alternate")
        fg.description("Actualités IA autonome et modèles locaux")
        fg.language("fr")

        seen_links = set()
        for a_tag in soup.find_all("a", href=True):
            title = a_tag.get_text(strip=True)
            href = a_tag["href"]

            if len(title) > 15 and ("/ia-" in href.lower() or "/intelligence-artificielle/" in href.lower()):
                full_url = href if href.startswith("http") else f"https://www.lesnumeriques.com{href}"
                if full_url not in seen_links:
                    seen_links.add(full_url)
                    fe = fg.add_entry()
                    fe.title(title)
                    fe.link(href=full_url)
                    fe.id(full_url)

        fg.rss_file("tech_ia.xml", pretty=True)
        print("✓ Flux Tech/IA généré avec succès.")
    except Exception as e:
        print(f"Erreur Tech/IA: {e}")

if __name__ == "__main__":
    build_geo_rss()
    build_permathaque_rss()
    build_web3_rss()
    build_meteo_rss()
    build_tech_diy_rss()
