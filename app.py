import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Attribution National / Régional", layout="wide")
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

# --- Colonnes pour National et Régional ---
for niveau in ["National", "Régional"]:
    df[f"Numéro {niveau}"] = None
    df[f"Capitaine {niveau}"] = False
    df[f"1ère ligne {niveau}"] = ""  # valeur par défaut vide

# --- Initialiser session ---
if "attrib" not in st.session_state:
    st.session_state.attrib = df.copy()

# --- Appliquer règle d'édition uniquement si Nom et Présence remplis ---
editable_rows = st.session_state.attrib["Nom"].notna() & (st.session_state.attrib["Nom"] != "") & \
                st.session_state.attrib["Présence"].notna() & (st.session_state.attrib["Présence"] != "")

# Marquer les colonnes éditables selon la condition
column_config = {
    "Numéro National": st.column_config.SelectboxColumn(options=list(range(1, 24)), required=False, disabled=~editable_rows),
    "Capitaine National": st.column_config.CheckboxColumn(disabled=~editable_rows),
    "1ère ligne National": st.column_config.SelectboxColumn(options=["", "G", "D", "T", "GD", "GDT"], disabled=~editable_rows),
    "Numéro Régional": st.column_config.SelectboxColumn(options=list(range(1, 24)), required=False, disabled=~editable_rows),
    "Capitaine Régional": st.column_config.CheckboxColumn(disabled=~editable_rows),
    "1ère ligne Régional": st.column_config.SelectboxColumn(options=["", "G", "D", "T", "GD", "GDT"], disabled=~editable_rows),
}

edited = st.data_editor(
    st.session_state.attrib,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config=column_config
)

st.session_state.attrib = edited

# --- Export Excel ---
def export_excel(df, niveau):
    subset = df.loc[
        (df["Nom"].notna()) & (df["Nom"] != "") & 
        (df["Présence"].notna()) & (df["Présence"] != ""),
        ["Nom", "Prénom", "Club", "Présence", f"Numéro {niveau}", f"Capitaine {niveau}", f"1ère ligne {niveau}"]
    ]
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
