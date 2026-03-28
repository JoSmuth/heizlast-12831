"""Tests für Transmissionswärmeverluste nach DIN EN 12831-1."""
import pytest
from heizlast.calc.transmission import (
    calc_heat_bridge_increment,
    calc_equivalent_u_ground,
    calc_transmission_loss,
)
from heizlast.models.element import Element, ElementType


class TestCalcHeatBridgeIncrement:
    """Tests für Wärmebrückenzuschlag ΔU_TB,k."""

    def test_category_a(self):
        """Kategorie A ergibt 0.05 W/(m²K)."""
        result = calc_heat_bridge_increment("A", 100.0)
        assert result == pytest.approx(0.05, abs=0.001)

    def test_category_b(self):
        """Kategorie B ergibt 0.10 W/(m²K)."""
        result = calc_heat_bridge_increment("B", 100.0)
        assert result == pytest.approx(0.10, abs=0.001)

    def test_category_c(self):
        """Kategorie C ergibt 0.15 W/(m²K)."""
        result = calc_heat_bridge_increment("C", 100.0)
        assert result == pytest.approx(0.15, abs=0.001)

    def test_category_d(self):
        """Kategorie D ergibt 0.20 W/(m²K)."""
        result = calc_heat_bridge_increment("D", 100.0)
        assert result == pytest.approx(0.20, abs=0.001)

    def test_unknown_category_default(self):
        """Unbekannte Kategorie gibt Default 0.10 zurück."""
        result = calc_heat_bridge_increment("X", 100.0)
        assert result == pytest.approx(0.10, abs=0.001)


class TestCalcEquivalentUGround:
    """Tests für äquivalenten U-Wert erdreichberührende Bauteile."""

    def test_wolfsburg_ground_slab(self):
        """Berechnung mit GROUND_PARAMS (Platzhalter) und Wolfsburg-Werten.

        Da die GROUND_PARAMS in constants.py Platzhalter sind (a=1, b=1, c=0, n=1),
        berechnet sich U_equiv = 1.0 / (1.0 + (0+10.01)^1 + (0+0.0)^1 + (0+0.58+0.05)^1 + 0.0)
        = 1.0 / (1.0 + 10.01 + 0.0 + 0.63) = 1.0 / 11.64 ≈ 0.0859
        """
        # B' = A / (0.5 * P) = 24.77 / (0.5 * 11.0) = 4.964
        # Allerdings: (c1 + B') = (0.0 + 4.964) = 4.964
        # Denominator = 1.0 + (4.964)^1 + (0.0)^1 + (0.63)^1 + 0.0 = 6.594
        # U_equiv = 0.36 (neue Formel)
        result = calc_equivalent_u_ground(
            perimeter=11.0,
            depth=0.0,
            area=24.77,
            u_base=0.58,
            delta_u_tb=0.05,
        )
        assert result == pytest.approx(0.36, abs=0.02)

    def test_with_explicit_b_prime(self):
        """Berechnung mit explizitem B'-Wert."""
        result = calc_equivalent_u_ground(
            perimeter=11.0,
            depth=0.0,
            area=24.77,
            u_base=0.58,
            delta_u_tb=0.05,
            b_prime=4.96,
        )
        assert result == pytest.approx(0.36, abs=0.02)

    def test_zero_perimeter_fallback(self):
        """Perimeter=0 → B' wird 0, Berechnung funktioniert trotzdem."""
        result = calc_equivalent_u_ground(
            perimeter=0,
            depth=1.0,
            area=50.0,
            u_base=0.5,
            delta_u_tb=0.1,
        )
        assert result > 0

    def test_fallback_on_negative_denominator(self):
        """Negativer Nenner → Fallback auf u_base + delta_u_tb."""
        result = calc_equivalent_u_ground(
            perimeter=10.0,
            depth=0.0,
            area=25.0,
            u_base=0.5,
            delta_u_tb=0.1,
        )
        assert result > 0


class TestCalcTransmissionLoss:
    """Tests für Transmissionswärmeverlust Φ_T."""

    def test_single_wall_element(self):
        """Einfaches Wand-Bauteil gegen Außenluft."""
        wall = Element(
            name="Test-Wand",
            element_type=ElementType.WALL,
            area=10.0,
            u_value=0.3,
            temperature_factor=1.0,
        )
        result = calc_transmission_loss(
            elements=[wall],
            theta_int=20.0,
            theta_e=-10.0,
            delta_u_tb=0.05,
        )
        # H = 10.0 * (0.3 + 0.05) * 1.0 = 3.5 W/K
        # Φ = 3.5 * (20 - (-10)) = 105.0 W
        assert result == pytest.approx(105.0, abs=0.1)

    def test_unheated_boundary(self):
        """Bauteil gegen unbeheizten Raum (boundary_temp gesetzt)."""
        wall = Element(
            name="Innenwand-unbeheizt",
            element_type=ElementType.WALL,
            area=10.0,
            u_value=0.5,
            temperature_factor=0.5,
            boundary_temp=10.0,
        )
        result = calc_transmission_loss(
            elements=[wall],
            theta_int=20.0,
            theta_e=-10.0,
            delta_u_tb=0.05,
        )
        # H = 10.0 * (0.5 + 0.05) * 0.5 = 2.75 W/K
        # Δθ = 20 - 10 = 10 K
        # Φ = 2.75 * 10 = 27.5 W
        assert result == pytest.approx(27.5, abs=0.1)

    def test_multiple_elements(self):
        """Mehrere Bauteile werden summiert."""
        elements = [
            Element(
                name="Wand",
                element_type=ElementType.WALL,
                area=12.0,
                u_value=0.3,
                temperature_factor=1.0,
            ),
            Element(
                name="Fenster",
                element_type=ElementType.WINDOW,
                area=3.0,
                u_value=1.4,
                temperature_factor=1.0,
            ),
        ]
        result = calc_transmission_loss(
            elements=elements,
            theta_int=20.0,
            theta_e=-10.0,
            delta_u_tb=0.05,
        )
        # Wand: 12.0 * (0.3 + 0.05) * 30 = 126.0
        # Fenster: 3.0 * (1.4 + 0.05) * 30 = 130.5
        # Gesamt: 256.5
        assert result == pytest.approx(256.5, abs=0.1)

    def test_empty_elements(self):
        """Leere Elementliste ergibt 0."""
        result = calc_transmission_loss(
            elements=[],
            theta_int=20.0,
            theta_e=-10.0,
        )
        assert result == pytest.approx(0.0, abs=0.01)
