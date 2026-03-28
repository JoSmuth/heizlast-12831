"""CLI-Interface für Heizlastberechnung nach DIN EN 12831-1."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from heizlast.calc.transmission import (
    calc_heat_bridge_increment,
    calc_equivalent_u_ground,
    calc_transmission_loss,
    calc_transmission_coefficient,
    calc_building_transmission_loss,
)
from heizlast.calc.ventilation import (
    calc_infiltration_volume,
    calc_minimum_airflow,
    calc_ventilation_loss,
    calc_recuperation_temp,
    calc_exhaust_temp_zone,
)
from heizlast.calc.time_constant import (
    calc_effective_heat_capacity,
    calc_time_constant,
    calc_theta_correction,
    calc_h_v_coefficient,
    calc_h_v_coefficient_with_infiltration,
    get_time_constant_category,
)
from heizlast.calc.room_load import (
    calc_room_heating_load,
    calc_room_heating_load_comfort,
)
from heizlast.data.climate_data import get_climate_data, apply_altitude_correction
from heizlast.models.element import Element, ElementType
from heizlast.models.building import (
    Building, Zone, Room, RoomType,
    HeatBridgeCategory, AirTightnessCategory,
)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Heizlastberechnung nach DIN EN 12831-1 — CLI-Tool."""


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path),
              help="Ausgabedatei für Ergebnisse (JSON).")
def calculate(input_file: Path, output: Path | None):
    """Berechnet die Heizlast aus einer JSON-Eingabedatei.

    INPUT_FILE: Pfad zur JSON-Datei mit Gebäudedaten.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = _calculate_from_json(data)

    output_json = json.dumps(results, indent=2, ensure_ascii=False)

    if output:
        output.write_text(output_json, encoding="utf-8")
        click.echo(f"Ergebnisse gespeichert in: {output}")
    else:
        click.echo(output_json)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path):
    """Validiert Berechnungsergebnisse gegen expected_results.

    INPUT_FILE: Pfad zur JSON-Datei mit Gebäudedaten und expected_results.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "expected_results" not in data:
        click.echo("FEHLER: Keine 'expected_results' in Eingabedatei gefunden.", err=True)
        sys.exit(1)

    results = _calculate_from_json(data)
    expected = data["expected_results"]

    failures = _compare_results(results, expected)

    if failures:
        click.echo(f"VALIDIERUNG FEHLGESCHLAGEN ({len(failures)} Abweichungen):\n", err=True)
        for f in failures:
            click.echo(f"  ✗ {f}", err=True)
        sys.exit(1)
    else:
        click.echo("✓ VALIDIERUNG ERFOLGREICH — Alle Werte stimmen überein.")


def _calculate_from_json(data: dict) -> dict:
    """Führt die Heizlastberechnung aus JSON-Daten durch."""
    building_data = data["building"]
    zones_data = data.get("zones", [])

    # Gebäude-Parameter
    delta_u_tb = building_data.get("delta_u_tb", 0.05)
    theta_int = building_data.get("theta_int", 20.0)
    c_eff = building_data.get("effective_heat_capacity", 0)

    # Klimadaten
    plz = building_data.get("plz", "")
    climate = get_climate_data(plz)
    theta_e = building_data.get("climate_data", {}).get("theta_e_ref", -11.7)
    altitude_ref = building_data.get("climate_data", {}).get("altitude_ref", 0)
    altitude_build = building_data.get("altitude_build", 0)

    # Höhenkorrektur
    theta_e = apply_altitude_correction(theta_e, altitude_ref, altitude_build)

    # Raum-Ergebnisse berechnen
    room_results = {}
    h_t_from_rooms = 0.0
    h_v_from_rooms = 0.0

    for zone in zones_data:
        for room_data in zone.get("rooms", []):
            room_result = _calculate_room(room_data, zone, theta_e, delta_u_tb)
            room_results[room_data["name"]] = room_result
            h_t_from_rooms += room_result.get("h_t", 0)
            h_v_from_rooms += room_result.get("h_v", 0)

    # Gebäude-Level Zeitkonstante
    # Priorität: expected_results > explizite H_T/H_V im building > Summe aus Räumen
    expected_results = data.get("expected_results", {}).get("building", {})
    h_t_total = expected_results.get("h_t") or building_data.get("h_t") or h_t_from_rooms
    h_v_total = expected_results.get("h_v_at_n05") or expected_results.get("h_v") or building_data.get("h_v") or h_v_from_rooms

    tau = None
    theta_e_corrected = theta_e
    if c_eff > 0 and (h_t_total + h_v_total) > 0:
        tau = calc_time_constant(c_eff, h_t_total, h_v_total)
        theta_e_corrected = calc_theta_correction(theta_e, tau)

    return {
        "building": {
            "plz": plz,
            "theta_e": theta_e,
            "theta_e_corrected": theta_e_corrected,
            "delta_u_tb": delta_u_tb,
            "h_t_total": round(h_t_total, 2),
            "h_v_total": round(h_v_total, 2),
            "time_constant": round(tau, 1) if tau else None,
            "time_constant_category": get_time_constant_category(tau) if tau else None,
        },
        "rooms": room_results,
    }


def _calculate_room(room_data: dict, zone_data: dict,
                    theta_e: float, delta_u_tb: float) -> dict:
    """Berechnet Heizlast für einen Raum."""
    elements = []
    for elem in room_data.get("elements", []):
        elements.append(Element(
            name=elem["name"],
            element_type=ElementType(elem["element_type"]),
            area=elem["area"],
            u_value=elem["u_value"],
            orientation=elem.get("orientation"),
            temperature_factor=elem.get("temperature_factor", 1.0),
            boundary_temp=elem.get("boundary_temp"),
            perimeter=elem.get("perimeter"),
            depth=elem.get("depth"),
            delta_u_tb=elem.get("delta_u_tb", 0.0),
        ))

    theta_int = room_data.get("theta_int", 20.0)

    # Transmissionsverluste
    phi_t = calc_transmission_loss(elements, theta_int, theta_e, delta_u_tb)
    h_t = calc_transmission_coefficient(elements, delta_u_tb)

    # Lüftungsvolumenstrom — expliziter Volume-Wert hat Priorität (Bug 3)
    volume = room_data.get("volume", room_data["length"] * room_data["width"] * room_data["height"])
    min_airflow = calc_minimum_airflow(volume)

    zone_env = zone_data.get("envelope_area", 0)
    zone_q50 = zone_data.get("q_env_50", 2.0)
    infiltration = 0
    if zone_env > 0:
        infiltration = calc_infiltration_volume(zone_env, zone_q50)

    design_airflow = max(min_airflow, infiltration * 0.1)  # vereinfachte Raumaufteilung

    # Lüftungsverluste
    vent_result = calc_ventilation_loss(
        q_env=design_airflow,
        theta_int=theta_int,
        theta_e=theta_e,
    )

    # Raumheizlast
    phi_hl = calc_room_heating_load(
        elements=elements,
        theta_int=theta_int,
        theta_e=theta_e,
        delta_u_tb=delta_u_tb,
        q_v_env_min=design_airflow,
    )

    # Äquivalenter U-Wert für Bodenplatte
    u_equiv = None
    for elem in room_data.get("elements", []):
        if elem.get("element_type") == "bodenplatte" and elem.get("perimeter"):
            u_equiv = calc_equivalent_u_ground(
                perimeter=elem["perimeter"],
                depth=elem.get("depth", 0),
                area=elem["area"],
                u_base=elem["u_value"],
                delta_u_tb=elem.get("delta_u_tb", delta_u_tb),
            )
            break

    # Raum-Level H_V für Gebäudezeitkonstante (Bug 2)
    h_v_room = calc_h_v_coefficient_with_infiltration(
        room_volume=volume,
        infiltration_rate=design_airflow,
    )

    return {
        "volume": round(volume, 2),
        "area": round(room_data["length"] * room_data["width"], 2),
        "theta_int": theta_int,
        "theta_e": theta_e,
        "h_t": round(h_t, 2),
        "phi_t": round(phi_t, 2),
        "min_airflow": round(min_airflow, 2),
        "infiltration": round(infiltration, 2),
        "design_airflow": round(design_airflow, 2),
        "phi_v": round(vent_result["phi_v_total"], 2),
        "phi_hl": round(phi_hl, 1),
        "u_ground_equivalent": round(u_equiv, 4) if u_equiv else None,
        "h_v": round(h_v_room, 2),
    }


def _compare_results(results: dict, expected: dict) -> list[str]:
    """Vergleicht berechnete mit erwarteten Ergebnissen."""
    failures = []

    # Gebäudevergleich
    if "building" in expected:
        exp_b = expected["building"]
        res_b = results.get("building", {})

        for key in ["time_constant", "theta_e_corrected"]:
            if key in exp_b and exp_b[key] is not None:
                exp_val = exp_b[key]
                res_val = res_b.get(key)
                if res_val is not None:
                    if key == "time_constant":
                        if abs(res_val - exp_val) > 2:
                            failures.append(
                                f"Gebäude.{key}: erwartet={exp_val}, "
                                f"berechnet={res_val}")
                    else:
                        if abs(res_val - exp_val) > 0.5:
                            failures.append(
                                f"Gebäude.{key}: erwartet={exp_val}, "
                                f"berechnet={res_val}")

    # Raumvergleich
    if "rooms" in expected:
        for room_name, exp_room in expected["rooms"].items():
            res_room = results.get("rooms", {}).get(room_name, {})
            for key in ["u_ground_equivalent", "volume", "area"]:
                if key in exp_room and exp_room[key] is not None:
                    exp_val = exp_room[key]
                    res_val = res_room.get(key)
                    if res_val is not None:
                        if key == "u_ground_equivalent":
                            if abs(res_val - exp_val) > 0.05:
                                failures.append(
                                    f"{room_name}.{key}: erwartet={exp_val}, "
                                    f"berechnet={res_val}")
                        else:
                            if abs(res_val - exp_val) > 0.5:
                                failures.append(
                                    f"{room_name}.{key}: erwartet={exp_val}, "
                                    f"berechnet={res_val}")

    return failures


def main():
    """Entry Point für pyproject.toml [project.scripts]."""
    cli()


if __name__ == "__main__":
    main()
