import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Composition National & Régional", layout="wide")
st.title("🏉 Composition National & Régional 🏉")

# --- URL directe Google Drive ---
url = "https://drive.google.com/uc?export=download&id=1y2eiaLo3xM8xWREgdTrVEuPlWKniDVql"

# --- Charger le fichier Excel ---
try:
    df = pd.read_excel(url, engine="openpyxl")
except Exception as e:
    st.error(f"Impossible de charger le fichier Excel distant : {e}")
    st.stop()

# --- Colonnes utiles ---
colonnes_utiles = ["Présence", "Prénom", "Nom", "Club", "1ere ligne"]
missing = [c for c in colonnes_utiles if c not in df.columns]
if missing:
    st.error(f"Colonnes manquantes dans le fichier Excel : {missing}")
    st.stop()

df = df[colonnes_utiles].copy()

# Transformation Présence
mapping_presence = {"A": "❌", "P": "✅", "C": "❓"}
df["Présence"] = df["Présence"].map(mapping_presence).fillna("")

# --- Filtrer les lignes valides ---
df = df[(df["Nom"].notna()) & (df["Nom"] != "") &
        (df["Présence"].notna()) & (df["Présence"] != "")].copy()
df = df.reset_index(drop=True)

# --- Initialiser la session une seule fois ---
if "attrib" not in st.session_state:
    for niveau in ["National", "Régional"]:
        df[f"Numéro {niveau}"] = None
        df[f"Capitaine {niveau}"] = False
        df[f"1ère ligne {niveau}"] = ""  # vide par défaut
    st.session_state.attrib = df.copy()

# --- Fonction pour éditer un niveau avec keys uniques ---
def edit_niveau(niveau):
    st.subheader(f"✏️ Attribution {niveau}")
    attrib = st.session_state.attrib
    for idx, row in attrib.iterrows():
        col1, col2, col3 = st.columns([1, 1, 2])

        # --- Numéro disponible pour ce niveau ---
        numeros_pris = attrib[f"Numéro {niveau}"].dropna().tolist()
        options_num = [n for n in range(1, 24) if n not in numeros_pris or n == row[f"Numéro {niveau}"]]

        with col1:
            attrib.at[idx, f"Numéro {niveau}"] = st.selectbox(
                f"{row['Nom']} - Numéro {niveau}",
                options=options_num,
                index=0 if pd.isna(row[f"Numéro {niveau}"]) else options_num.index(row[f"Numéro {niveau}"]),
                key=f"num_{niveau}_{idx}"
            )
        with col2:
            attrib.at[idx, f"Capitaine {niveau}"] = st.checkbox(
                "Capitaine",
                value=row[f"Capitaine {niveau}"],
                key=f"cap_{niveau}_{idx}"
            )
        with col3:
            attrib.at[idx, f"1ère ligne {niveau}"] = st.selectbox(
                "1ère ligne",
                options=["", "G", "D", "T", "GD", "GDT"],
                index=0 if row[f"1ère ligne {niveau}"] == "" else ["", "G", "D", "T", "GD", "GDT"].index(row[f"1ère ligne {niveau}"]),
                key=f"ligne_{niveau}_{idx}"
            )

    st.session_state.attrib = attrib

# --- Édition pour les deux niveaux ---
edit_niveau("National")
st.markdown("---")
edit_niveau("Régional")

# --- Aperçu vertical en deux colonnes ---
st.subheader("📋 Aperçu des joueurs sélectionnés")
col_n, col_r = st.columns(2)

with col_n:
    st.markdown("### National")
    df_national = st.session_state.attrib[st.session_state.attrib["Numéro National"].notna()].copy()
    
    def style_n(row):
        style_full = []
        if row["Capitaine National"]:
            style_full += ["font-weight: bold; color: darkgreen;", "font-weight: bold; color: darkgreen;"]  # Numéro, Capitaine
        else:
            style_full += ["", ""]
        style_full += ["", "", ""]  # Nom, Prénom, 1ère ligne
        return style_full
    
    cols_display = ["Numéro National", "Nom", "Prénom", "1ère ligne National", "Capitaine National"]
    st.dataframe(
        df_national[cols_display].sort_values("Numéro National").style.apply(style_n, axis=1),
        use_container_width=True,
        height=300
    )

with col_r:
    st.markdown("### Régional")
    df_regional = st.session_state.attrib[st.session_state.attrib["Numéro Régional"].notna()].copy()
    
    def style_r(row):
        style_full = []
        if row["Capitaine Régional"]:
            style_full += ["font-weight: bold; color: darkgreen;", "font-weight: bold; color: darkgreen;"]  # Numéro, Capitaine
        else:
            style_full += ["", ""]
        style_full += ["", "", ""]  # Nom, Prénom, 1ère ligne
        return style_full
    
    cols_display = ["Numéro Régional", "Nom", "Prénom", "1ère ligne Régional", "Capitaine Régional"]
    st.dataframe(
        df_regional[cols_display].sort_values("Numéro Régional").style.apply(style_r, axis=1),
        use_container_width=True,
        height=300
    )

# --- Export Excel ---
def export_excel(df, niveau):
    subset = df[[f"Numéro {niveau}", "Nom", "Prénom", f"1ère ligne {niveau}", f"Capitaine {niveau}"]]
    subset = subset.rename(columns={
        f"Numéro {niveau}": "Numéro",
        f"1ère ligne {niveau}": "1ère ligne",
        f"Capitaine {niveau}": "Capitaine"
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        subset.to_excel(writer, index=False, sheet_name=niveau)
    return output.getvalue()

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        "📥 Exporter National",
        data=export_excel(st.session_state.attrib, "National"),
        file_name="selection_nationale.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
with col2:
    st.download_button(
        "📥 Exporter Régional",
        data=export_excel(st.session_state.attrib, "Régional"),
        file_name="selection_regionale.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
