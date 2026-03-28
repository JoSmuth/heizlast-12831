"""
Raumheizlast nach DIN EN 12831-1 §6.3.1.3.

Zusammenfassung Transmissions- und Lüftungsverluste mit
Komfort- und Aufheizzuschlag.
"""

from __future__ import annotations

from ..models.building import Room, Building
from ..models.element import Element
from ..data.constants import AIR_CONSTANT, ROOM_TEMPERATURES

from .transmission import calc_transmission_loss
from .time_constant import calc_theta_correction


def calc_room_heating_load(
    elements: list[Element],
    theta_int: float,
    theta_e: float,
    delta_u_tb: float = 0.0,
    q_v_env_min: float = 0.0,
    air_constant: float = AIR_CONSTANT,
) -> float:
    """
    Berechnet die Raumheizlast Φ_HL,i [W].

    Φ_HL,i = Φ_T,i + Φ_V,i
    """
    # Transmissionsverluste
    phi_t = calc_transmission_loss(elements, theta_int, theta_e, delta_u_tb)

    # Lüftungsverluste
    phi_v = air_constant * q_v_env_min * (theta_int - theta_e)

    phi_hl = phi_t + phi_v

    return round(phi_hl, 1)


def calc_room_heating_load_comfort(
    room: Room,
    theta_e: float,
    delta_u_tb: float = 0.0,
    q_v_env_min: float = 0.0,
) -> dict[str, float]:
    """
    Raumheizlast mit Komfort- und Aufheizzuschlag nach Gleichung 43/44.

    Rückgabe: Dictionary mit Standardlast, Komfortzuschlag, Aufheizzuschlag, Gesamtlast.
    """
    # Standard-Raumtemperatur
    theta_int = room.theta_int
    if theta_int is None:
        theta_int = ROOM_TEMPERATURES.get(room.room_type.value, 20.0)

    # Standard-Heizlast
    phi_hl_stand = calc_room_heating_load(
        elements=room.elements,
        theta_int=theta_int,
        theta_e=theta_e,
        delta_u_tb=delta_u_tb,
        q_v_env_min=q_v_env_min,
    )

    # Komfortzuschlag
    phi_comfort = 0.0
    if room.theta_int_comfort is not None:
        phi_hl_comfort = calc_room_heating_load(
            elements=room.elements,
            theta_int=room.theta_int_comfort,
            theta_e=theta_e,
            delta_u_tb=delta_u_tb,
            q_v_env_min=q_v_env_min,
        )
        phi_comfort = max(0.0, phi_hl_comfort - phi_hl_stand)

    # Aufheizzuschlag (vereinfacht)
    phi_hu = 0.0
    if room.heating_up_enabled:
        from .heating_up import calc_heating_up_power
        from .transmission import calc_h_t_12

        h_t = calc_h_t_12(room.elements, delta_u_tb)
        h_v = AIR_CONSTANT * q_v_env_min
        c_eff = 60.0 * room.volume  # Vereinfacht: schwere Bauweise

        hu_data = calc_heating_up_power(
            theta_int=theta_int,
            theta_e=theta_e,
            h_t=h_t,
            h_v=h_v,
            c_eff=c_eff,
            area=room.area,
            n_sb=room.n_sb,
            t_hu=room.t_hu,
        )
        phi_hu = hu_data["phi_hu_total"]

    # Kombination nach Gleichung 44
    if phi_comfort < 0:
        phi_surchage = phi_comfort + phi_hu
    else:
        phi_surchage = max(phi_comfort, phi_hu)

    phi_hl_total = phi_hl_stand + phi_surchage

    return {
        "phi_hl_stand": round(phi_hl_stand, 1),
        "phi_comfort": round(phi_comfort, 1),
        "phi_hu": round(phi_hu, 1),
        "phi_surchage": round(phi_surchage, 1),
        "phi_hl_total": round(phi_hl_total, 1),
    }


def calc_building_heating_load(
    building: Building,
    theta_int: float = 20.0,
) -> float:
    """
    Gebäudeheizlast nach Gleichung 48.

    Φ_HL,build ≈ H · (θ_int - θ_e)
    
    Vereinfachte Berechnung über Gebäudehüllfläche.
    """
    from ..data.climate_data import get_climate_data

    climate = get_climate_data(building.plz)
    theta_e = calc_theta_correction(
        climate.get_corrected_theta_e(),
        tau=100.0,  # Standardwert, falls nicht berechnet
    )

    delta_u_tb = building.get_delta_u_tb()

    # Gesamtwärmeverlustkoeffizient
    h_total = 0.0
    for zone in building.zones:
        for room in zone.rooms:
            for elem in room.elements:
                u_eff = elem.u_value + delta_u_tb
                h_total += elem.area * u_eff * elem.temperature_factor

    phi_hl_build = h_total * (theta_int - theta_e)

    return round(phi_hl_build, 1)
