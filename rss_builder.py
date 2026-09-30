import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def create_fallback_entry(fg, site_name, site_url):
    fe = fg.add_entry()
    fe.title(f"Information - {site_name}")
    fe.link(href=site_url)
    fe.id(site_url)
    fe.description("Flux opérationnel. Aucun nouvel article extrait lors du dernier scan.")

# 1. GEO HISTOIRE (AVEC FILTRE ANTI-PUB / ANTI-ABONNEMENT)
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
            
            # Exclusion des mots-clés liés aux abonnements et menus annexes
            ignored = [
                "charte", "auteurs", "équipe", "consentement", "accessibilité", 
                "mentions", "contact", "cookies", "abonner", "abonnement", 
                "offre", "boutique", "kiosque", "magazine"
            ]

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                # On vérifie que le titre ne contient AUCUN mot indésirable
                if len(title) >= 15 and not any(bad in title.lower() or bad in href.lower() for bad in ignored):
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

# 2. PERMATHÈQUE (URL CORRIGÉE : permatheque.fr)
def build_permatheque_rss():
    url = "https://permatheque.fr"
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
                    full_url = href if href.startswith("http") else f"https://permatheque.fr{href}"
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

    fg.rss_file("permatheque.xml", pretty=True)
    print("✓ permatheque.xml généré.")

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

# 4A. MÉTÉO NATIONALE
def build_meteo_nationale_rss():
    url = "https://www.meteo-express.com"
    fg = FeedGenerator()
    fg.title("Météo Express - France")
    fg.link(href=url, rel="alternate")
    fg.description("Prévisions et alertes météo au niveau national")
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
        print(f"Erreur Météo Nationale: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Météo Express France", url)

    fg.rss_file("meteo_france.xml", pretty=True)
    print("✓ meteo_france.xml généré.")

# 4B. MÉTÉO RÉGIONALE (Bourgogne / Côte-d'Or)
def build_meteo_regionale_rss():
    url = "https://www.meteo-express.com"
    fg = FeedGenerator()
    fg.title("Météo - Bourgogne & Côte-d'Or")
    fg.link(href=url, rel="alternate")
    fg.description("Actualités et alertes météo ciblées Bourgogne / Côte-d'Or (21)")
    fg.language("fr")

    keywords = ["bourgogne", "côte-d'or", "cote-d'or", "21", "dijon", "est", "centre-est"]
    entries_count = 0

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                text_to_check = f"{title} {href}".lower()
                if len(title) > 8 and any(kw in text_to_check for kw in keywords):
                    full_url = href if href.startswith("http") else f"https://www.meteo-express.com{href}"
                    if full_url not in seen_links:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[Région] {title}")
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Météo Régionale: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Météo Bourgogne / Côte-d'Or", url)

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

# 6. VITRINE HTML
def build_index_html():
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rss.feed.flow - Flux RSS Automatisés</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 15px; background: #f4f6f8; color: #1a1a1a; line-height: 1.5; }
        .container { max-width: 680px; margin: 0 auto; background: #fff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { margin-top: 0; color: #0969da; font-size: 1.6rem; border-bottom: 2px solid #eaeef2; padding-bottom: 10px; }
        h2 { font-size: 1.1rem; color: #24292f; margin-top: 20px; }
        p { color: #57606a; font-size: 0.92rem; margin-bottom: 12px; }
        .intro-box { background: #f6f8fa; border-left: 4px solid #0969da; padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; }
        ul { list-style: none; padding: 0; margin: 15px 0; }
        li { margin-bottom: 12px; padding: 14px; background: #ffffff; border-radius: 8px; border: 1px solid #d0d7de; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .title { font-weight: 600; font-size: 0.95rem; color: #1f2328; }
        .btn { background: #0969da; color: white; padding: 7px 14px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 500; display: inline-block; }
        .btn:hover { background: #0451a5; }
        .footer { margin-top: 25px; text-align: center; font-size: 0.8rem; color: #8c959f; border-top: 1px solid #eaeef2; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 Rss.feed.flow</h1>
        
        <div class="intro-box">
            <p><strong>À propos du projet :</strong> Ce service génère automatiquement des flux RSS personnalisés à partir de sites web ne proposant pas de flux natif. Il s'exécute de manière autonome via GitHub Actions.</p>
            <p style="margin-bottom:0;">💡 <strong>Utilisation :</strong> Cliquez sur <em>« Ouvrir le flux »</em> pour consulter le XML brut, ou copiez l'adresse du lien pour l'ajouter directement dans votre lecteur RSS (ex: <em>Read You</em>, <em>Feeder</em>).</p>
        </div>

        <h2>📂 Flux RSS disponibles :</h2>
        <ul>
            <li>
                <span class="title">📜 GEO Histoire</span>
                <a class="btn" href="geo_histoire.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">🌱 Permaculture (Permathèque)</span>
                <a class="btn" href="permatheque.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">💎 Web3 & Airdrops</span>
                <a class="btn" href="web3_airdrops.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">🇫🇷 Météo Express (France entière)</span>
                <a class="btn" href="meteo_france.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">🌤️ Météo Régionale (Bourgogne / Côte-d'Or)</span>
                <a class="btn" href="meteo_cote_dor.xml" target="_blank">Ouvrir le flux</a>
            </li>
            <li>
                <span class="title">🤖 Tech DIY & IA Locale</span>
                <a class="btn" href="tech_ia.xml" target="_blank">Ouvrir le flux</a>
            </li>
        </ul>

        <div class="footer">
            Généré automatiquement via Python & GitHub Pages
        </div>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✓ index.html généré.")

if __name__ == "__main__":
    build_geo_rss()
    build_permatheque_rss()
    build_web3_rss()
    build_meteo_nationale_rss()
    build_meteo_regionale_rss()
    build_tech_diy_rss()
    build_index_html()
