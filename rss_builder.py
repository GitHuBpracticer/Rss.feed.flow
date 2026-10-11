import os
import re
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# ---------------------------------------------------------
# CONSTANTES & CONFIGURATION
# ---------------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}
RETENTION_DAYS = 30
CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

EXCLUDED_TITLES = [
    "Site / Médias",
    "Partenaires",
    "Mentions légales",
    "Contact",
    "Not Found",
    "Aucune mise à jour détectée",
    "404",
]

AIRDROP_KEYWORDS = [
    "airdrop",
    "token drop",
    "drop crypto",
    "claim free",
    "gratuit crypto",
    "free token",
    "bonus token",
    "web3 giveaway",
    "wallet airdrop",
    "snapshot",
    "claim rewards",
]

EXCLUDED_AIRDROP_PATTERNS = [
    "prix du bitcoin",
    "prix de l'eth",
    "analyse crypto",
    "crypto market",
    "market update",
    "guide crypto",
    "bitcoin news",
    "eth news",
    "etf crypto",
]


def clean_text(text):
    if not text:
        return ""
    text = str(text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_absolute_url(url, base_url=None):
    if not url:
        return None
    url = url.strip()
    if not url:
        return None
    if url.startswith("data:"):
        return None
    if url.startswith("//"):
        return "https:" + url
    if not re.match(r"^https?://", url):
        if base_url:
            return urljoin(base_url, url)
        return url
    return url


def normalize_image_url(img_url, base_url=None):
    if not img_url:
        return None
    img_url = normalize_absolute_url(img_url, base_url)
    if not img_url:
        return None
    if "?" in img_url:
        return img_url.split("?")[0]
    return img_url


def is_valid_item(title, link):
    if not title or not link:
        return False
    title_clean = clean_text(title)
    for excluded in EXCLUDED_TITLES:
        if excluded.lower() in title_clean.lower():
            return False
    return True


def is_airdrop_related(title, description=""):
    text = clean_text(f"{title} {description}").lower()
    if not text:
        return False
    if any(keyword in text for keyword in AIRDROP_KEYWORDS):
        return True
    if any(pattern in text for pattern in EXCLUDED_AIRDROP_PATTERNS):
        return False
    return False


def create_feed_generator(title, link, description, logo_filename):
    fg = FeedGenerator()
    fg.title(title)
    fg.link(href=link, rel="alternate")
    fg.description(description)
    fg.language("fr")

    base_logo_url = "https://githubpracticer.github.io/Rss.feed.flow/icons/"
    icon_url = f"{base_logo_url}{logo_filename}"

    # Compatibilité plus large avec les lecteurs RSS/Atom
    fg.image(url=icon_url, title=title, link=link)
    fg.icon(icon_url)
    fg.logo(icon_url)

    return fg


def add_entry_with_media(fg, title, link, description, pub_date, img_url=None):
    if not is_valid_item(title, link):
        return

    entry = fg.add_entry()
    entry.title(clean_text(title))
    entry.link(href=link)
    entry.pubDate(pub_date if pub_date else datetime.now(timezone.utc))

    clean_desc = clean_text(description)
    if img_url:
        formatted_desc = (
            f'<p><img src="{img_url}" alt="Miniature" '
            'style="max-width:100%; height:auto;" /></p><p>{clean_desc}</p>'
        )
        entry.enclosure(url=img_url, type="image/jpeg")
    else:
        formatted_desc = f"<p>{clean_desc}</p>"

    entry.description(formatted_desc)


# ---------------------------------------------------------
# 1. SCRAPER : GEO HISTOIRE
# ---------------------------------------------------------
def scrape_geo_histoire(fg):
    url = "https://www.geo.fr/histoire"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.content, "html.parser")
        articles = soup.find_all("article", limit=15)
        for art in articles:
            a_tag = art.find("a", href=True)
            title_tag = art.find(["h2", "h3", "span"])
            img_tag = art.find("img")

            if a_tag and title_tag:
                title = clean_text(title_tag.get_text())
                link = normalize_absolute_url(a_tag.get("href"), url)
                if not link:
                    continue
                img_url = normalize_image_url(
                    img_tag.get("src") or img_tag.get("data-src") if img_tag else None,
                    url,
                )
                add_entry_with_media(
                    fg,
                    title,
                    link,
                    "Article Histoire de GEO.fr",
                    datetime.now(timezone.utc),
                    img_url,
                )
    except Exception as e:
        print(f"Erreur GEO Histoire: {e}")


# ---------------------------------------------------------
# 2. SCRAPER : PERMACULTURE (PERMATHÈQUE)
# ---------------------------------------------------------
def scrape_permatheque(fg):
    url = "https://permatheque.fr/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.content, "html.parser")

        items = soup.find_all(
            ["article", "div", "section"],
            class_=re.compile(r"(post|item|tutorial|guide|pdf|ressource|content|card)", re.IGNORECASE),
            limit=25,
        )

        if not items:
            items = soup.find_all(["div", "section", "article"], limit=25)

        for item in items:
            a_tag = item.find("a", href=True)
            if not a_tag:
                continue

            title_tag = item.find(["h2", "h3", "h4", "h1", "a"])
            if not title_tag:
                continue

            title = clean_text(title_tag.get_text())
            if not title:
                continue

            link = normalize_absolute_url(a_tag.get("href"), url)
            if not link:
                continue

            img_tag = item.find("img")
            img_url = normalize_image_url(
                img_tag.get("src") or img_tag.get("data-src") if img_tag else None,
                url,
            )

            if "pdf" in link.lower() or "pdf" in title.lower():
                content_type = "📄 PDF Permaculture"
            elif "tutorial" in link.lower() or "guide" in link.lower() or "tuto" in title.lower():
                content_type = "📚 Tutoriel Permaculture"
            else:
                content_type = "📖 Article Permaculture"

            add_entry_with_media(
                fg,
                title,
                link,
                content_type,
                datetime.now(timezone.utc),
                img_url,
            )
    except Exception as e:
        print(f"Erreur Permathèque: {e}")


# ---------------------------------------------------------
# 3. SCRAPER : WEB3 & AIRDROPS
# ---------------------------------------------------------
def scrape_web3(fg):
    urls = [
        "https://coinspeaker.com/news/crypto/",
        "https://cointelegraph.com/tags/airdrop",
    ]

    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.content, "html.parser")
            articles = soup.find_all("article", limit=20)
            if not articles:
                continue

            for art in articles:
                a_tag = art.find("a", href=True)
                title_tag = art.find(["h2", "h3", "h4"])
                img_tag = art.find("img")

                if not a_tag or not title_tag:
                    continue

                title = clean_text(title_tag.get_text())
                if not is_airdrop_related(title):
                    continue

                link = normalize_absolute_url(a_tag.get("href"), url)
                if not link:
                    continue

                img_url = normalize_image_url(
                    img_tag.get("src") or img_tag.get("data-src") if img_tag else None,
                    url,
                )
                add_entry_with_media(
                    fg,
                    title,
                    link,
                    "Actualité Web3 & Airdrops",
                    datetime.now(timezone.utc),
                    img_url,
                )
        except Exception as e:
            print(f"Erreur Web3: {e}")


# ---------------------------------------------------------
# 4. SCRAPER : MÉTÉO EXPRESS (FRANCE)
# ---------------------------------------------------------
def scrape_meteo_express(fg):
    url = "https://meteo-express.com/actualites/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.content, "html.parser")
        articles = soup.find_all("article", limit=15)
        for art in articles:
            a_tag = art.find("a", href=True)
            title_tag = art.find(["h2", "h3"])
            img_tag = art.find("img")

            if a_tag and title_tag:
                title = clean_text(title_tag.get_text())
                link = normalize_absolute_url(a_tag.get("href"), url)
                if not link:
                    continue
                img_url = normalize_image_url(img_tag.get("src") if img_tag else None, url)
                add_entry_with_media(
                    fg,
                    title,
                    link,
                    "Bulletin Météo Express France",
                    datetime.now(timezone.utc),
                    img_url,
                )
    except Exception as e:
        print(f"Erreur Météo Express: {e}")


# ---------------------------------------------------------
# 5. SCRAPER : MÉTÉO CÔTE-D'OR & REGION (DIJON + FR3 BFC)
# ---------------------------------------------------------
def scrape_meteo_cote_dor(fg):
    urls = [
        "https://france3-regions.franceinfo.fr/bourgogne-franche-comte/",
        "https://www.meteo-dijon.com/",
    ]

    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.content, "html.parser")
            articles = soup.find_all(["article", "div"], limit=15)
            for art in articles:
                a_tag = art.find("a", href=True)
                if not a_tag:
                    continue

                title_anchor = art.find(["h2", "h3", "h4", "a"])
                if not title_anchor:
                    continue

                title = clean_text(title_anchor.get_text())
                if not title:
                    continue

                link = normalize_absolute_url(a_tag.get("href"), url)
                if not link:
                    continue

                if not any(k in title.lower() for k in ["meteo", "bfc", "dijon", "bourgogne"]):
                    continue

                img_tag = art.find("img")
                img_url = normalize_image_url(
                    img_tag.get("src") or img_tag.get("data-src") if img_tag else None,
                    url,
                )

                add_entry_with_media(
                    fg,
                    f"[Météo Bourgogne] {title}",
                    link,
                    "Prévisions & Actualités Météo Bourgogne-Franche-Comté",
                    datetime.now(timezone.utc),
                    img_url,
                )
        except Exception as e:
            print(f"Erreur Météo Bourgogne: {e}")


# ---------------------------------------------------------
# 6. SCRAPER : TECH DIY & AGENTS IA
# ---------------------------------------------------------
def scrape_tech_ia(fg):
    url = "https://www.tomshardware.fr/actualites/ia/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.content, "html.parser")
        articles = soup.find_all("article", limit=15)
        for art in articles:
            a_tag = art.find("a", href=True)
            title_tag = art.find(["h2", "h3"])
            img_tag = art.find("img")

            if a_tag and title_tag:
                title = clean_text(title_tag.get_text())
                link = normalize_absolute_url(a_tag.get("href"), url)
                if not link:
                    continue
                img_url = normalize_image_url(img_tag.get("src") if img_tag else None, url)
                add_entry_with_media(
                    fg,
                    title,
                    link,
                    "Actualités IA & Tech DIY",
                    datetime.now(timezone.utc),
                    img_url,
                )
    except Exception as e:
        print(f"Erreur Tech IA: {e}")


# ---------------------------------------------------------
# 7. GENERATION DE LA PAGE HTML (INDEX.HTML)
# ---------------------------------------------------------
def build_index_html():
    html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rss.feed.flow - Flux RSS Automatisés</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 12px; background: #f4f6f8; color: #1a1a1a; line-height: 1.5; }
        .container { max-width: 600px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h1 { margin-top: 0; color: #0969da; font-size: 1.4rem; border-bottom: 2px solid #eaeef2; padding-bottom: 8px; }
        h2 { font-size: 1.05rem; color: #24292f; margin-top: 18px; margin-bottom: 10px; }
        p { color: #57606a; font-size: 0.88rem; margin: 0 0 8px 0; }

        .intro-box { background: #f0f7ff; border-left: 4px solid #0969da; padding: 12px; border-radius: 6px; margin-bottom: 18px; }
        .intro-box ol { margin: 6px 0 0 0; padding-left: 18px; font-size: 0.85rem; color: #24292f; }
        .intro-box li { margin-bottom: 6px; }

        .support-box { background: #fff8c5; border-left: 4px solid #d4a72c; padding: 14px; border-radius: 6px; margin-top: 22px; text-align: center; }
        .support-box p { color: #4d3800; font-weight: 600; margin-bottom: 10px; }
        .btn-kofi { background: #ff5e5b; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-bottom: 6px; }
        .paypal-link { display: block; font-size: 0.8rem; color: #57606a; text-decoration: underline; }

        ul { list-style: none; padding: 0; margin: 10px 0; }
        li { margin-bottom: 10px; padding: 12px; background: #ffffff; border-radius: 8px; border: 1px solid #d0d7de; display: flex; flex-direction: column; gap: 8px; }
        .title { font-weight: 600; font-size: 0.9rem; color: #1f2328; width: 100%; }
        .btn-container { text-align: right; width: 100%; }
        .btn { background: #0969da; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.82rem; font-weight: 500; display: inline-block; }

        .footer { margin-top: 22px; text-align: center; font-size: 0.78rem; color: #8c959f; border-top: 1px solid #eaeef2; padding-top: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 Rss.feed.flow</h1>
        <div class="intro-box">
            <p><strong>💡 Comment s'abonner :</strong></p>
            <ol>
                <li>Maintenez un appui long sur le bouton <strong>Flux XML</strong> et sélectionnez <em>Copier l'adresse du lien</em>.</li>
                <li>Collez le lien dans votre lecteur RSS open source (ex: <strong>ReadYou</strong>, <strong>Feeder</strong>).</li>
                <li>⚙️ <strong>Optimisations Python :</strong> mise à jour automatique toutes les 6 heures via GitHub Actions, aucun doublon multi-sources et purge automatique des contenus de plus de 30 jours.</li>
            </ol>
        </div>

        <h2>📂 Flux RSS disponibles :</h2>
        <ul>
            <li>
                <span class="title">📜 GEO Histoire</span>
                <div class="btn-container"><a class="btn" href="geo_histoire.xml" target="_blank">Flux XML</a></div>
            </li>
            <li>
                <span class="title">🌱 Permaculture (Permathèque)</span>
                <div class="btn-container"><a class="btn" href="permatheque.xml" target="_blank">Flux XML</a></div>
            </li>
            <li>
                <span class="title">💎 Web3 & Airdrops</span>
                <div class="btn-container"><a class="btn" href="web3_airdrops.xml" target="_blank">Flux XML</a></div>
            </li>
            <li>
                <span class="title">🇫🇷 Météo Express (France)</span>
                <div class="btn-container"><a class="btn" href="meteo_france.xml" target="_blank">Flux XML</a></div>
            </li>
            <li>
                <span class="title">🌤 Météo Régionale (Dijon & FR3 BFC)</span>
                <div class="btn-container"><a class="btn" href="meteo_cote_dor.xml" target="_blank">Flux XML</a></div>
            </li>
            <li>
                <span class="title">🤖 Tech DIY & Agents IA</span>
                <div class="btn-container"><a class="btn" href="tech_ia.xml" target="_blank">Flux XML</a></div>
            </li>
        </ul>

        <div class="support-box">
            <p>☕ Ces flux vous sont utiles au quotidien ?</p>
            <a class="btn-kofi" href="https://ko-fi.com/multifloow" target="_blank">Offrir un café sur Ko-fi</a>
            <a class="paypal-link" href="https://paypal.com/paypalme/Multifloo" target="_blank">Ou soutenir via PayPal.me</a>
        </div>

        <div class="footer">
            Rss.feed.flow — Développé par <strong>GitHubPracticer</strong>
        </div>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✓ index.html généré.")


# ---------------------------------------------------------
# EXECUTION PRINCIPALE
# ---------------------------------------------------------
if __name__ == "__main__":
    feeds = [
        (
            "GEO Histoire",
            "https://www.geo.fr/histoire",
            "Flux Histoire GEO.fr",
            "geo_histoire.xml",
            "geo.jpg",
            scrape_geo_histoire,
        ),
        (
            "Permaculture",
            "https://permatheque.fr/",
            "Flux Permaculture",
            "permatheque.xml",
            "permatheque.jpg",
            scrape_permatheque,
        ),
        (
            "Web3 & Airdrops",
            "https://coinspeaker.com/",
            "Flux Web3",
            "web3_airdrops.xml",
            "airdrops.jpg",
            scrape_web3,
        ),
        (
            "Météo Express",
            "https://meteo-express.com/",
            "Flux Météo France",
            "meteo_france.xml",
            "francemeteo.jpg",
            scrape_meteo_express,
        ),
        (
            "Météo Côte-d'Or & BFC",
            "https://france3-regions.franceinfo.fr/bourgogne-franche-comte/",
            "Flux Météo Dijon & Bourgogne FR3",
            "meteo_cote_dor.xml",
            "bourgognemeteo.jpg",
            scrape_meteo_cote_dor,
        ),
        (
            "Tech IA",
            "https://www.tomshardware.fr/",
            "Flux Tech & IA",
            "tech_ia.xml",
            "techaidiy.jpg",
            scrape_tech_ia,
        ),
    ]

    for title, link, desc, filename, logo, scraper_func in feeds:
        fg = create_feed_generator(title, link, desc, logo)
        scraper_func(fg)
        fg.rss_file(filename, pretty=True)
        print(f"✓ {filename} mis à jour avec le logo icons/{logo}.")

    build_index_html()
