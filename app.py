import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sélection de joueurs", layout="wide")
st.title("🏉 Sélection de joueurs 🏉")

# --- URL du fichier Excel Google Drive ---
# ⚠️ Remplacer TON_ID_DE_FICHIER par l'ID réel du fichier Google Drive
url = "https://docs.google.com/spreadsheets/d/1y2eiaLo3xM8xWREgdTrVEuPlWKniDVql/edit?usp=drive_link&ouid=115423419700090282464&rtpof=true&sd=true"

try:
    df = pd.read_excel(url)

    # On ne garde que les colonnes utiles
    colonnes_utiles = ["Nom", "Prénom", "Club", "1ere ligne", "Amical 2"]
    df = df[colonnes_utiles]

    # Transformation de Amical 2 en symboles
    mapping_amical = {"A": "❌", "P": "✅", "C": "❓"}
    df["Amical 2"] = df["Amical 2"].map(mapping_amical).fillna("")

    st.subheader("Aperçu du fichier (colonnes filtrées)")
    st.dataframe(df, use_container_width=True)

    # --- Sélection des joueurs ---
    joueurs_selectionnes = st.multiselect(
        "Choisir les joueurs :",
        options=df["Nom"].tolist()
    )

    if joueurs_selectionnes:
        st.subheader("Configuration des joueurs sélectionnés")

        joueurs_config = []

        for i, joueur in enumerate(joueurs_selectionnes, start=1):
            ligne_joueur = df[df["Nom"] == joueur].iloc[0]

            st.markdown(f"### {joueur} ({ligne_joueur['Prénom']}) - {ligne_joueur['Club']}")

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                numero = st.number_input(
                    f"Numéro de {joueur}",
                    min_value=1,
                    max_value=23,
                    value=i,
                    key=f"num_{joueur}"
                )
            with col2:
                capitaine = st.checkbox("Capitaine", key=f"cap_{joueur}")
            with
