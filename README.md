# Freshness Crawler

Petit script Python qui crawl un site à partir d'une URL principale et extrait les dates de publication / modification quand elles sont présentes dans le HTML.

## Installation

```bash
python3 -m venv .freshness-venv
source .freshness-venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
python freshness.py https://example.com
```

Si aucune URL n'est fournie, le script utilise l'URL par défaut configurée dans le code.

Le résultat est écrit dans un CSV nommé automatiquement à partir du domaine, par exemple `example_com_dates.csv`.
