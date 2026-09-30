import os
import re
import html
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# BASE URL
BASE_ICON_URL = "https://githubpracticer.github.io/Rss.feed.flow/icons"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_title(title):
    if not title:
        return ""
    # Échappe les caractères XML critiques (<, >, &)
    title = html.escape(title)
    # Nettoie les retours à la ligne et espaces superflus
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def is_valid_link(title, href, min_length=8, specific_ignored=None):
    if not title or len(title) < min_length:
        return False
    
    title_lower = title.lower()
    href_lower = href.lower()

    # Mots-clés d'exclusion généraux
    general_ignored = [
        "javascript:", "mailto:", "#", "login", "register", "connexion", 
        "politique de confidentialité", "mentions légales", "cgv", "cgu", 
        "contact", "facebook", "twitter", "instagram", "linkedin"
    ]

    for term in general_ignored:
        if term in title_lower or term in href_lower:
            return False

    if specific_ignored:
        for term in specific_ignored:
            if term in title_lower or term in href_lower:
                return False

    return True

def create_fallback_entry(fg, site_name, site_url):
    fe = fg.add_entry()
    fe.title(f"{site_name} - Aucune mise à jour détectée")
    fe.link(href=site_url)
    fe.id(site_url)

# ---------------------------------------------------------
# 1. GEO HISTOIRE
# ---------------------------------------------------------
def build_geo_histoire_rss():
    url = "https://www.geo.fr/histoire"
    fg = FeedGenerator()
    fg.title("GEO Histoire")
    fg.link(href=url, rel="alternate")
    fg.description("Les derniers articles Histoire de GEO.fr")
    fg.language("fr")
    fg.icon(f"{BASE_ICON_URL}/Geo.jpg")

    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]

                if "/histoire/" in href and is_valid_link(title, href, min_length=15):
                    full_url = href if href.startswith("http") else f"https://www.geo.fr{href}"
                    
                    if full_url not in seen_links and full_url.rstrip("/") != "https://www.geo.fr/histoire":
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur GEO Histoire: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "GEO Histoire", url)

    fg.rss_file("geo_histoire.xml", pretty=True)
    print("✓ geo_histoire.xml généré.")

# ---------------------------------------------------------
# 2. PERMATHÈQUE
# ---------------------------------------------------------
def build_permatheque_rss():
    url = "https://permatheque.fr"
    fg = FeedGenerator()
    fg.title("Permathèque - Potager & Permaculture")
    fg.link(href=url, rel="alternate")
    fg.description("Guides et fiches pratiques de la Permathèque")
    fg.language("fr")
    fg.icon(f"{BASE_ICON_URL}/Permatheque.jpg")

    # Liste d'exclusion sans "pépinière de projets"
    perma_ignored = [
        "connexion", "se connecter", "s'inscrire", "mon compte", "panier",
        "soutenir", "ajouter un évènement", "déposer une annonce", 
        "publier un article", "nous contacter", "contact",
        "instagram", "facebook", "suivez-nous", "association", "mentions", "cgv"
    ]
    entries_count = 0

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            # Ciblage par blocs d'articles
            article_blocks = soup.find_all(["article", "div", "section"], class_=re.compile(r'post|card|entry|article|item', re.I))
            target_tags = article_blocks if article_blocks else [soup]

            for block in target_tags:
                for a_tag in block.find_all("a", href=True):
                    title = clean_title(a_tag.get_text(strip=True))
                    href = a_tag["href"]

                    if is_valid_link(title, href, min_length=10, specific_ignored=perma_ignored):
                        full_url = href if href.startswith("http") else f"https://permatheque.fr{href}"
                        
                        if full_url not in seen_links and full_url.rstrip("/") != "https://permatheque.fr":
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

# ---------------------------------------------------------
# 3. WEB3 & AIRDROPS (Multi-sources complètes)
# ---------------------------------------------------------
def build_web3_airdrops_rss():
    fg = FeedGenerator()
    fg.title("Web3 & Airdrops Update")
    fg.link(href="https://cryptoast.fr/airdrop/", rel="alternate")
    fg.description("Flux consolidé Airdrops & Web3 (Cryptoast, AirdropAlert, Airdrops.io, CoinAcademy)")
    fg.language("fr")
    fg.icon(f"{BASE_ICON_URL}/Airdrops.jpg")

    seen_links = set()
    entries_count = 0

    # Source 1: Cryptoast (avec filtrage de récence)
    try:
        res = requests.get("https://cryptoast.fr/airdrop/", headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                raw_title = a_tag.get_text(strip=True)
                href = a_tag["href"]
                
                # Exclut les articles de plus de 30 jours
                if "il y a" in raw_title.lower() and re.search(r'il y a ([3-9]\d|\d{3,}) jours', raw_title.lower()):
                    continue

                clean_t = re.sub(r'Par\s+.*$', '', raw_title).strip()
                clean_t = clean_title(clean_t)

                if is_valid_link(clean_t, href, min_length=10):
                    full_url = href if href.startswith("http") else f"https://cryptoast.fr{href}"
                    if full_url not in seen_links and "/airdrop/" in full_url:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[Cryptoast] {clean_t}")
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Cryptoast Airdrops: {e}")

    # Source 2: AirdropAlert (RSS Direct)
    try:
        res = requests.get("https://airdropalert.com/feed/rssfeed", headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "xml")
            for item in soup.find_all("item")[:10]:
                title = clean_title(item.title.text if item.title else "")
                link = item.link.text if item.link else ""
                if link and link not in seen_links:
                    seen_links.add(link)
                    fe = fg.add_entry()
                    fe.title(f"[AirdropAlert] {title}")
                    fe.link(href=link)
                    fe.id(link)
                    entries_count += 1
    except Exception as e:
        print(f"Erreur AirdropAlert: {e}")

    # Source 3: Airdrops.io
    try:
        res = requests.get("https://airdrops.io/", headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=8):
                    full_url = href if href.startswith("http") else f"https://airdrops.io{href}"
                    if full_url not in seen_links and "airdrops.io/" in full_url and full_url.count("/") > 3:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[Airdrops.io] {title}")
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
                        if entries_count >= 25:
                            break
    except Exception as e:
        print(f"Erreur Airdrops.io: {e}")

    # Source 4: CoinAcademy (Guides & Airdrops FR)
    try:
        res = requests.get("https://coinacademy.fr/category/airdrop/", headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]
                if is_valid_link(title, href, min_length=12):
                    full_url = href if href.startswith("http") else f"https://coinacademy.fr{href}"
                    if full_url not in seen_links and "/airdrop/" in full_url and full_url.rstrip("/") != "https://coinacademy.fr/category/airdrop":
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(f"[CoinAcademy] {title}")
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur CoinAcademy: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Web3 & Airdrops", "https://cryptoast.fr/airdrop/")

    fg.rss_file("web3_airdrops.xml", pretty=True)
    print("✓ web3_airdrops.xml généré.")

# ---------------------------------------------------------
# 4. MÉTÉO EXPRESS FRANCE
# ---------------------------------------------------------
def build_meteo_france_rss():
    url = "https://meteo-express.com/actualites/"
    fg = FeedGenerator()
    fg.title("Météo Express - France")
    fg.link(href=url, rel="alternate")
    fg.description("Actualités et bulletins météo France")
    fg.language("fr")
    fg.icon(f"{BASE_ICON_URL}/FranceMeteo.jpg")

    entries_count = 0
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            seen_links = set()

            for a_tag in soup.find_all("a", href=True):
                title = clean_title(a_tag.get_text(strip=True))
                href = a_tag["href"]

                if "/actualites/" in href and is_valid_link(title, href, min_length=12):
                    full_url = href if href.startswith("http") else f"https://meteo-express.com{href}"
                    
                    if full_url not in seen_links and full_url.rstrip("/") != "https://meteo-express.com/actualites":
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Météo France: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Météo Express France", url)

    fg.rss_file("meteo_france.xml", pretty=True)
    print("✓ meteo_france.xml généré.")

# ---------------------------------------------------------
# 5. MÉTÉO RÉGIONALE (Côte-d'Or)
# ---------------------------------------------------------
def build_meteo_cote_dor_rss():
    url = "https://www.bienpublic.com/meteo/cote-d-or"
    fg = FeedGenerator()
    fg.title("Météo Côte-d'Or (Le Bien Public)")
    fg.link(href=url, rel="alternate")
    fg.description("Météo et prévisions Côte-d'Or")
    fg.language("fr")
    fg.icon(f"{BASE_ICON_URL}/BourgogneMeteo.jpg")

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
                    full_url = href if href.startswith("http") else f"https://www.bienpublic.com{href}"
                    if full_url not in seen_links and "/meteo/" in full_url:
                        seen_links.add(full_url)
                        fe = fg.add_entry()
                        fe.title(title)
                        fe.link(href=full_url)
                        fe.id(full_url)
                        entries_count += 1
    except Exception as e:
        print(f"Erreur Météo Côte-d'Or: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Météo Côte-d'Or", url)

    fg.rss_file("meteo_cote_dor.xml", pretty=True)
    print("✓ meteo_cote_dor.xml généré.")

# ---------------------------------------------------------
# 6. TECH DIY & AGENTS IA
# ---------------------------------------------------------
def build_tech_ia_rss():
    url = "https://www.minimachines.net/"
    fg = FeedGenerator()
    fg.title("Tech DIY, Hardware & IA (Minimachines)")
    fg.link(href=url, rel="alternate")
    fg.description("Actualité Tech, Minimachines et Mini-PC")
    fg.language("fr")
    fg.icon(f"{BASE_ICON_URL}/TechAiDIY.jpg")

    entries_count = 0
    try:
        response = requests.get("https://www.minimachines.net/feed", headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "xml")
            for item in soup.find_all("item")[:15]:
                title = clean_title(item.title.text if item.title else "")
                link = item.link.text if item.link else ""
                if link:
                    fe = fg.add_entry()
                    fe.title(title)
                    fe.link(href=link)
                    fe.id(link)
                    entries_count += 1
    except Exception as e:
        print(f"Erreur Tech DIY: {e}")

    if entries_count == 0:
        create_fallback_entry(fg, "Tech DIY & IA", url)

    fg.rss_file("tech_ia.xml", pretty=True)
    print("✓ tech_ia.xml généré.")

# ---------------------------------------------------------
# 7. SCRIPT HTML (index.html)
# ---------------------------------------------------------
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
        h1 { margin-top: 0; color: #0969da; font-size: 1.5rem; border-bottom: 2px solid #eaeef2; padding-bottom: 10px; }
        h2 { font-size: 1.1rem; color: #24292f; margin-top: 20px; }
        p { color: #57606a; font-size: 0.9rem; margin: 0 0 8px 0; }
        .intro-box { background: #f0f7ff; border-left: 4px solid #0969da; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; }
        .intro-box ol { margin: 8px 0 0 0; padding-left: 20px; font-size: 0.88rem; color: #24292f; }
        .intro-box li { margin-bottom: 4px; }
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
            <p><strong>💡 Comment s'abonner à un flux :</strong></p>
            <ol>
                <li>Maintenez un appui long sur le bouton <strong>Flux XML</strong> de votre choix et sélectionnez <em>Copier l'adresse du lien</em>.</li>
                <li>Ouvrez votre lecteur RSS open source préféré (ex: <strong>ReadYou</strong>, <strong>Feeder</strong>, <strong>Fressh</strong>) et collez le lien dans l'option <em>S'abonner / +</em>.</li>
            </ol>
        </div>
        <h2>📂 Flux RSS disponibles :</h2>
        <ul>
            <li><span class="title">📜 GEO Histoire</span><a class="btn" href="geo_histoire.xml" target="_blank">Flux XML</a></li>
            <li><span class="title">🌱 Permaculture (Permathèque)</span><a class="btn" href="permatheque.xml" target="_blank">Flux XML</a></li>
            <li><span class="title">💎 Web3 & Airdrops</span><a class="btn" href="web3_airdrops.xml" target="_blank">Flux XML</a></li>
            <li><span class="title">🇫🇷 Météo Express (France)</span><a class="btn" href="meteo_france.xml" target="_blank">Flux XML</a></li>
            <li><span class="title">🌤️️ Météo Régionale (Côte-d'Or)</span><a class="btn" href="meteo_cote_dor.xml" target="_blank">Flux XML</a></li>
            <li><span class="title">🤖 Tech DIY & Agents IA</span><a class="btn" href="tech_ia.xml" target="_blank">Flux XML</a></li>
        </ul>
        <div class="footer">Rss.feed.flow</div>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✓ index.html généré.")

# ---------------------------------------------------------
# EXECUTION GENERALE
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Début de la génération des flux RSS...")
    build_geo_histoire_rss()
    build_permatheque_rss()
    build_web3_airdrops_rss()
    build_meteo_france_rss()
    build_meteo_cote_dor_rss()
    build_tech_ia_rss()
    build_index_html()
    print("Tous les flux et index.html ont été générés avec succès.")
