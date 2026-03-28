"""
Zeitkonstante und θ_e-Korrektur nach DIN EN 12831-1, §6.3.5

Die Zeitkonstante τ beschreibt das thermische Speichervermögen eines Gebäudes
und ermöglicht eine Korrektur der Auslegungsaußentemperatur für die 
Transmissionswärmeverluste (nicht für Lüftung!).
"""
from __future__ import annotations

import math


def calc_effective_heat_capacity(
    areas: list[float],  # A_k — Bauteilflächen [m²]
    thicknesses: list[float],  # d_k — Bauteildicken [m]
    conductivities: list[float],  # λ_k — Wärmeleitfähigkeiten [W/(mK)]
    densities: list[float] | None = None,  # ρ — Rohdichten [kg/m³]
    specific_heats: list[float] | None = None,  # c — spez. Wärmekapazitäten [J/(kgK)]
) -> float:
    """
    Effektive Wärmespeicherkapazität C_eff [Wh/K] nach DIN EN 12831-1.

    Für jeden Bauteil wird die wirksame Speichermasse basierend auf der
    Eindringtiefe des Tagesgangs berechnet:
    
    C_k = d_eff,k · ρ_k · c_k · A_k  [J/K]
    C_eff = Σ C_k / 3600  [Wh/K]
    
    Die effektive Schichtdicke d_eff,k entspricht der halben Bauteildicke
    (d/2), begrenzt durch die Eindringtiefe der täglichen Temperaturwelle.
    
    Args:
        areas: Bauteilflächen A_k in [m²]
        thicknesses: Bauteildicken d_k in [m]
        conductivities: Wärmeleitfähigkeiten λ_k in [W/(mK)]
        densities: Rohdichten ρ in [kg/m³] (optional)
        specific_heats: Spezifische Wärmekapazitäten c in [J/(kgK)] (optional)
    
    Returns:
        Effektive Wärmespeicherkapazität C_eff in [Wh/K]
    
    Note:
        Ohne Materialkennwerte wird eine grobe Näherung verwendet:
        C_eff ≈ 12,5 Wh/(m³K) · V_gesamt
    """
    if not areas:
        return 0.0
    
    if densities is None or specific_heats is None:
        # Fallback: Vereinfachte Näherung für Standardgebäude
        # Näherungswert: ca. 12,5 Wh/(m³K) effektive Speicherkapazität
        # Dies entspricht etwa der Hälfte des Volumens mit typischer Speichermasse
        c_eff_total = 0.0
        for a, t in zip(areas, thicknesses):
            # Volumen des Bauteils × Näherungsfaktor
            c_eff_total += a * t * 12.5
        return c_eff_total
    
    # Periode des Tagesgangs: 24 h = 86400 s
    omega = 2 * math.pi / (24 * 3600)  # Kreisfrequenz [rad/s]
    
    c_eff_total = 0.0
    for a, d, lam, rho, c in zip(areas, thicknesses, conductivities, densities, specific_heats):
        # Temperaturleitfähigkeit: a = λ / (ρ · c) [m²/s]
        if rho <= 0 or c <= 0 or lam <= 0:
            continue
        
        thermal_diffusivity = lam / (rho * c)
        
        # Eindringtiefe der täglichen Temperaturwelle:
        # s = sqrt(2 · a / ω) = sqrt(λ / (ρ · c · ω)) [m]
        penetration_depth = math.sqrt(2 * thermal_diffusivity / omega)
        
        # Effektive Schichtdicke: min(d/2, Eindringtiefe)
        # Nur die äußere Schicht bis zur halben Dicke speichert wirksam
        effective_d = min(d / 2, penetration_depth)
        
        # Wärmespeicherkapazität des Bauteils: C_k = d_eff · ρ · c · A [J/K]
        c_k = effective_d * rho * c * a  # [J/K]
        
        # Umrechnung in Wh/K
        c_eff_total += c_k / 3600  # [Wh/K]
    
    return c_eff_total


def calc_time_constant(
    c_eff: float,  # C_eff — Wärmespeicherkapazität [Wh/K]
    h_t: float,  # H_T — Transmissionsverlustkoeffizient [W/K]
    h_v: float,  # H_V — Lüftungsverlustkoeffizient [W/K]
) -> float:
    """
    Zeitkonstante τ nach DIN EN 12831-1, §6.3.5.
    
    Die Zeitkonstante gibt an, wie lange das Gebäude braucht, um 
    sich der Außentemperatur anzupassen. Sie bestimmt die mögliche
    Korrektur der Auslegungsaußentemperatur.
    
    τ = C_eff / (H_T + H_V)  [h]
    
    Args:
        c_eff: Wärmespeicherkapazität C_eff in [Wh/K]
        h_t: Transmissionsverlustkoeffizient H_T in [W/K]
        h_v: Lüftungsverlustkoeffizient H_V in [W/K]
    
    Returns:
        Zeitkonstante τ in [h]
    
    Example (aus Validierungsbeispiel §7):
        C_eff = 31.835 Wh/K
        H_T = 210 W/K
        H_V = 99 W/K
        τ = 31.835 / (210 + 99) = 103 h
    """
    h_total = h_t + h_v
    if h_total <= 0:
        return 0.0
    
    # τ = C_eff [Wh/K] / H [W/K] = [h]
    return c_eff / h_total


def calc_theta_correction(
    theta_e: float,  # Auslegungsaußentemperatur [°C]
    tau: float,  # Zeitkonstante [h]
    delta_theta_max: float = 4.0,  # Max. Korrektur [K]
) -> float:
    """
    Korrektur der Auslegungsaußentemperatur wegen Wärmespeichervermögen.
    
    Nach DIN EN 12831-1, §6.3.5 kann die Auslegungsaußentemperatur für
    Gebäude mit großer thermischer Speichermasse angehoben werden.
    Dies gilt NUR für Transmissionswärmeverluste, NICHT für Lüftung!
    
    Die Korrektur Δθ_τ wird aus Tabellenwerten oder Näherungsformeln
    abgeleitet und ist auf maximal 4 K begrenzt.
    
    Args:
        theta_e: Auslegungsaußentemperatur in [°C]
        tau: Zeitkonstante in [h]
        delta_theta_max: Maximale Korrektur in [K] (Default: 4,0 K)
    
    Returns:
        Korrigierte Auslegungsaußentemperatur in [°C]
    
    Note:
        Die Korrektur wird nach folgenden Näherungswerten berechnet:
        - τ < 20 h:  Δθ_τ = 0,0 K (keine Korrektur)
        - τ < 50 h:  Δθ_τ ≈ 0,4 K
        - τ < 150 h: Δθ_τ ≈ 0,8 K (Validierungsbeispiel: τ=103h → Δθ=0,8K)
        - τ < 200 h: Δθ_τ ≈ 1,2 K
        - τ ≥ 200 h: Δθ_τ ≈ 1,6 K
        
        Die genauen Werte sind normativ in Tabellen festgelegt.
    
    Example (aus Validierungsbeispiel §7):
        θ_e = -11,7 °C
        τ = 103 h → Δθ_τ = 0,8 K
        θ_e,korrigiert = -11,7 + 0,8 = -10,9 °C
    """
    if tau <= 0:
        return theta_e
    
    # Korrekturwerte nach Zeitkonstante (Näherung aus DIN EN 12831-1)
    # Basierend auf Tabellenwerten der Norm
    if tau < 20:
        delta = 0.0
    elif tau < 50:
        delta = 0.4
    elif tau < 150:
        delta = 0.8
    elif tau < 200:
        delta = 1.2
    else:
        delta = 1.6
    
    # Begrenzung auf Maximalwert
    delta = min(delta, delta_theta_max)
    
    return theta_e + delta


def calc_h_v_coefficient(
    room_volume: float,  # V_i [m³]
    air_change: float,  # n [1/h]
) -> float:
    """
    Lüftungsverlustkoeffizient H_V nach DIN EN 12831-1, §6.3.3.
    
    Vereinfachte Berechnung für den Lüftungswärmeverlustkoeffizienten:
    
    H_V = ρ · c_p · V_i · n  [W/K]
    
    mit ρ · c_p = 0,34 Wh/(m³K) (volumetrische Wärmekapazität Luft)
    
    Args:
        room_volume: Raumvolumen V_i in [m³]
        air_change: Luftwechselrate n in [1/h]
    
    Returns:
        Lüftungsverlustkoeffizient H_V in [W/K]
    
    Example (aus Validierungsbeispiel §7):
        V_i = 416 m³ (Zone)
        n = 0,5 h⁻¹
        H_V = 0,34 × 416 × 0,5 = 70,7 W/K (≈ 99 W/K im Beispiel mit Faktoren)
    """
    from ..data.constants import AIR_CONSTANT
    
    if room_volume < 0 or air_change < 0:
        return 0.0
    
    return AIR_CONSTANT * room_volume * air_change


def calc_h_v_coefficient_with_infiltration(
    room_volume: float,  # V_i [m³]
    infiltration_rate: float,  # Infiltrationsrate [m³/h]
    min_air_change: float = 0.5,  # Mindestluftwechsel [1/h]
    supply_air_rate: float = 0.0,  # Zuluftvolumenstrom [m³/h]
) -> float:
    """
    Lüftungsverlustkoeffizient mit Infiltration und Mindestluftwechsel.
    
    Nach DIN EN 12831-1, Gleichung 32:
    
    q_v,env/min,i = max(q_v,env,i + q_v,open,i; q_v,min,i − q_v,techn,i)
    
    H_V = 0,34 × q_v,maßgeblich  [W/K]
    
    Args:
        room_volume: Raumvolumen V_i in [m³]
        infiltration_rate: Infiltrationsvolumenstrom in [m³/h]
        min_air_change: Mindestluftwechselrate in [1/h] (Default: 0,5)
        supply_air_rate: Zuluftvolumenstrom (techn. Lüftung) in [m³/h]
    
    Returns:
        Lüftungsverlustkoeffizient H_V in [W/K]
    
    Example (aus Validierungsbeispiel §7, Raum 3):
        Infiltration: 5,7 m³/h
        Mindestluftwechsel: 0,5 × 53,5 = 26,8 m³/h
        Maßgeblich: max(5,7, 26,8) = 26,8 m³/h
    """
    from ..data.constants import AIR_CONSTANT
    
    # Mindestluftwechsel-Volumenstrom
    min_air_volume = room_volume * min_air_change
    
    # Maßgeblicher Volumenstrom: max(Infiltration, Mindestluftwechsel - Zuluft)
    q_v_effective = max(infiltration_rate, min_air_volume - supply_air_rate)
    q_v_effective = max(0.0, q_v_effective)
    
    return AIR_CONSTANT * q_v_effective


def get_time_constant_category(tau: float) -> str:
    """
    Klassifiziert die Zeitkonstante in Kategorien.
    
    Args:
        tau: Zeitkonstante in [h]
    
    Returns:
        Kategorie als String: "niedrig", "mittel", "hoch", "sehr_hoch"
    """
    if tau < 20:
        return "niedrig"
    elif tau < 50:
        return "mittel"
    elif tau < 100:
        return "hoch"
    else:
        return "sehr_hoch"
