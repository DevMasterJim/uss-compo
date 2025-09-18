import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sélection de joueurs", layout="wide")
st.title("⚽ Sélection de joueurs")

# --- Upload du fichier ---
uploaded_file = st.file_uploader("📂 Importer un fichier Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Aperçu du fichier")
    st.dataframe(df, use_container_width=True)

    # --- Sélection des joueurs ---
    joueurs_selectionnes = st.multiselect(
        "Choisir les joueurs :",
        options=df["Nom"].tolist()
    )

    if joueurs_selectionnes:
        st.subheader("Configuration des joueurs sélectionnés")

        # Liste des enregistrements
        joueurs_config = []

        for i, joueur in enumerate(joueurs_selectionnes, start=1):
            st.markdown(f"### {joueur}")

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                numero = st.number_input(
                    f"Numéro de {joueur}", min_value=1, max_value=23, value=i, key=f"num_{joueur}"
                )
            with col2:
                capitaine = st.checkbox(
                    "Capitaine", key=f"cap_{joueur}"
                )
            with col3:
                premiere_ligne = st.selectbox(
                    "1ère ligne",
                    options=["", "G", "T", "D", "GD", "GTD"],
                    key=f"pl_{joueur}"
                )

            joueurs_config.append({
                "Nom": joueur,
                "Numéro": numero,
                "Capitaine": "Oui" if capitaine else "Non",
                "1ère ligne": premiere_ligne
            })

        # --- Résumé de la sélection ---
        selection_df = pd.DataFrame(joueurs_config).sort_values("Numéro")
        st.subheader("📋 Récapitulatif")
        st.dataframe(selection_df, use_container_width=True)

        # --- Export Excel ---
        if st.button("📥 Exporter la sélection"):
            selection_df.to_excel("joueurs_selectionnes.xlsx", index=False)
            st.success("✅ Fichier 'joueurs_selectionnes.xlsx' exporté avec succès !")
