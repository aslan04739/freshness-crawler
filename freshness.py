import argparse
import json
import time
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
MAX_PAGES_TO_CRAWL = 500  # Sécurité pour éviter un crawl infini
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (SEO Analysis)"


def parse_args():
    parser = argparse.ArgumentParser(description="Crawl un site et extrait les dates de publication/modification.")
    parser.add_argument(
        "url",
        nargs="?",
        default="https://amphibee.fr/",
        help="URL principale du site à crawler (ex: https://example.com)",
    )
    return parser.parse_args()


def normalize_start_url(url):
    if "://" not in url:
        url = f"https://{url}"

    if not url.endswith("/"):
        url += "/"

    return url


def extract_dates(soup):
    """
    Extrait les dates en priorisant le JSON-LD (Standard SEO),
    avec fallback sur les balises Meta.
    """
    pub_date, mod_date = None, None

    # 1. Extraction via JSON-LD (Très fréquent sur WordPress/Agences)
    json_lds = soup.find_all("script", type="application/ld+json")
    for script in json_lds:
        try:
            if script.string:
                data = json.loads(script.string)

                # Gestion des structures JSON-LD complexes (Yoast/RankMath utilisent souvent un "@graph")
                items = data.get("@graph", data) if isinstance(data, dict) else data
                if isinstance(items, dict):
                    items = [items]

                for item in items:
                    if isinstance(item, dict):
                        if "datePublished" in item and not pub_date:
                            pub_date = item.get("datePublished")
                        if "dateModified" in item and not mod_date:
                            mod_date = item.get("dateModified")
        except (json.JSONDecodeError, TypeError):
            continue

    # 2. Fallback via Meta Tags (Open Graph)
    if not pub_date:
        meta_pub = soup.find("meta", property="article:published_time")
        if meta_pub:
            pub_date = meta_pub.get("content")

    if not mod_date:
        meta_mod = soup.find("meta", property="article:modified_time")
        if meta_mod:
            mod_date = meta_mod.get("content")

    return pub_date, mod_date


def crawl_site(start_url):
    parsed_start_url = urlparse(start_url)
    base_domain = parsed_start_url.netloc.replace("www.", "")
    output_file = f"{base_domain.replace('.', '_')}_dates.csv"

    visited_urls = set()
    urls_to_visit = [start_url]
    results = []

    print(f"Début du crawl sur {start_url}...")

    while urls_to_visit and len(visited_urls) < MAX_PAGES_TO_CRAWL:
        current_url = urls_to_visit.pop(0)

        if current_url in visited_urls:
            continue

        print(f"[{len(visited_urls)+1}/{MAX_PAGES_TO_CRAWL}] Crawl : {current_url}")
        visited_urls.add(current_url)

        try:
            response = requests.get(current_url, headers={"User-Agent": USER_AGENT}, timeout=10)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue
        except requests.RequestException as e:
            print(f"Erreur ignorée sur {current_url} : {e}")
            continue

        soup = BeautifulSoup(response.content, "lxml")

        pub_date, mod_date = extract_dates(soup)

        results.append(
            {
                "URL": current_url,
                "Date Publication": pub_date,
                "Date Modification": mod_date,
                "Status Code": response.status_code,
            }
        )

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(current_url, href)
            parsed_url = urlparse(full_url)

            clean_url = full_url.split("#")[0].split("?")[0]  # Nettoyage des ancres et paramètres de tracking

            # Vérification du domaine (gère les cas avec ou sans www)
            if parsed_url.netloc.replace("www.", "") == base_domain:
                # Exclusion des extensions de fichiers statiques
                if not clean_url.lower().endswith((".pdf", ".jpg", ".png", ".zip", ".css", ".js")):
                    if clean_url not in visited_urls and clean_url not in urls_to_visit:
                        urls_to_visit.append(clean_url)

        time.sleep(0.5)

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\nTerminé ! {len(results)} pages analysées.")
    print(f"Les résultats sont sauvegardés dans le fichier : {output_file}")


if __name__ == "__main__":
    args = parse_args()
    crawl_site(normalize_start_url(args.url))
