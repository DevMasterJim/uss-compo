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

# --- Style pour capitaines : nom et numéro ---
def style_capitaine(row):
    styles = []
    for niveau in ["National", "Régional"]:
        if row[f"Capitaine {niveau}"]:
            # Numéro et Capitaine en vert gras
            styles.append("font-weight: bold; color: darkgreen;")  # Numéro
            styles.append("font-weight: bold; color: darkgreen;")  # Capitaine
        else:
            styles.append("")  # Numéro
            styles.append("")  # Capitaine
    # Colonnes Nom, Prénom neutres
    style_full = ["", ""]  # Nom, Prénom
    style_full += [styles[0]]  # Numéro National
    style_full += [styles[1]]  # Capitaine National
    style_full += [""]  # 1ère ligne National
    style_full += [styles[2]]  # Numéro Régional
    style_full += [styles[3]]  # Capitaine Régional
    style_full += [""]  # 1ère ligne Régional
    return style_full

# --- Vue récapitulative non éditable ---
st.subheader("📋 Aperçu des joueurs et affectations")
display_cols = ["Nom", "Prénom",
                "Numéro National", "Capitaine National", "1ère ligne National",
                "Numéro Régional", "Capitaine Régional", "1ère ligne Régional"]

st.dataframe(
    st.session_state.attrib[display_cols].sort_values("Nom").style.apply(style_capitaine, axis=1),
    use_container_width=True,
    height=300
)

st.markdown("---")

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
