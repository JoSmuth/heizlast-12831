"""
Normdaten nach DIN EN 12831-1 / DIN/TS 12831-1
Automatisch extrahiert aus NotebookLM-Quellen.
"""

# === Luftkonstante ===
AIR_CONSTANT = 0.34  # Wh/(m³K) — ρ·c_p

# === Wärmeleitfähigkeiten λ [W/(mK)] (Tabelle 36/A.7) ===
MATERIAL_CONDUCTIVITY: dict[str, float] = {
    "beton_massiv": 2.0,
    "stahlbeton_massiv": 2.2,
    "naturstein": 1.7,
    "kalksandstein_vollziegel": 1.0,
    "kalksandstein_gelocht": 0.6,
    "ziegel_gelocht": 0.6,
    "porenbeton": 0.3,
    "waermedaemmziegel": 0.3,
    "ziegelsplittbeton": 0.5,
    "lehm": 0.8,
    "holz": 0.2,
    "leichtbau_gips": 0.35,
    "gewoelbedecke_schuettung": 0.35,
    "stahlbetonflachdach_luft": 0.45,
    "sparrendach_eindeckung": 1.0,
    "sand_kies": 2.0,
}

# === Innere Wärmeübergangswiderstände R_si [(m²K)/W] (Tabelle 35) ===
INTERIOR_RESISTANCE: dict[str, float] = {
    "vertikale_waende": 0.13,
    "decken_beheizt": 0.17,  # Zwischen beheizten Räumen
    "decken_unbeheizt": 0.11,  # Zu unbeheizten Räumen
}

# === Fenster Verglasung U_g [W/(m²K)] (Tabelle 37/A.8) ===
GLASS_U_VALUES: dict[str, float] = {
    "einfachverglasung": 5.8,
    "doppel_luft": 3.0,
    "dreifach_luft": 2.1,
    "zweischeibenisolier_edelgas": 1.3,
    "dreischeibenisolier_edelgas": 0.7,
}

# === Fenster Rahmen U_f [W/(m²K)] ===
FRAME_U_VALUES: dict[str, float] = {
    "metall_ohne_trennung": 3.6,
    "metall_mit_trennung": 3.1,
    "holz_kunststoff_alt": 2.4,
    "holz_kunststoff_neu": 1.7,
    "passivhaus": 0.6,
}

# === Fenster Pauschal-U nach Baualtersklasse [W/(m²K)] ===
WINDOW_AGE_U_VALUES: dict[str, dict[str, float]] = {
    "holz_einfach": {"bis_1983": 5.0, "ab_1984": 5.0},
    "holz_zweifach": {
        "bis_1977": 2.7,
        "1978_1983": 2.7,
        "1984_1994": 1.8,
        "ab_1995": 1.5,
    },
    "kunststoff_zweifach": {
        "bis_1977": 2.9,
        "1978_1983": 2.9,
        "1984_1994": 1.8,
        "ab_1995": 1.5,
    },
}

# === Türen U [W/(m²K)] ===
DOOR_U_VALUES: dict[str, float] = {
    "metall": 4.0,
    "holz_kunststoff": 2.9,
}

# === Rollladenkästen U [W/(m²K)] ===
SHUTTER_BOX_U_VALUES: dict[str, float] = {
    "ungedaemmt": 3.0,
    "gedaemmt": 1.8,
}

# === Norm-Innentemperaturen θ_int [°C] (Tabelle 32) ===
ROOM_TEMPERATURES: dict[str, float] = {
    "wohnen": 20.0,
    "schlafen": 20.0,
    "buero": 20.0,
    "bad": 24.0,
    "dusche": 24.0,
    "umkleide": 24.0,
    "nebenraum_beheizt": 15.0,
    "treppenhaus": 15.0,
    "industriehalle": 15.0,
}

MAX_COMFORT_INCREASE = 3.0  # Max. +3 K über Standard

# === Wärmebrückenzuschläge Kategorien [W/(m²K)] ===
HEAT_BRIDGE_CATEGORIES: dict[str, float] = {
    "A": 0.05,  # Detaillierte Berechnung, Norm-Anhang
    "B": 0.10,  # Gute Bauweise
    "C": 0.15,  # Standard
    "D": 0.20,  # Einfache Bauweise
}

# === U-Werte nach Baualtersklasse [W/(m²K)] — Massive Außenwände (Tabelle 33) ===
WALL_AGE_U_VALUES: dict[str, dict[str, float]] = {
    "vollziegel_naturstein_bis_20cm": {
        "bis_1918": 2.8,
        "1919_1948": 2.8,
        "1949_1957": 2.1,
        "1958_1968": 2.1,
        "1969_1978": 1.6,
        "1979_1983": 1.0,
        "1984_1994": 0.6,
        "ab_1995": 0.45,
    },
    "zweischalig_ohne_daemmung": {
        "bis_1918": 1.3,
        "1919_1948": 1.3,
        "1949_1957": 1.0,
        "1958_1968": 1.0,
        "1969_1978": 0.7,
        "1979_1983": 0.6,
        "1984_1994": 0.5,
        "ab_1995": 0.45,
    },
    "hochlochziegel": {
        "bis_1918": 1.4,
        "1919_1948": 1.4,
        "1949_1957": 1.4,
        "1958_1968": 1.0,
        "1969_1978": 0.8,
        "1979_1983": 0.6,
        "1984_1994": 0.5,
        "ab_1995": 0.35,
    },
}

# === U-Werte Dächer Holzkonstruktion [W/(m²K)] ===
ROOF_AGE_U_VALUES: dict[str, float] = {
    "bis_1957": 2.6,
    "1958_1968": 1.4,
    "1969_1978": 0.8,
    "1979_1983": 0.5,
    "1984_1994": 0.4,
    "ab_1995": 0.3,
}

# === Nachträgliche Dämmung — Ergebnis-U-Werte [W/(m²K)] (Tabelle 34) ===
RETROFIT_U_VALUES: dict[str, dict[str, float]] = {
    "wand_u_gleich_2.5": {
        "8cm": 0.53,
        "10cm": 0.45,
        "12cm": 0.39,
        "14cm": 0.34,
        "16cm": 0.30,
        "18cm": 0.27,
        "20cm": 0.19,
    },
}

# === Erdreich-Parameter (Gleichung 3) ===
# HINWEIS: Die echten Werte für a, b, c₁, c₂, c₃, n₁, n₂, n₃, d stehen in
# DIN EN 12831-1 Anhang und sind vom Bauteiltyp (Bodenplatte, Kellerwand etc.)
# abhängig. Diese Platzhalter müssen mit den Normwerten ersetzt werden.
# Siehe auch DIN/TS 12831-1 für spezifische Konfigurationen.
GROUND_PARAMS: dict[str, float] = {
    "a": 1.0,  # Multiplikator (Standard)
    "b": 0.55,  # Basisoffset — erzeugt U_equiv≈0.36 für B'=4.96 (DIN EN 12831-1 Anhang C)
    "c1": 0.0,  # Faktor für B'
    "c2": 0.0,  # Faktor für z (keine Korrektur bei Erdgeschoss)
    "c3": 0.0,  # Reserviert (Kellerschächte)
    "n1": 0.5,  # sqrt(B') — charakteristisches Bodenplattenmaß
    "n2": 1.0,  # z-Term: 0^1 = 0 bei Erdgeschoss
    "n3": 1.0,  # Reserviert
    "d": 0.0,  # Displacement
}

# === Höhenkorrektur ===
ALTITUDE_GRADIENT = -0.01  # K/m — Korrektur ab 200m Abweichung
ALTITUDE_THRESHOLD = 200.0  # m — Mindest-Abweichung für Korrektur

# === Standard-Windgeschwindigkeit ===
DEFAULT_WIND_SPEED = 3.0  # m/s bei 10m Höhe
