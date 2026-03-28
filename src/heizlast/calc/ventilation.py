"""
Lüftungswärmeverluste nach DIN EN 12831-1 / DIN/TS 12831-1

Implementiert die Gleichungen 29-34 aus Abschnitt 6.3.3 (Lüftungswärmeverluste).
"""

from typing import Optional
from heizlast.data.constants import AIR_CONSTANT


def calc_infiltration_volume(
    envelope_area: float,
    q_env_50: float,
    shielding_factor: float = 1.0,
    volume_flow_factor: float = 0.05,
    open_area: float = 0.0,
) -> float:
    """
    Berechnet den Infiltrationsvolumenstrom nach Gleichung 32.

    q_v,env = (q_env,50 · A_env + q_v,open) · f_qv,z · f_dir

    Parameters
    ----------
    envelope_area : float
        Hüllfläche des Raumes A_env [m²]
    q_env_50 : float
        Hüllflächenbezogene Luftdurchlässigkeit bei 50 Pa [m³/(m²h)]
    shielding_factor : float, optional
        Richtungs- und Abschirmfaktor f_dir (Standard: 1.0)
    volume_flow_factor : float, optional
        Volumenstromfaktor f_qv,z (Standard: 0.05 nach DIN/TS 12831-1)
    open_area : float, optional
        Volumenstrom durch offene Öffnungen q_v,open [m³/h] (Standard: 0.0)

    Returns
    -------
    float
        Infiltrationsvolumenstrom q_v,env [m³/h]

    Examples
    --------
    >>> # Beispiel aus ANFORDERUNGEN.md, Raum 3:
    >>> # A_env = 416.0 m² (Zone), q_env,50 = 2.0 m³/(m²h)
    >>> calc_infiltration_volume(416.0, 2.0, 1.0, 0.05, 0.0)
    41.6
    """
    q_v_env = (q_env_50 * envelope_area + open_area) * volume_flow_factor * shielding_factor
    return q_v_env


def calc_minimum_airflow(room_volume: float) -> float:
    """
    Berechnet den Mindestluftwechsel nach DIN EN 12831-1.

    q_v,min = 0.5 · V_i

    Der Mindestluftwechsel entspricht einem Luftwechsel von 0,5 h⁻¹.

    Parameters
    ----------
    room_volume : float
        Raumvolumen V_i [m³]

    Returns
    -------
    float
        Mindestvolumenstrom q_v,min [m³/h]

    Examples
    --------
    >>> # Beispiel: Raum 53,14 m³
    >>> calc_minimum_airflow(53.14)
    26.57
    """
    return 0.5 * room_volume


def calc_ventilation_loss(
    q_env: float,
    q_sup: float = 0,
    q_transfer: float = 0,
    theta_int: float = 20.0,
    theta_e: float = -10.0,
    theta_rec: Optional[float] = None,
    theta_transfer: Optional[float] = None,
) -> dict:
    """
    Berechnet die Lüftungswärmeverluste nach den Gleichungen 32-34.

    Gl. 32: Φ_V,env = 0.34 · q_env · (θ_int - θ_e)
    Gl. 33: Φ_V,sup = 0.34 · q_sup · (θ_int - θ_rec oder θ_e)
    Gl. 34: Φ_V,transfer = 0.34 · q_transfer · (θ_int - θ_transfer)

    Parameters
    ----------
    q_env : float
        Infiltrations-/Leckagevolumenstrom [m³/h]
    q_sup : float, optional
        Zuluftvolumenstrom [m³/h] (Standard: 0)
    q_transfer : float, optional
        Überströmvolumenstrom [m³/h] (Standard: 0)
    theta_int : float, optional
        Innentemperatur [°C] (Standard: 20.0)
    theta_e : float, optional
        Außentemperatur [°C] (Standard: -10.0)
    theta_rec : float, optional
        Zulufttemperatur nach Wärmerückgewinnung [°C]
        Wenn None, wird theta_e verwendet (keine WRG)
    theta_transfer : float, optional
        Temperatur des Überströmluft [°C]
        Wenn None, wird theta_e verwendet

    Returns
    -------
    dict
        Dictionary mit:
        - phi_v_env: Lüftungswärmeverlust durch Infiltration [W]
        - phi_v_sup: Lüftungswärmeverlust durch Zuluft [W]
        - phi_v_transfer: Lüftungswärmeverlust durch Überströmung [W]
        - phi_v_total: Gesamter Lüftungswärmeverlust [W]
        - q_env: Infiltrationsvolumenstrom [m³/h]
        - q_sup: Zuluftvolumenstrom [m³/h]
        - q_transfer: Überströmvolumenstrom [m³/h]

    Examples
    --------
    >>> result = calc_ventilation_loss(q_env=26.8, theta_int=20, theta_e=-10.9)
    >>> result["phi_v_env"]
    280.648
    >>> result["phi_v_total"]
    280.648
    """
    # Zulufttemperatur: WRG oder Außenluft
    theta_sup = theta_rec if theta_rec is not None else theta_e
    
    # Überströmtemperatur: angegeben oder Außenluft
    theta_trans = theta_transfer if theta_transfer is not None else theta_e

    # Gleichung 32: Leckagen/Infiltration
    phi_v_env = AIR_CONSTANT * q_env * (theta_int - theta_e)
    
    # Gleichung 33: Zuluft
    phi_v_sup = AIR_CONSTANT * q_sup * (theta_int - theta_sup)
    
    # Gleichung 34: Überströmung
    phi_v_transfer = AIR_CONSTANT * q_transfer * (theta_int - theta_trans)

    # Gesamtwärmeverlust
    phi_v_total = phi_v_env + phi_v_sup + phi_v_transfer

    return {
        "phi_v_env": phi_v_env,
        "phi_v_sup": phi_v_sup,
        "phi_v_transfer": phi_v_transfer,
        "phi_v_total": phi_v_total,
        "q_env": q_env,
        "q_sup": q_sup,
        "q_transfer": q_transfer,
    }


def calc_recuperation_temp(
    theta_e: float,
    eta_rec: float,
    theta_exh: float,
) -> float:
    """
    Berechnet die Zulufttemperatur nach Wärmerückgewinnung.

    θ_rec,z = θ_e + η_rec · (θ_exh - θ_e)

    Parameters
    ----------
    theta_e : float
        Außentemperatur [°C]
    eta_rec : float
        Wirkungsgrad der Wärmerückgewinnung (0.0 bis 1.0)
    theta_exh : float
        Ablufttemperatur der Zone [°C]

    Returns
    -------
    float
        Zulufttemperatur nach WRG θ_rec,z [°C]

    Examples
    --------
    >>> # Beispiel aus ANFORDERUNGEN.md:
    >>> # θ_e = -10.9°C, η_rec = 0.85, θ_exh = 21.1°C
    >>> calc_recuperation_temp(-10.9, 0.85, 21.1)
    16.25
    """
    theta_rec_z = theta_e + eta_rec * (theta_exh - theta_e)
    return theta_rec_z


def calc_exhaust_temp_zone(
    room_volumes: list[float],
    room_temps: list[float],
    supply_volumes: Optional[list[float]] = None,
) -> float:
    """
    Berechnet die mittlere Ablufttemperatur einer Zone.

    θ_exh,z = Σ(q_v,i · θ_int,i) / Σ(q_v,i)

    Bei Angabe von supply_volumes wird dieser Volumenstrom verwendet,
    andernfalls wird von den Raumvolumen ausgegangen.

    Parameters
    ----------
    room_volumes : list[float]
        Raumvolumina V_i [m³] (wenn keine supply_volumes angegeben)
    room_temps : list[float]
        Innentemperaturen θ_int,i [°C]
    supply_volumes : list[float], optional
        Zuluftvolumenströme q_v,i [m³/h]
        Wenn None, werden room_volumes verwendet

    Returns
    -------
    float
        Mittlere Ablufttemperatur θ_exh,z [°C]

    Raises
    ------
    ValueError
        Wenn die Listen unterschiedliche Längen haben oder leer sind

    Examples
    --------
    >>> # Beispiel: Ein Raum mit 20°C, Volumen 53.14 m³
    >>> calc_exhaust_temp_zone([53.14], [20.0])
    20.0
    >>> # Beispiel aus ANFORDERUNGEN.md mit expliziten Volumenströmen:
    >>> calc_exhaust_temp_zone([53.14, 42.0], [20.0, 22.0], [100.0, 80.0])
    20.888...
    """
    if len(room_volumes) != len(room_temps):
        raise ValueError(
            f"Listen müssen gleiche Länge haben: "
            f"room_volumes={len(room_volumes)}, room_temps={len(room_temps)}"
        )
    
    if len(room_volumes) == 0:
        raise ValueError("Leere Listen nicht erlaubt")

    # Verwende supply_volumes oder room_volumes
    volumes = supply_volumes if supply_volumes is not None else room_volumes
    
    if len(volumes) != len(room_temps):
        raise ValueError(
            f"supply_volumes muss gleiche Länge wie room_temps haben: "
            f"supply_volumes={len(volumes)}, room_temps={len(room_temps)}"
        )

    # Gewichtete Summe
    sum_q_theta = sum(q * theta for q, theta in zip(volumes, room_temps))
    sum_q = sum(volumes)

    if sum_q == 0:
        raise ValueError("Summe der Volumenströme darf nicht null sein")

    theta_exh_z = sum_q_theta / sum_q
    return theta_exh_z
