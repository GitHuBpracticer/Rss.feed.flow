import re
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. MOTS-CLÉS DE NAVIGATION GLOBAUX (Bruit commun)
GLOBAL_IGNORED = [
    "contact", "mentions", "politique", "cookies", "facebook", 
    "instagram", "twitter", "connexion", "connecter", "propos", 
    "accueil", "charte", "auteurs", "équipe", "accessibilité"
]

# 2. FONCTIONS DE NETTOYAGE
def clean_title(raw_title):
    # Supprime la durée de lecture parasite (ex: "6 minmin de lecture", "7 minutesmin de lecture")
    cleaned = re.sub(r'\d+\s*(min|minutes)?\s*min\s*de\s*lecture', '', raw_title, flags=re.IGNORECASE)
    # Supprime les préfixes parasites répétitifs si présents dans les balises
    cleaned = re.sub(r'^(GEO\s*:|IA\s*:)', '', cleaned, flags=re.IGNORECASE)
    # Nettoyage des espaces multiples
    return " ".join(cleaned.split()).strip()

def is_valid_link(title, href, min_length=8, specific_ignored=None):
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
    fg.description("Flux RSS généré pour GEO Histoire")
    fg.language("fr")
    fg.icon("https://www.geo.fr/favicon.ico")

    geo_ignored = ["abonner", "abonnement", "offre", "boutique", "kiosque", "magazine"]
    entries_count = 0

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
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
# 2. PERMATHÈQUE (Filtre assoupli)
# -------------------------------------------------------------------
def build_permatheque_rss():
    url = "https://permatheque.fr"
    fg = FeedGenerator()
    fg.title("Permathèque - Potager & Permaculture")
    fg.link(href=url, rel="alternate")
    fg.description("Guides et fiches pratiques de la Permathèque")
    fg.language("fr")
    fg.icon("https://permatheque.fr/favicon.ico")

    # Uniquement des exclusions de bruit, aucun mot-clé obligatoire
    perma_ignored = ["soutenir", "événement", "annonce", "publier", "association", "pépinière", "don", "connexion"]
    entries_count = 0

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]

                if is_valid_link(title, href, min_length=8, specific_ignored=perma_ignored):
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
# 3. WEB3 & AIRDROPS
# -------------------------------------------------------------------
def build_web3_rss():
    fg = FeedGenerator()
    fg.title("Web3 & Airdrops Multi-sources")
    fg.link(href="https://cryptoast.fr/actu/airdrop/", rel="alternate")
    fg.description("Guides, opportunités et actualités Airdrops Web3")
    fg.language("fr")
    fg.icon("https://cryptoast.fr/favicon.ico")

    entries_count = 0
    seen_links = set()

    try:
        url_cryptoast = "https://cryptoast.fr/actu/airdrop/"
        res = requests.get(url_cryptoast, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=12) and "airdrop" in href.lower():
                    if href.startswith("https://cryptoast.fr") and href not in seen_links:
                        seen_links.add(href)
                        fe = fg.add_entry()
                        fe.title(f"[Cryptoast] {title}")
                        fe.link(href=href)
                        fe.id(href)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Web3 Cryptoast: {e}")

    try:
        url_coinacademy = "https://coinacademy.fr/crypto-airdrops/"
        res = requests.get(url_coinacademy, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=12) and ("airdrop" in href.lower() or "guide" in href.lower()):
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
    fg.description("Prévisions et alertes météo nationales")
    fg.language("fr")
    fg.icon("https://www.meteo-express.com/favicon.ico")

    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]

                if is_valid_link(title, href, min_length=10):
                    full_url = href if href.startswith("http") else f"https://www.meteo-express.com{href}"
                    if full_url not in seen_links:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[France] {title}")
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
    fg.description("Actualités météo Bourgogne / Côte-d'Or (21)")
    fg.language("fr")
    fg.icon("https://www.meteo-express.com/favicon.ico")

    keywords = ["bourgogne", "côte-d'or", "cote-d'or", "21", "dijon", "est", "centre-est"]
    entries_count = 0

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
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
# 5. TECH DIY, AGENTS IA & AUTOMATISATION (Avec Regex pour titres propres)
# -------------------------------------------------------------------
def build_tech_diy_rss():
    fg = FeedGenerator()
    fg.title("Tech DIY, IA Locale & Open Source")
    fg.link(href="https://www.ecole.cube.fr/blog", rel="alternate")
    fg.description("Tutoriels et actualités sur les agents IA et l'automatisation")
    fg.language("fr")
    fg.icon("https://www.lesnumeriques.com/favicon.ico")

    entries_count = 0
    seen_links = set()

    # Source 1 : Les Numériques - IA
    try:
        url_num = "https://www.lesnumeriques.com/intelligence-artificielle.html"
        res = requests.get(url_num, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
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

    # Source 2 : École Cube - Blog (avec nettoyage des durées de lecture)
    try:
        url_cube = "https://www.ecole.cube.fr/blog"
        res = requests.get(url_cube, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=10) and ("/blog/" in href.lower()):
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
olor: #1f2328; }
        .btn { background: #0969da; color: white; padding: 7px 14px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 500; display: inline-block; }
        .btn:hover { background: #0451a5; }
        .footer { margin-top: 25px; text-align: center; font-size: 0.8rem; color: #8c959f; border-top: 1px solid #eaeef2; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 Rss.feed.flow</h1>
        <div class="intro-box">
            <p><strong>Service autonome :</strong> Flux RSS personnalisés générés par GitHub Actions.</p>
        </div>
        <h2>📂 Flux RSS disponibles :</h2>
        <ul>
            <li><span class="title">📜 GEO Histoire</span><a class="btn" href="geo_histoire.xml" target="_blank">Ouvrir le flux</a></li>
            <li><span class="title">🌱 Permaculture (Permathèque)</span><a class="btn" href="permatheque.xml" target="_blank">Ouvrir le flux</a></li>
            <li><span class="title">💎 Web3 & Airdrops</span><a class="btn" href="web3_airdrops.xml" target="_blank">Ouvrir le flux</a></li>
            <li><span class="title">🇫🇷 Météo Express (France)</span><a class="btn" href="meteo_france.xml" target="_blank">Ouvrir le flux</a></li>
            <li><span class="title">🌤️ Météo Régionale (Côte-d'Or)</span><a class="btn" href="meteo_cote_dor.xml" target="_blank">Ouvrir le flux</a></li>
            <li><span class="title">🤖 Tech DIY & Agents IA</span><a class="btn" href="tech_ia.xml" target="_blank">Ouvrir le flux</a></li>
        </ul>
        <div class="footer">Rss.feed.flow</div>
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

