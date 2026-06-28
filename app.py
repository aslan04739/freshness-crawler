import streamlit as st

from freshness import crawl_site, normalize_start_url


st.set_page_config(page_title="Freshness Crawler", page_icon="🕒", layout="wide")

st.title("Freshness Crawler")
st.caption("Entre une URL principale et récupère les dates de publication et de modification quand elles sont disponibles.")

url = st.text_input("URL du site", value="https://amphibee.fr/")

if st.button("Lancer le crawl", type="primary"):
    with st.spinner("Analyse du site en cours..."):
        df, output_file = crawl_site(normalize_start_url(url))

    st.success(f"Terminé. {len(df)} pages analysées. Résultat enregistré dans {output_file}.")

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
        st.info("Aucune page exploitable n'a été trouvée pour cette URL.")
