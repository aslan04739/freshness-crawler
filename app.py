import streamlit as st

from freshness import crawl_sites, normalize_start_url


st.set_page_config(page_title="Freshness Crawler", page_icon="🕒", layout="wide")

st.title("Freshness Crawler")
st.caption("Entre une ou plusieurs URLs principales et récupère les dates de publication et de modification quand elles sont disponibles.")

urls_text = st.text_area(
    "URLs des sites",
    value="https://amphibee.fr/\nhttps://example.com",
    help="Une URL par ligne. Le crawl sera lancé pour chaque site.",
    height=120,
)

if st.button("Lancer le crawl", type="primary"):
    raw_urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
    start_urls = [normalize_start_url(url) for url in raw_urls]

    if not start_urls:
        st.error("Ajoute au moins une URL valide.")
        st.stop()

    with st.spinner("Analyse des sites en cours..."):
        df, output_file, site_output_files = crawl_sites(start_urls)

    st.success(f"Terminé. {len(df)} pages analysées. Résultat consolidé enregistré dans {output_file}.")

    if site_output_files:
        st.caption("CSV générés par site: " + ", ".join(site_output_files))

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Télécharger le CSV",
            data=csv_data,
            file_name=output_file,
            mime="text/csv",
        )
    else:
        st.info("Aucune page exploitable n'a été trouvée pour les URLs fournies.")
