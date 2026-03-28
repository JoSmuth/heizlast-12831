"""
Aufheizzuschlag nach DIN EN 12831-1 §6.3.5 / Gleichung 44.

Berechnung der zusätzlichen Leistung für Wiederaufheizung
nach einer Absenkphase.
"""

from __future__ import annotations
import math

from ..data.constants import AIR_CONSTANT


def calc_heating_up_power(
    theta_int: float,
    theta_e: float,
    h_t: float,
    h_v: float,
    c_eff: float,
    area: float,
    n_sb: float = 0.1,
    t_sb: float = 6.0,
    t_hu: float = 2.0,
) -> dict[str, float]:
    """
    Aufheizzuschlag nach DIN EN 12831-1.

    Berechnung:
    1. τ_sb = C_eff / (H_T + H_V,sb)
       mit H_V,sb = ρ·c_p · n_sb · V
    2. Δθ_sb = (θ_int - θ_e) · (1 - e^(-t_sb/τ_sb))
    3. Φ_hu = H_12 · Δθ_sb · (C_eff / (H_12 · t_hu) + 1)
    
    Rückgabe: Dictionary mit allen Zwischenergebnissen.
    """
    if area <= 0:
        raise ValueError("Grundfläche muss > 0 sein")

    # H_V während Absenkung
    # Vereinfacht: H_V,sb = ρ·c_p · n_sb · V
    # V wird aus H_V bei Normbetrieb extrapoliert
    h_v_sb = h_v * (n_sb / 0.5) if h_v > 0 else 0.0

    # Zeitkonstante während Absenkung
    h_total_sb = h_t + h_v_sb
    if h_total_sb <= 0:
        raise ValueError("Wärmeverlustkoeffizienten müssen > 0 sein")
    tau_sb = c_eff / h_total_sb

    # Temperaturabfall während Absenkung
    delta_theta_sb = (theta_int - theta_e) * (1 - math.exp(-t_sb / tau_sb))

    # Aufheizleistung
    # Vereinfachte Formel: Φ_hu = (C_eff · Δθ_sb) / t_hu + H_12 · Δθ_sb
    h_12 = h_t + h_v  # bei Normbetrieb
    phi_hu_total = (c_eff * delta_theta_sb) / t_hu + h_12 * delta_theta_sb

    # Spezifische Aufheizleistung
    phi_hu_specific = phi_hu_total / area

    return {
        "h_v_sb": round(h_v_sb, 2),
        "tau_sb": round(tau_sb, 1),
        "delta_theta_sb": round(delta_theta_sb, 1),
        "phi_hu_total": round(phi_hu_total, 1),
        "phi_hu_specific": round(phi_hu_specific, 1),
    }


def calc_comfort_surchage(
    theta_int: float,
    theta_int_comfort: float,
    elements: list,
    theta_e: float,
    delta_u_tb: float = 0.0,
    q_v_env_min: float = 0.0,
    air_constant: float = AIR_CONSTANT,
) -> float:
    """
    Komfortzuschlag nach Gleichung 43.

    ΔΦ_HL,i,comf = Φ_HL,i(θ_int,comf) - Φ_HL,i(θ_int,stand)
    """
    from .room_load import calc_room_heating_load

    # Heizlast bei Standardtemperatur
    hl_stand = calc_room_heating_load(
        elements=elements,
        theta_int=theta_int,
        theta_e=theta_e,
        delta_u_tb=delta_u_tb,
        q_v_env_min=q_v_env_min,
        air_constant=air_constant,
    )

    # Heizlast bei Komforttemperatur
    hl_comfort = calc_room_heating_load(
        elements=elements,
        theta_int=theta_int_comfort,
        theta_e=theta_e,
        delta_u_tb=delta_u_tb,
        q_v_env_min=q_v_env_min,
        air_constant=air_constant,
    )

    return round(hl_comfort - hl_stand, 1)
