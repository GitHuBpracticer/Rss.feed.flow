import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def create_fallback_entry(fg, site_name, site_url):
    """Ajoute un article de sécurité si le scraping n'a rien renvoyé pour éviter l'erreur 404."""
    fe = fg.add_entry()
    fe.title(f"Information - {site_name}")
    fe.link(href=site_url)
    fe.id(site_url)
    fe.description("Flux opérationnel. Aucun nouvel article extrait lors de la dernière mise à jour.")

# 1. GEO HISTOIRE
def build_geo_rss():
    url = "https://www.geo.fr/histoire"
    fg = FeedGenerator()
    fg.title("GEO.fr - Histoire")
    fg.link(href=url, rel="alternate")
    fg.description("Flux RSS généré automatiquement pour GEO Histoire")
    fg.language("fr")
    
    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()
            ignored = ["charte", "auteurs", "équipe", "consentement", "accessibilité", "mentions", "contact", "cookies"]

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                if len(title) >= 15 and not any(bad in title.lower() for bad in ignored):
                    full_url = f"https://www.geo.fr{href}" if href.startswith("/") else href
                    if full_url.startswith("https://www.geo.fr") and "-" in href and full_url not in seen_links:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur GEO: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "GEO Histoire", url)

    fg.rss_file("geo_histoire.xml", pretty=True)
    print("✓ geo_histoire.xml généré.")

# 2. PERMATHÈQUE
def build_permathaque_rss():
    url = "https://permathaque.fr"
    fg = FeedGenerator()
    fg.title("Permathèque - Potager & Permaculture")
    fg.link(href=url, rel="alternate")
    fg.description("Guides et fiches pratiques de la Permathèque")
    fg.language("fr")

    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                if len(title) > 10:
                    full_url = href if href.startswith("http") else f"https://permathaque.fr{href}"
                    if full_url not in seen_links and ("/" in href):
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Permathèque: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Permathèque", url)

    fg.rss_file("permathaque.xml", pretty=True)
    print("✓ permathaque.xml généré.")

# 3. WEB3 & AIRDROPS
def build_web3_rss():
    url = "https://coinacademy.fr/crypto-airdrops/"
    fg = FeedGenerator()
    fg.title("Web3 & Airdrops")
    fg.link(href=url, rel="alternate")
    fg.description("Opportunités et guides Airdrops Web3")
    fg.language("fr")

    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                if len(title) > 12:
                    full_url = href if href.startswith("http") else f"https://coinacademy.fr{href}"
                    if full_url not in seen_links and ("airdrop" in href.lower() or "crypto" in href.lower()):
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Web3: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Web3 Airdrops", url)

    fg.rss_file("web3_airdrops.xml", pretty=True)
    print("✓ web3_airdrops.xml généré.")

# 4. MÉTÉO CÔTE-D'OR
def build_meteo_rss():
    url = "https://www.meteo-express.com"
    fg = FeedGenerator()
    fg.title("Météo - Côte-d'Or (21)")
    fg.link(href=url, rel="alternate")
    fg.description("Prévisions et alertes météo")
    fg.language("fr")

    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                if len(title) > 10:
                    full_url = href if href.startswith("http") else f"https://www.meteo-express.com{href}"
                    if full_url not in seen_links:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Météo: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Météo Express", url)

    fg.rss_file("meteo_cote_dor.xml", pretty=True)
    print("✓ meteo_cote_dor.xml généré.")

# 5. TECH DIY & IA LOCALE
def build_tech_diy_rss():
    url = "https://www.lesnumeriques.com/intelligence-artificielle.html"
    fg = FeedGenerator()
    fg.title("Tech DIY, IA Locale & Open Source")
    fg.link(href=url, rel="alternate")
    fg.description("Actualités IA autonome et modèles locaux")
    fg.language("fr")

    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
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
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Tech/IA: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Tech IA", url)

    fg.rss_file("tech_ia.xml", pretty=True)
    print("✓ tech_ia.xml généré.")

# 6. GÉNÉRATION DE INDEX.HTML
def build_index_html():
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rss.feed.flow - Annuaire de flux RSS</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f4f6f8; color: #1a1a1a; }
        .container { max-width: 650px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { margin-top: 0; color: #0969da; font-size: 1.5rem; }
        p { color: #57606a; font-size: 0.95rem; }
        ul { list-style: none; padding: 0; margin: 20px 0; }
        li { margin-bottom: 12px; padding: 12px; background: #f6f8fa; border-radius: 8px; border: 1px solid #d0d7de; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
        .title { font-weight: 600; font-size: 0.95rem; }
        .btn { background: #0969da; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 500; }
        .btn:hover { background: #0451a5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 Rss.feed.flow</h1>
        <p>Annuaire de flux RSS personnalisés mis à jour automatiquement.</p>
        <ul>
            <li>
                <span class="title">📜 GEO Histoire</span>
                <a class="btn" href="geo_histoire.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">🌱 Permaculture (Permathèque)</span>
                <a class="btn" href="permathaque.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">💎 Web3 & Airdrops</span>
                <a class="btn" href="web3_airdrops.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">🌤️ Météo Côte-d'Or (21)</span>
                <a class="btn" href="meteo_cote_dor.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">🤖 Tech DIY & IA Locale</span>
                <a class="btn" href="tech_ia.xml" target="_blank">Ouvrir le flux</a>
            </li>
        </ul>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✓ index.html généré.")

if __name__ == "__main__":
    build_geo_rss()
    build_permathaque_rss()
    build_web3_rss()
    build_meteo_rss()
    build_tech_diy_rss()
    build_index_html()
