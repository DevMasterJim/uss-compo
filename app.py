import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sélection de joueurs", layout="wide")
st.title("🏉 Sélection de joueurs 🏉")

# --- URL directe Google Drive ---
url = "https://drive.google.com/uc?export=download&id=1y2eiaLo3xM8xWREgdTrVEuPlWKniDVql"

# --- Télécharger le fichier Excel ---
df = pd.read_excel(url, engine="openpyxl")

# Colonnes utiles
colonnes_utiles = ["Présence","Prénom","Nom","Club", "1ere ligne"]
df = df[colonnes_utiles]

# Transformation Présence
mapping_presence = {"A": "❌", "P": "✅", "C": "❔"}
df["Présence"] = df["Présence"].map(mapping_presence).fillna("")

st.subheader("Aperçu du fichier (colonnes filtrées)")
st.dataframe(df, use_container_width=True)

# --- Initialisation de la session pour stocker les joueurs sélectionnés ---
if "selection_joueurs" not in st.session_state:
    st.session_state.selection_joueurs = []

# --- Liste des numéros disponibles ---
def numeros_disponibles():
    attribues = [j["Numéro"] for j in st.session_state.selection_joueurs]
    return [n for n in range(1, 24) if n not in attribues]

# --- Sélection des joueurs ---
# On ne montre que les joueurs non encore choisis
joueurs_disponibles = [j for j in df["Nom"].tolist() if j not in [s["Nom"] for s in st.session_state.selection_joueurs]]

joueur_choisi = st.selectbox("Choisir un joueur :", options=joueurs_disponibles)

if joueur_choisi:
    ligne_joueur = df[df["Nom"] == joueur_choisi].iloc[0]

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        numero = st.selectbox(
            f"Numéro de {joueur_choisi}",
            options=numeros_disponibles(),
            index=0
        )
    with col2:
        capitaine = st.checkbox("Capitaine", key=f"cap_{joueur_choisi}")
    with col3:
        premiere_ligne = st.selectbox(
            "1ère ligne",
            options=["", "G", "T", "D", "GD", "GTD"],
            index=0 if pd.isna(ligne_joueur["1ere ligne"]) else 0
        )

    # Ajouter le joueur à la sélection
    if st.button("✅ Ajouter le joueur"):
        st.session_state.selection_joueurs.append({
            "Nom": ligne_joueur["Nom"],
            "Prénom": ligne_joueur["Prénom"],
            "Club": ligne_joueur["Club"],
            "Numéro": numero,
            "Capitaine": "Oui" if capitaine else "Non",
            "1ère ligne": premiere_ligne if premiere_ligne else ligne_joueur["1ere ligne"],
            "Amical 2": ligne_joueur["Amical 2"]
        })
        st.experimental_rerun()  # rafraîchit l'app pour mettre à jour la liste

# --- Affichage de la sélection ---
if st.session_state.selection_joueurs:
    selection_df = pd.DataFrame(st.session_state.selection_joueurs).sort_values("Numéro")
    st.subheader("📋 Récapitulatif")
    st.dataframe(selection_df, use_container_width=True)

    # --- Vérification unicité des numéros ---
    numeros = selection_df["Numéro"].tolist()
    numeros_dupliques = [x for x in numeros if numeros.count(x) > 1]

    if numeros_dupliques:
        st.error(f"⚠️ Les numéros {sorted(set(numeros_dupliques))} sont attribués plusieurs fois.")
        export_possible = False
    else:
        export_possible = True

    # --- Export Excel ---
    if st.button("📥 Exporter la sélection"):
        if export_possible:
            selection_df.to_excel("joueurs_selectionnes.xlsx", index=False)
            st.success("✅ Fichier exporté avec succès !")
        else:
            st.warning("❌ Export impossible tant que des numéros sont dupliqués.")
