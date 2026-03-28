"""Tests für room_load Modul."""
import pytest
from heizlast.calc.room_load import calc_room_heating_load
from heizlast.models.element import Element, ElementType


def test_basic_room_load():
    """Einfacher Test: Transmissionsverlust ohne Lüftung."""
    element = Element(
        name="Wand",
        element_type=ElementType.WALL,
        area=10.0,
        u_value=1.0,
        temperature_factor=1.0,
    )
    # Phi_T = 10 * 1.0 * 1.0 * (20 - (-12)) = 320 W, Phi_V = 0
    result = calc_room_heating_load(
        elements=[element],
        theta_int=20.0,
        theta_e=-12.0,
    )
    assert result == 320.0


def test_room_load_with_ventilation():
    """Test mit Lüftungsverlusten."""
    element = Element(
        name="Wand",
        element_type=ElementType.WALL,
        area=10.0,
        u_value=1.0,
        temperature_factor=1.0,
    )
    # Phi_T = 320 W, Phi_V = 0.34 * 10 * 32 = 108.8 W
    result = calc_room_heating_load(
        elements=[element],
        theta_int=20.0,
        theta_e=-12.0,
        q_v_env_min=10.0,
    )
    assert result == pytest.approx(428.8, abs=0.1)
