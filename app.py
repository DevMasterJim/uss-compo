import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Attribution National / Régional", layout="wide")
st.title("🏉 Attribution National & Régional 🏉")

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

# --- Transformation Présence ---
mapping_presence = {"A": "❌", "P": "✅", "C": "❓"}
df["Présence"] = df["Présence"].map(mapping_presence).fillna("")

# --- Ne garder que les lignes valides ---
df = df[(df["Nom"].notna()) & (df["Nom"] != "") &
        (df["Présence"].notna()) & (df["Présence"] != "")].copy()
df = df.reset_index(drop=True)

# --- Ajouter colonnes pour National et Régional ---
for niveau in ["National", "Régional"]:
    df[f"Numéro {niveau}"] = None
    df[f"Capitaine {niveau}"] = False
    df[f"1ère ligne {niveau}"] = None

# --- Initialiser la session ---
if "attrib" not in st.session_state:
    st.session_state.attrib = df.copy()

# --- Interface édition ---
st.subheader("📝 Attribution des numéros et rôles")

# Fonction pour générer les options de numéros disponibles
def get_num_options(attrib, niveau, current_value):
    nums_pris = attrib[f"Numéro {niveau}"].dropna().tolist()
    options = [n for n in range(1, 24) if n not in nums_pris or n == current_value]
    return options

edited_rows = []
attrib = st.session_state.attrib.copy()

for idx, row in attrib.iterrows():
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        options_num = get_num_options(attrib, "National", row["Numéro National"])
        row["Numéro National"] = st.selectbox(
            f"{row['Nom']} - Numéro National",
            options=options_num,
            index=0 if row["Numéro National"] is None else options_num.index(row["Numéro National"]),
            key=f"num_National_{idx}"
        )
    with col2:
        row["Capitaine National"] = st.checkbox(
            "Capitaine",
            value=row["Capitaine National"],
            key=f"cap_National_{idx}"
        )
    with col3:
        row["1ère ligne National"] = st.selectbox(
            "1ère ligne",
            options=["", "G", "D", "T", "GD", "GDT"],
            index=0 if row["1ère ligne National"] == "" else ["", "G", "D", "T", "GD", "GDT"].index(row["1ère ligne National"]),
            key=f"ligne_National_{idx}"
        )
    edited_rows.append(row)

attrib = pd.DataFrame(edited_rows)

# Même chose pour Régional
edited_rows = []
for idx, row in attrib.iterrows():
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        options_num = get_num_options(attrib, "Régional", row["Numéro Régional"])
        row["Numéro Régional"] = st.selectbox(
            f"{row['Nom']} - Numéro Régional",
            options=options_num,
            index=0 if row["Numéro Régional"] is None else options_num.index(row["Numéro Régional"]),
            key=f"num_Régional_{idx}"
        )
    with col2:
        row["Capitaine Régional"] = st.checkbox(
            "Capitaine",
            value=row["Capitaine Régional"],
            key=f"cap_Régional_{idx}"
        )
    with col3:
        row["1ère ligne Régional"] = st.selectbox(
            "1ère ligne",
            options=["", "G", "D", "T", "GD", "GDT"],
            index=0 if row["1ère ligne Régional"] == "" else ["", "G", "D", "T", "GD", "GDT"].index(row["1ère ligne Régional"]),
            key=f"ligne_Régional_{idx}"
        )
    edited_rows.append(row)

attrib = pd.DataFrame(edited_rows)

st.session_state.attrib = attrib

# --- Aperçu récapitulatif vertical ---
st.subheader("📋 Aperçu des joueurs sélectionnés")
col_n, col_r = st.columns(2)

with col_n:
    st.markdown("### National")
    df_national = attrib[attrib["Numéro National"].notna()]
    st.dataframe(
        df_national[["Numéro National", "Nom", "Prénom", "1ère ligne National", "Capitaine National"]],
        use_container_width=True,
        height=300
    )

with col_r:
    st.markdown("### Régional")
    df_regional = attrib[attrib["Numéro Régional"].notna()]
    st.dataframe(
        df_regional[["Numéro Régional", "Nom", "Prénom", "1ère ligne Régional", "Capitaine Régional"]],
        use_container_width=True,
        height=300
    )

# --- Export Excel ---
def export_excel(df, niveau):
    subset = df[["Nom", "Prénom", "Numéro " + niveau, "1ère ligne " + niveau, "Capitaine " + niveau]]
    subset = subset.rename(columns={
        "Numéro " + niveau: "Numéro",
        "1ère ligne " + niveau: "1ère ligne",
        "Capitaine " + niveau: "Capitaine"
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
