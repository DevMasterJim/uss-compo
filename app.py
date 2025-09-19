import streamlit as st
import pandas as pd
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

# --- Auto-refresh toutes les 10 secondes ---
count = st_autorefresh(interval=10000, limit=None, key="autorefresh")  # intervalle en ms

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

# --- Transformation Présence ---
mapping_presence = {"A": "❌", "P": "✅", "C": "❔"}
df["Présence"] = df["Présence"].map(mapping_presence).fillna("")

# --- Ne garder que les lignes valides ---
df = df[(df["Nom"].notna()) & (df["Nom"] != "") &
        (df["Présence"].notna()) & (df["Présence"] != "")]
df = df.reset_index(drop=True)

# --- Ajouter colonnes pour National et Régional ---
for niveau in ["National", "Régional"]:
    df[f"Numéro {niveau}"] = None
    df[f"Capitaine {niveau}"] = False
    df[f"1ère ligne {niveau}"] = ""  # vide par défaut

# --- Initialiser session uniquement si pas déjà fait ---
if "attrib" not in st.session_state:
    st.session_state.attrib = df.copy()

# --- Tableau éditable ---
# Copie pour éviter les conflits de session
attrib_copy = st.session_state.attrib.copy()

# Data editor
edited = st.data_editor(
    attrib_copy,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    height=700,
    column_config={
        "Numéro National": st.column_config.SelectboxColumn(options=list(range(1,24)), required=False),
        "Capitaine National": st.column_config.CheckboxColumn(),
        "1ère ligne National": st.column_config.SelectboxColumn(options=["","G","D","T","GD","GDT"]),
        "Numéro Régional": st.column_config.SelectboxColumn(options=list(range(1,24)), required=False),
        "Capitaine Régional": st.column_config.CheckboxColumn(),
        "1ère ligne Régional": st.column_config.SelectboxColumn(options=["","G","D","T","GD","GDT"]),
    }
)

# Écriture **seule** si la variable edited existe
if edited is not None:
    st.session_state.attrib = edited


# --- Sauvegarder les modifications dans la session ---
st.session_state.attrib = edited

# --- Export Excel ---
def export_excel(df, niveau):
    subset = df[["Nom", "Prénom", "Club", f"Numéro {niveau}", f"Capitaine {niveau}", f"1ère ligne {niveau}"]]
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
