import pandas as pd
import streamlit as st

# ░█▀█░█▀█░█▀▄░█▀▀░▀█▀░█▀█░█▀█
st.set_page_config(page_title="Unterkunftsbewertung", layout="wide")
st.title("🏡 Intelligente Unterkunftsbewertung & Preisoptimierung")

# 🔹 Upload
file = st.file_uploader("Lade deine Unterkunftsdaten hoch (CSV oder Excel)", type=["csv", "xlsx"])

# 🔹 Gewichtung
st.sidebar.header("⚙️ Gewichtung anpassen (1–5)")
gewichtung = {
    "Fahrtzeit": st.sidebar.slider("Fahrtzeit zur Arbeit", 1, 5, 5),
    "Facilities": st.sidebar.slider("Ausstattung / Facilities", 1, 5, 3),
    "Kosten": st.sidebar.slider("Gesamtkosten", 1, 5, 3),
    "Küche": st.sidebar.slider("Küche / Pantry", 1, 5, 4),
    "Fitness": st.sidebar.slider("Fitnessstudio", 1, 5, 3),
    "Größe": st.sidebar.slider("Platzangebot", 1, 5, 3),
    "Internet": st.sidebar.slider("Internetqualität", 1, 5, 4),
    "Umgebung": st.sidebar.slider("Umgebung / Lagequalität", 1, 5, 2),
}

# Bewertungshilfen
def bewertung_kosten(w): return 5 if w <= 8000 else 4 if w <= 9500 else 3 if w <= 11000 else 2 if w <= 12500 else 1
def bewertung_fahrtzeit(m): return 5 if m <= 50 else 4 if m <= 55 else 3 if m <= 60 else 2 if m <= 65 else 1
def bewertung_größe(t):
    t = str(t).lower()
    if "3 sz" in t: return 5
    elif "2 sz" in t: return 4
    elif "1 sz" in t: return 3
    elif "studio" in t or "hotelzimmer" in t: return 2
    else: return 1

mapper = {
    "Küche": {"Ja": 5, "Ja (vollständig)": 5, "Ja (Pantry)": 4, "Ja (teilweise)": 3, "Teilweise": 3, "Nein": 1},
    "Fitness": {"eigenes Fitnessstudio": 5, "nahe B_Fit & Optimo": 4, "nahe Fitness Time": 3, "–": 1},
    "Internet": {"hoch": 5, "mittel": 3, "niedrig": 1},
    "Facilities": {"hoch": 5, "mittel": 3, "einfach": 1},
    "Umgebung": {"hoch": 4, "durchschnittlich": 3, "wenig": 2}
}

# Rabattstaffel
def rabatt(laufzeit):
    return 0.12 if laufzeit >= 6 else 0.07 if laufzeit >= 3 else 0

# 🔹 Verarbeitung
if file:
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    df["Score_Kosten"] = df["Gesamtkosten (SAR/Monat)"].apply(bewertung_kosten)
    df["Score_Fahrtzeit"] = df["Fahrtzeit zur Arbeit (Min)"].apply(bewertung_fahrtzeit)
    df["Score_Größe"] = df["Platzangebot"].apply(bewertung_größe)

    for k in ["Küche", "Fitness", "Internet", "Facilities", "Umgebung"]:
        df[f"Score_{k}"] = df[k].map(mapper[k]).fillna(2)

    df["Gesamt-Score"] = (
        df["Score_Fahrtzeit"] * gewichtung["Fahrtzeit"] +
        df["Score_Facilities"] * gewichtung["Facilities"] +
        df["Score_Kosten"] * gewichtung["Kosten"] +
        df["Score_Küche"] * gewichtung["Küche"] +
        df["Score_Fitness"] * gewichtung["Fitness"] +
        df["Score_Größe"] * gewichtung["Größe"] +
        df["Score_Internet"] * gewichtung["Internet"] +
        df["Score_Umgebung"] * gewichtung["Umgebung"]
    )

    # Rabatt-Simulation
    for mon in [3, 6]:
        r = rabatt(mon)
        df[f"Optimierte Miete ({mon}M)"] = df["Miete (SAR)"] * (1 - r)
        df[f"Optimierte Gesamtkosten ({mon}M)"] = (
            df[f"Optimierte Miete ({mon}M)"] + df["Transportkosten (SAR)"] + df["Fitnessstudio-Kosten (SAR)"]
        )
        df[f"Ersparnis/Monat ({mon}M)"] = df["Gesamtkosten (SAR/Monat)"] - df[f"Optimierte Gesamtkosten ({mon}M)"]

    st.success(f"{len(df)} Einträge erfolgreich bewertet.")
    st.dataframe(df.sort_values("Gesamt-Score", ascending=False), use_container_width=True)

    st.download_button("⬇️ Ergebnis als Excel speichern", df.to_excel(index=False, engine="openpyxl"), file_name="Bewertete_Unterkuenfte.xlsx")
