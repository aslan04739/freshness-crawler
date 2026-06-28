# Freshness Crawler

Petit script Python qui crawl un site à partir d'une URL principale et extrait les dates de publication / modification quand elles sont présentes dans le HTML.

## Version Streamlit

Si tu déploies sur Streamlit Community Cloud, lance plutôt l'application avec `app.py`.
Tu peux y coller une ou plusieurs URLs, une par ligne.

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

Pour plusieurs sites dans l'interface Streamlit, mets une URL par ligne puis clique sur le bouton de crawl.

Ou en mode Streamlit local:

```bash
streamlit run app.py
```

Si aucune URL n'est fournie, le script utilise l'URL par défaut configurée dans le code.

Le résultat est écrit dans un CSV nommé automatiquement à partir du domaine, par exemple `example_com_dates.csv`.
