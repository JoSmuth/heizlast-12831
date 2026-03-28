""" Transmissionswärmeverluste nach DIN EN 12831-1, §6.3.2 """
from __future__ import annotations
from typing import TYPE_CHECKING

from ..data.constants import (
    HEAT_BRIDGE_CATEGORIES,
    GROUND_PARAMS,
)

if TYPE_CHECKING:
    from ..models.element import Element
    from ..models.building import Room


def calc_heat_bridge_increment(
    category: str,
    area: float,
) -> float:
    """
    Flächenbezogener Wärmebrückenzuschlag ΔU_TB,k (Gleichung 1).

    Falls detaillierte Wärmebrücken berechnet (Ψ·l + χ) vorhanden:
        ΔU_TB,k = (Σ(Ψ_l · l_l) + Σχ_m) / A_k

    Sonst: Pauschalwert nach Kategorie (A-D).

    Args:
        category: Wärmebrückenkategorie (A, B, C, D)
        area: Bauteilfläche A_k in m² (für detaillierte Berechnung)

    Returns:
        Flächenbezogener Wärmebrückenzuschlag in W/(m²K)
    """
    return HEAT_BRIDGE_CATEGORIES.get(category, 0.10)


def calc_transmission_coefficient_unheated(
    elements: list[Element],
    delta_u_tb: float,
) -> float:
    """
    Wärmeübertragungskoeffizient an unbeheizte Räume H_T,iae (Gleichung 2).

    H_T,iae = Σ(A_k · (U_k + ΔU_TB,k) · f_ia,k)

    Args:
        elements: Liste der Bauteile gegen unbeheizte Räume
        delta_u_tb: Wärmebrückenzuschlag in W/(m²K)

    Returns:
        Wärmeübertragungskoeffizient H_T,iae in W/K
    """
    h_t_iae = 0.0
    for elem in elements:
        if elem.boundary_temp is not None:
            # Temperaturanpassungsfaktor f_ia,k
            f_ia = elem.temperature_factor
            h_t_iae += elem.area * (elem.u_value + delta_u_tb) * f_ia
    return round(h_t_iae, 2)


def calc_equivalent_u_ground(
    perimeter: float,  # P — erdreichberührter Umfang [m]
    depth: float,  # z — Tiefe Bodenplatte [m]
    area: float,  # A_k — Bodenplattenfläche [m²]
    u_base: float,  # U_k — Basis-U-Wert
    delta_u_tb: float,  # ΔU_TB,k
    b_prime: float | None = None,  # B' — char. Bodenplattenmaß [m]
) -> float:
    """
    Äquivalenter U-Wert erdreichberührende Bauteile (Gleichung 3).

    U_equiv,k = a / (b + (c₁ + B')^n₁ + (c₂ + z)^n₂ + d)

    Hinweis: Die Gleichung 3 nach DIN EN 12831-1 Anhang C für Bodenplatten
    enthält KEINEN Term für U_k + ΔU_TB,k (dieser ist in der Norm nur für
    Kellerschächte relevant). Daher wird hier nur der B'- und z-Term berechnet.

    Falls B' nicht gegeben: B' = A_g / (0.5 * P)

    Args:
        perimeter: Erdreichberührter Umfang P in m
        depth: Tiefe Bodenplatte z in m
        area: Bodenplattenfläche A_k in m²
        u_base: Basis-U-Wert U_k in W/(m²K) (Platzhalter, wird nicht in Formel eingesetzt)
        delta_u_tb: Wärmebrückenzuschlag W/(m²K) (Platzhalter, wird nicht in Formel eingesetzt)
        b_prime: Charakteristisches Bodenplattenmaß B' in m (optional)

    Returns:
        Äquivalenter U-Wert U_equiv in W/(m²K)
    """
    # Berechne B' falls nicht gegeben
    if b_prime is None:
        b_prime = area / (0.5 * perimeter) if perimeter > 0 else 0.0

    p = GROUND_PARAMS

    numerator = p["a"]
    # Nur B'- und z-Term (ohne U+ΔU-Term) — entspricht DIN EN 12831-1 Anhang C
    denominator = (
        p["b"]
        + (p["c1"] + b_prime) ** p["n1"]
        + (p["c2"] + depth) ** p["n2"]
        + p["d"]
    )

    if denominator <= 0:
        # Fallback auf Basis-U-Wert
        return round(u_base + delta_u_tb, 4)

    u_equiv = numerator / denominator
    return round(u_equiv, 4)


def calc_transmission_loss(
    elements: list[Element],
    theta_int: float,
    theta_e: float,
    delta_u_tb: float = 0.10,
    heat_bridge_category: str = "C",
) -> float:
    """
    Transmissionswärmeverlust Φ_T eines Raums (Gleichung 6.3.1.3).

    Φ_T = Σ(H_T,k · (θ_int − θ_adj,k))

    Für jedes Bauteil:
    - Standard (gegen Außenluft): H_k = A_k · (U_k + ΔU_TB) · (θ_int − θ_e)
    - Erdreich: mit U_equiv
    - Unbeheizt: mit f_ix

    Args:
        elements: Liste aller Bauteile des Raums
        theta_int: Innentemperatur in °C
        theta_e: Außentemperatur in °C
        delta_u_tb: Wärmebrückenzuschlag in W/(m²K) (optional)
        heat_bridge_category: Kategorie für Pauschalwert (optional)

    Returns:
        Transmissionswärmeverlust Φ_T in W
    """
    if delta_u_tb is None:
        delta_u_tb = calc_heat_bridge_increment(heat_bridge_category, 0)

    phi_t = 0.0

    for elem in elements:
        # Bestimme angrenzende Temperatur
        if elem.boundary_temp is not None:
            theta_adj = elem.boundary_temp
        else:
            theta_adj = theta_e

        delta_theta = theta_int - theta_adj

        # Prüfe ob Erdreichkontakt
        is_ground_contact = (
            elem.perimeter is not None
            and elem.perimeter > 0
            and elem.depth is not None
        )

        if is_ground_contact:
            # Erdreich: U_equiv verwenden
            u_eff = calc_equivalent_u_ground(
                perimeter=elem.perimeter or 0,
                depth=elem.depth or 0,
                area=elem.area,
                u_base=elem.u_value,
                delta_u_tb=delta_u_tb,
            )
            h_k = elem.area * u_eff
        else:
            # Standard: U + ΔU_TB mit Temperaturfaktor
            h_k = elem.area * (elem.u_value + delta_u_tb) * elem.temperature_factor

        phi_t += h_k * delta_theta

    return round(phi_t, 2)


def calc_transmission_coefficient(
    elements: list[Element],
    delta_u_tb: float = 0.10,
) -> float:
    """
    Wärmeverlustkoeffizient H_T (für Zeitkonstante, Gleichung 7).

    H_T,12 = Σ(A_k · U_eff,k · f_x)

    Args:
        elements: Liste aller Bauteile
        delta_u_tb: Wärmebrückenzuschlag in W/(m²K)

    Returns:
        Wärmeverlustkoeffizient H_T in W/K
    """
    h_t = 0.0

    for elem in elements:
        # Prüfe ob Erdreichkontakt
        is_ground_contact = (
            elem.perimeter is not None
            and elem.perimeter > 0
            and elem.depth is not None
        )

        if is_ground_contact:
            u_eff = calc_equivalent_u_ground(
                perimeter=elem.perimeter or 0,
                depth=elem.depth or 0,
                area=elem.area,
                u_base=elem.u_value,
                delta_u_tb=delta_u_tb,
            )
            # delta_u_tb nicht zusätzlich addieren — U_equiv ist bereits äquivalent
        else:
            u_eff = elem.u_value + delta_u_tb

        h_t += elem.area * u_eff * elem.temperature_factor

    return round(h_t, 2)


# Alias für Abwärtskompatibilität
calc_h_t_12 = calc_transmission_coefficient


def calc_building_transmission_loss(
    elements: list[Element],
    theta_int_build: float,
    theta_e: float,
    delta_u_tb: float = 0.10,
) -> float:
    """
    Transmissionswärmeverlust Gebäude (Gleichung 41/42).

    Φ_T,build = U_m · ΣA_k · (θ_int,build − θ_e)
    U_m = Σ((U_k + ΔU_TB,k) · A_k · f_x,k) / ΣA_k

    Args:
        elements: Liste aller Gebäudehüllflächen
        theta_int_build: Gebäude-Innentemperatur in °C
        theta_e: Außentemperatur in °C
        delta_u_tb: Wärmebrückenzuschlag in W/(m²K)

    Returns:
        Transmissionswärmeverlust des Gebäudes in W
    """
    if not elements:
        return 0.0

    # Berechne mittleren U-Wert U_m
    sum_ua = 0.0
    sum_area = 0.0

    for elem in elements:
        u_eff = elem.u_value + delta_u_tb
        sum_ua += u_eff * elem.area * elem.temperature_factor
        sum_area += elem.area

    if sum_area <= 0:
        return 0.0

    u_m = sum_ua / sum_area
    phi_t_build = u_m * sum_area * (theta_int_build - theta_e)

    return round(phi_t_build, 2)
