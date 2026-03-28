"""
Web-GUI für Heizlast-Rechentool
FastAPI Backend mit Jinja2 Templates
Normgerechte Berechnung nach DIN EN 12831-1
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from pathlib import Path
import sys
import math

# Projekt-Root finden
HERE = Path(__file__).resolve()
SRC_DIR = HERE.parent.parent
PROJECT_ROOT = SRC_DIR.parent
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

# Pfad für Imports
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from heizlast.calc.transmission import calc_transmission_loss
    from heizlast.calc.ventilation import calc_ventilation_loss, calc_minimum_airflow
    from heizlast.calc.time_constant import calc_time_constant, calc_theta_correction
    from heizlast.data.climate_data import get_climate_data
    HAS_CALC_MODULES = True
except ImportError:
    HAS_CALC_MODULES = False

app = FastAPI(title="Heizlast-Rechentool DIN EN 12831-1")

# Static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ==================== DIN EN 12831-1 KONSTANTEN ====================

# Raumart-Temperaturen (°C) nach DIN EN 12831-1 Anhang A
ROOM_TYPE_TEMPS = {
    "wohnraum": 20,
    "schlafzimmer": 20,
    "buero": 20,
    "kueche": 20,
    "bad": 24,
    "dusche": 24,
    "umkleide": 24,
    "nebenraum": 15,
    "treppenhaus": 15,
    "halle": 15,
}

# Lüftungshäufigkeit nach Raumart (Anpassungsfaktor)
VENTILATION_USAGE_FACTORS = {
    "wohnraum": 0.5,
    "schlafzimmer": 0.5,
    "buero": 0.5,
    "kueche": 0.7,
    "bad": 1.0,
    "dusche": 1.0,
    "umkleide": 0.7,
    "nebenraum": 0.3,
    "treppenhaus": 0.3,
    "halle": 0.3,
}

# Abschirmungsfaktoren für Windrichtungswärmebrücken
SHIELDING_FACTORS = {
    "frei": 0.0,     # exponierte Lage
    "mittel": 0.015,  # normale Bebauung
    "stark": 0.025,   # Innenstadtlage, starke Bebauung
}

# Grenzwerte für angrenzende Temperaturen (°C)
ADJACENT_TEMPS = {
    "aussenluft": None,          # wird aus Klimadaten berechnet
    "erdreich": 10,              # mittlere Erdreichtemperatur
    "unbeheizt": 10,             # unbeheizter Raum
    "beheizt": 20,               # beheizter Raum
    "angrenzend": None,          # manuelle Eingabe
}

# Luftdichte ρ_L in kg/m³
RHO_AIR = 1.2
# Spezifische Wärmekapazität c_p in Wh/(kg·K)
CP_AIR = 0.28  # ca. 1000 J/(kg·K) = 0.28 Wh/(kg·K)


# ==================== PYDANTIC MODELLE ====================

class VentilationInput(BaseModel):
    has_system: bool = False
    supply_air: float = 0.0          # m³/h
    exhaust_air: float = 0.0         # m³/h
    transfer_air: float = 0.0        # m³/h
    tech_air: float = 0.0            # m³/h
    has_wrg: bool = False
    wrg_efficiency: float = 0.0      # 0..1


class ElementInput(BaseModel):
    name: str
    type: str = "aussenwand"
    area: float = 0.0
    u_value: float = 0.0             # inkl. Wärmebrückenzuschlag
    u_value_base: float = 0.0        # ohne Wärmebrücke
    delta_u_tb: float = 0.0
    adjacent_to: str = "aussenluft"
    adjacent_temp: Optional[float] = None
    orientation: str = "N"
    is_ground_contact: bool = False
    glass_u_value: Optional[float] = None
    frame_u_value: Optional[float] = None
    perimeter: Optional[float] = None
    depth: Optional[float] = None


class RoomInput(BaseModel):
    name: str
    type: str = "wohnraum"
    area: float = 0.0
    height: float = 2.5
    volume: float = 0.0
    theta_int: float = 20.0
    comfort_requirement: bool = False
    elements: List[ElementInput] = []
    ventilation: Optional[VentilationInput] = None


class BuildingInput(BaseModel):
    plz: str
    name: str = "Mein Gebäude"
    gross_volume: float = 0.0        # m³
    floor_area: float = 0.0          # m²
    envelope_area: float = 0.0       # m²
    thermal_bridge_class: str = "B"
    delta_u_tb: float = 0.10
    air_tightness_class: str = "B"
    n50: float = 2.0                 # h⁻¹
    facades: int = 2
    shielding: str = "mittel"
    heat_storage_category: str = "mittel"
    effective_heat_capacity: float = 10000.0  # Wh/K
    rooms: List[RoomInput] = []


# ==================== BERECHNUNGSFUNKTIONEN ====================

def get_adjacent_temp(element: ElementInput, building: BuildingInput, theta_e: float) -> float:
    """
    Bestimmt die angrenzende Temperatur je nach 'Grenzt an' Kategorie.
    """
    if element.adjacent_to == "aussenluft":
        return theta_e
    elif element.adjacent_to == "erdreich":
        return 10.0
    elif element.adjacent_to == "unbeheizt":
        return 10.0
    elif element.adjacent_to == "beheizt":
        return 20.0
    elif element.adjacent_to == "angrenzend" and element.adjacent_temp is not None:
        return element.adjacent_temp
    else:
        return theta_e


def calc_transmission_element(element: ElementInput, theta_int: float, theta_adj: float) -> float:
    """
    Berechnet den Transmissionswärmeverlust eines Bauteils nach DIN EN 12831-1.
    Φ_T = A · (U + ΔU_TB) · (θ_int - θ_adj)
    """
    u_total = element.u_value
    # Für Fenster: gewichtete U-Werte berücksichtigen
    if element.type == "fenster" and element.glass_u_value and element.frame_u_value:
        # Annahme: 70% Glasanteil, 30% Rahmen
        u_total = 0.7 * element.glass_u_value + 0.3 * element.frame_u_value + element.delta_u_tb

    # Für Bodenplatte auf Erdreich: Berechnung nach Umfang/Tiefe-Methode
    if element.type == "bodenplatte" and element.adjacent_to == "erdreich":
        if element.perimeter and element.depth is not None:
            u_total = calc_ground_floor_u_value(element.perimeter, element.depth, element.area)

    phi_t = element.area * u_total * (theta_int - theta_adj)
    return max(phi_t, 0)  # nur positive Werte (Heizfall)


def calc_ground_floor_u_value(perimeter: float, depth: float, area: float) -> float:
    """
    Berechnet den U-Wert einer Bodenplatte auf Erdreich nach DIN EN 12831-1.
    U_fg = 2 · λ_g / (π · (B/2 + z)) · ln(π · B / (2 · z) + 1)
    Vereinfachte Berechnung: U ≈ 0.35 · (P / A) für z = 0.5m
    """
    if area <= 0:
        return 0.5
    # Lambda_g für Boden: ca. 2.0 W/(m·K)
    lambda_g = 2.0
    if depth <= 0:
        depth = 0.5

    # Formel nach Norm
    # Charakteristische Länge B = A / (0.5 * P)
    if perimeter <= 0:
        return 0.5

    b = area / (0.5 * perimeter)

    if b <= 0:
        return 0.5

    ln_arg = (math.pi * b) / (2 * depth) + 1
    if ln_arg <= 0:
        return 0.5

    u_fg = (2 * lambda_g) / (math.pi * (b / 2 + depth)) * math.log(ln_arg)
    return max(u_fg, 0.1)


def calc_ventilation_room(room: RoomInput, theta_e: float, building: BuildingInput) -> float:
    """
    Berechnet den Lüftungswärmeverlust eines Raumes nach DIN EN 12831-1.
    Φ_V = 0.34 · q_v · (θ_int - θ_e)
    mit q_v = max(n_min · V, q_sup + q_exh + q_trans + q_tech)
    """
    theta_int = room.theta_int
    if room.comfort_requirement:
        theta_int += 3.0

    volume = room.area * room.height

    # Mindestaußenluftvolumenstrom nach Raumart
    usage_factor = VENTILATION_USAGE_FACTORS.get(room.type, 0.5)
    # Grundwechsel 0.1 l/(s·m²) = 0.36 m³/(h·m²) für Wohnräume
    n_min = usage_factor * 0.5  # pauschal 0.5 h⁻¹ mal Nutzungsfaktor
    q_min = n_min * volume

    if room.ventilation and room.ventilation.has_system:
        # Mechanische Lüftung
        q_supply = room.ventilation.supply_air
        q_exhaust = room.ventilation.exhaust_air
        q_transfer = room.ventilation.transfer_air
        q_tech = room.ventilation.tech_air
        q_total = max(q_min, q_supply + q_exhaust + q_transfer + q_tech)
    else:
        # Natürliche Lüftung über Infiltration
        # Verwendung der Gebäude-Luftwechselrate
        n_infiltration = building.n50 * 0.07  # n_50 × Leckagefaktor
        q_infiltration = n_infiltration * volume
        q_total = max(q_min, q_infiltration)

    # WRG-Berücksichtigung
    theta_eff = theta_e
    if room.ventilation and room.ventilation.has_wrg and room.ventilation.has_system:
        eta_rec = room.ventilation.wrg_efficiency
        # Effektive Außentemperatur nach WRG
        theta_eff = theta_e + eta_rec * (theta_int - theta_e)

    phi_v = 0.34 * q_total * (theta_int - theta_eff)
    return max(phi_v, 0)


def calc_shielding_correction(building: BuildingInput) -> float:
    """
    Berechnet die Abschirmungskorrektur für die Temperatur.
    """
    factor = SHIELDING_FACTORS.get(building.shielding, 0.015)
    return factor


def calc_time_constant_local(c_eff: float, h_t: float, h_v: float) -> float:
    """
    Berechnet die Gebäude-Zeitkonstante nach DIN EN 12831-1.
    τ = C_eff / (H_T + H_V)
    """
    h_total = h_t + h_v
    if h_total <= 0:
        return 0
    return c_eff / h_total


def calc_theta_correction_local(theta_e: float, tau: float) -> float:
    """
    Berechnet die korrigierte Außentemperatur nach der Zeitkonstante.
    Vereinfacht: für τ > 6h wird eine Korrektur angewendet.
    """
    # Näherung nach DIN EN 12831-1 Anhang F
    if tau <= 6:
        return theta_e
    elif tau >= 100:
        return theta_e + 4.0
    else:
        # Logarithmische Interpolation
        return theta_e + 4.0 * (math.log(tau / 6) / math.log(100 / 6))


# ==================== ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Startseite mit Eingabeformular"""
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/api/calculate")
async def calculate(building: BuildingInput):
    """Berechne Heizlast für alle Räume nach DIN EN 12831-1"""
    try:
        # Klimadaten laden
        if HAS_CALC_MODULES:
            climate = get_climate_data(building.plz)
            theta_e = climate.theta_e_ref
        else:
            # Fallback: geschätzte Außentemperatur nach PLZ-Region
            theta_e = get_theta_e_fallback(building.plz)

        # Abschirmungskorrektur
        delta_theta_shielding = calc_shielding_correction(building)

        results = []
        total_ht = 0.0
        total_hv = 0.0

        for room in building.rooms:
            theta_int_effective = room.theta_int
            if room.comfort_requirement:
                theta_int_effective += 3.0

            # Transmissionswärmeverlust
            phi_t_total = 0.0
            for element in room.elements:
                theta_adj = get_adjacent_temp(element, building, theta_e)
                phi_t = calc_transmission_element(element, theta_int_effective, theta_adj)
                phi_t_total += phi_t

            # Wärmebrückenzuschlag für gesamten Raum (nach Hüllfläche)
            # ΔΦ_TB = A_env_room × ΔU_TB × ΔT
            room_envelope = sum(
                e.area for e in room.elements
                if e.type in ("aussenwand", "dach", "bodenplatte", "fenster", "tuer", "kellerdecke")
            )
            phi_tb = room_envelope * building.delta_u_tb * (theta_int_effective - theta_e)

            # Lüftungswärmeverlust
            phi_v = calc_ventilation_room(room, theta_e, building)

            # Korrigierte Temperatur
            phi_t_total += phi_tb

            # Raum-Heizleistung H_T und H_V
            delta_t = theta_int_effective - theta_e
            h_t_room = phi_t_total / delta_t if delta_t != 0 else 0
            h_v_room = phi_v / delta_t if delta_t != 0 else 0

            total_ht += h_t_room
            total_hv += h_v_room

            phi_total = phi_t_total + phi_v

            results.append({
                "name": room.name,
                "area": round(room.area, 1),
                "volume": round(room.volume or room.area * room.height, 1),
                "theta_int": round(theta_int_effective, 1),
                "phi_t": round(phi_t_total, 1),
                "phi_v": round(phi_v, 1),
                "phi_total": round(phi_total, 1),
                "h_t": round(h_t_room, 2),
                "h_v": round(h_v_room, 2),
            })

        # Zeitkonstante
        tau = calc_time_constant_local(
            building.effective_heat_capacity, total_ht, total_hv
        )

        # Korrigierte Außentemperatur
        theta_e_corr = calc_theta_correction_local(theta_e, tau)

        # Abschirmungskorrektur
        theta_e_corr -= delta_theta_shielding

        return {
            "success": True,
            "climate": {
                "plz": building.plz,
                "theta_e": round(theta_e, 1),
                "theta_e_corrected": round(theta_e_corr, 1),
                "shielding_correction": round(delta_theta_shielding, 3),
            },
            "building": {
                "name": building.name,
                "tau": round(tau, 1),
                "c_eff": building.effective_heat_capacity,
                "delta_u_tb": building.delta_u_tb,
                "n50": building.n50,
                "shielding": building.shielding,
            },
            "rooms": results,
            "totals": {
                "h_t": round(total_ht, 1),
                "h_v": round(total_hv, 1),
                "phi_total": round(sum(r["phi_total"] for r in results), 1),
                "phi_t_total": round(sum(r["phi_t"] for r in results), 1),
                "phi_v_total": round(sum(r["phi_v"] for r in results), 1),
            },
        }

    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}


def get_theta_e_fallback(plz: str) -> float:
    """
    Fallback-Außentemperatur nach PLZ-Bereichen.
    Vereinfachte Zuordnung zu Klimazonen in Deutschland.
    """
    try:
        plz_int = int(plz[:2])
    except ValueError:
        return -10.0

    # Referenz-Außentemperatur nach PLZ-Bereichen (°C)
    # Werte nach DIN 4710 / TRY-Daten
    plz_temps = {
        # Norddeutschland
        range(0, 15): -8.0,
        range(15, 28): -7.0,
        # Nordrhein-Westfalen
        range(28, 40): -8.0,
        # Niedersachsen / Bremen
        range(40, 50): -9.0,
        # Hessen / Mitte
        range(50, 62): -10.0,
        # Rheinland-Pfalz / Saarland
        range(62, 70): -8.0,
        # Baden-Württemberg
        range(70, 80): -9.0,
        # Bayern
        range(80, 90): -11.0,
        range(90, 100): -12.0,
    }

    for rng, temp in plz_temps.items():
        if plz_int in rng:
            return temp

    return -10.0  # Standardwert


@app.get("/api/climate/{plz}")
async def get_climate(plz: str):
    """Gibt Klimadaten für eine PLZ zurück"""
    try:
        if HAS_CALC_MODULES:
            climate = get_climate_data(plz)
            return {
                "success": True,
                "plz": plz,
                "theta_e": climate.theta_e_ref,
            }
        else:
            return {
                "success": True,
                "plz": plz,
                "theta_e": get_theta_e_fallback(plz),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/room-types")
async def get_room_types():
    """Gibt alle unterstützten Raumarten mit Temperaturen zurück"""
    return {
        "success": True,
        "room_types": [
            {"key": k, "temp": v, "label": f"{k.replace('_', ' ').title()} ({v}°C)"}
            for k, v in ROOM_TYPE_TEMPS.items()
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
