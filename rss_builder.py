import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. MOTS-CLÉS DE NAVIGATION GLOBAUX (Bruit présent sur presque tous les sites)
GLOBAL_IGNORED = [
    "contact", "mentions", "politique", "cookies", "facebook", 
    "instagram", "twitter", "connexion", "connecter", "propos", 
    "accueil", "charte", "auteurs", "équipe", "accessibilité"
]

# 2. FONCTION DE FILTRAGE CENTRALISÉE
def is_valid_link(title, href, min_length=12, specific_ignored=None):
    if specific_ignored is None:
        specific_ignored = []
    
    all_ignored = GLOBAL_IGNORED + specific_ignored
    text_to_check = f"{title} {href}".lower()

    if len(title) < min_length:
        return False
    if any(bad in text_to_check for bad in all_ignored):
        return False
    return True

def create_fallback_entry(fg, site_name, site_url):
    fe = fg.add_entry()
    fe.title(f"Information - {site_name}")
    fe.link(href=site_url)
    fe.id(site_url)
    fe.description("Flux opérationnel. Aucun nouvel article extrait lors du dernier scan.")

# -------------------------------------------------------------------
# 1. GEO HISTOIRE
# -------------------------------------------------------------------
def build_geo_rss():
    url = "https://www.geo.fr/histoire"
    fg = FeedGenerator()
    fg.title("GEO.fr - Histoire")
    fg.link(href=url, rel="alternate")
    fg.description("Flux RSS généré automatiquement pour GEO Histoire")
    fg.language("fr")
    
    geo_ignored = ["abonner", "abonnement", "offre", "boutique", "kiosque", "magazine"]
    entries_count = 0

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                if is_valid_link(title, href, min_length=15, specific_ignored=geo_ignored):
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

# -------------------------------------------------------------------
# 2. PERMATHÈQUE
# -------------------------------------------------------------------
def build_permatheque_rss():
    url = "https://permatheque.fr"
    fg = FeedGenerator()
    fg.title("Permathèque - Potager & Permaculture")
    fg.link(href=url, rel="alternate")
    fg.description("Guides et fiches pratiques de la Permathèque")
    fg.language("fr")

    perma_ignored = ["soutenir", "événement", "annonce", "publier", "association", "pépinière", "don"]
    entries_count = 0

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]

                if is_valid_link(title, href, min_length=12, specific_ignored=perma_ignored):
                    full_url = href if href.startswith("http") else f"https://permatheque.fr{href}"
                    if full_url not in seen_links and full_url != "https://permatheque.fr/":
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

# -------------------------------------------------------------------
# 3. WEB3 & AIRDROPS (Cryptoast + CoinAcademy)
# -------------------------------------------------------------------
def build_web3_rss():
    fg = FeedGenerator()
    fg.title("Web3 & Airdrops Multi-sources")
    fg.link(href="https://cryptoast.fr/actu/airdrop/", rel="alternate")
    fg.description("Guides, opportunités et actualités Airdrops Web3")
    fg.language("fr")

    entries_count = 0
    seen_links = set()

    # Source 1 : Cryptoast Airdrops
    try:
        url_cryptoast = "https://cryptoast.fr/actu/airdrop/"
        res = requests.get(url_cryptoast, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=15) and "airdrop" in href.lower():
                    if href.startswith("https://cryptoast.fr") and href not in seen_links:
                        seen_links.add(href)
                        fe = fg.add_entry()
                        fe.title(f"[Cryptoast] {title}")
                        fe.link(href=href)
                        fe.id(href)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Web3 Cryptoast: {e}")

    # Source 2 : CoinAcademy Airdrops
    try:
        url_coinacademy = "https://coinacademy.fr/crypto-airdrops/"
        res = requests.get(url_coinacademy, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=15) and ("airdrop" in href.lower() or "guide" in href.lower()):
                    full_url = href if href.startswith("http") else f"https://coinacademy.fr{href}"
                    if full_url not in seen_links:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[CoinAcademy] {title}")
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Web3 CoinAcademy: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Web3 Airdrops", "https://cryptoast.fr/actu/airdrop/")

    fg.rss_file("web3_airdrops.xml", pretty=True)
    print("✓ web3_airdrops.xml généré.")

# -------------------------------------------------------------------
# 4A. MÉTÉO NATIONALE
# -------------------------------------------------------------------
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

                if is_valid_link(title, href, min_length=10):
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

# -------------------------------------------------------------------
# 4B. MÉTÉO RÉGIONALE (Bourgogne / Côte-d'Or)
# -------------------------------------------------------------------
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
                if is_valid_link(title, href, min_length=8) and any(kw in text_to_check for kw in keywords):
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

# -------------------------------------------------------------------
# 5. TECH DIY, AGENTS IA & AUTOMATISATION
# -------------------------------------------------------------------
def build_tech_diy_rss():
    fg = FeedGenerator()
    fg.title("Tech DIY, Agents IA & Automatisation")
    fg.link(href="https://www.ecole.cube.fr/blog", rel="alternate")
    fg.description("Tutoriels et actualités sur les agents IA, le no-code et l'automatisation")
    fg.language("fr")

    entries_count = 0
    seen_links = set()

    # Source 1 : Les Numériques - IA
    try:
        url_num = "https://www.lesnumeriques.com/intelligence-artificielle.html"
        res = requests.get(url_num, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=15) and ("/ia-" in href.lower() or "/intelligence-artificielle/" in href.lower()):
                    full_url = href if href.startswith("http") else f"https://www.lesnumeriques.com{href}"
                    if full_url not in seen_links:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[Les Numériques] {title}")
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Tech Numériques: {e}")

    # Source 2 : École Cube - Blog Agents IA & Automatisation
    try:
        url_cube = "https://www.ecole.cube.fr/blog"
        res = requests.get(url_cube, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = a_tag.get_text(strip=True)
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=12) and ("/blog/" in href.lower()):
                    full_url = href if href.startswith("http") else f"https://www.ecole.cube.fr{href}"
                    if full_url not in seen_links and full_url != "https://www.ecole.cube.fr/blog":
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[Tuto IA/Auto] {title}")
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Tech Cube: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Tech IA & Agents", "https://www.ecole.cube.fr/blog")

    fg.rss_file("tech_ia.xml", pretty=True)
    print("✓ tech_ia.xml généré.")

# -------------------------------------------------------------------
# 6. PAGE INDEX HTML
# -------------------------------------------------------------------
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
                <span class="title">🤖 Tech DIY, Agents IA & Automatisation</span>
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
    
