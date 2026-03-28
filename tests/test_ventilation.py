"""Tests für Lüftungswärmeverluste nach DIN EN 12831-1."""
import pytest

from heizlast.calc.ventilation import (
    calc_infiltration_volume,
    calc_minimum_airflow,
    calc_ventilation_loss,
    calc_recuperation_temp,
)


class TestCalcInfiltrationVolume:
    """Tests für Infiltrationsvolumenstrom q_v,env."""

    def test_wolfsburg_zone_infiltration(self):
        """Wolfsburg: A_env=416, q_env_50=2.0 → 41.6 m³/h."""
        result = calc_infiltration_volume(
            envelope_area=416.0,
            q_env_50=2.0,
            shielding_factor=1.0,
            volume_flow_factor=0.05,
            open_area=0.0,
        )
        assert result == pytest.approx(41.6, abs=0.01)

    def test_with_open_area(self):
        """Infiltration mit offenen Öffnungen."""
        result = calc_infiltration_volume(
            envelope_area=100.0,
            q_env_50=2.0,
            shielding_factor=1.0,
            volume_flow_factor=0.05,
            open_area=10.0,
        )
        # (2.0 * 100 + 10) * 0.05 = 10.5
        assert result == pytest.approx(10.5, abs=0.01)

    def test_with_different_shielding(self):
        """Abschirmfaktor beeinflusst Ergebnis."""
        result_shielded = calc_infiltration_volume(
            envelope_area=100.0,
            q_env_50=2.0,
            shielding_factor=0.5,
            volume_flow_factor=0.05,
        )
        result_unshielded = calc_infiltration_volume(
            envelope_area=100.0,
            q_env_50=2.0,
            shielding_factor=1.0,
            volume_flow_factor=0.05,
        )
        assert result_shielded == pytest.approx(result_unshielded * 0.5, abs=0.01)

    def test_zero_envelope(self):
        """Hüllfläche = 0 → Infiltration = 0."""
        result = calc_infiltration_volume(
            envelope_area=0.0,
            q_env_50=2.0,
        )
        assert result == pytest.approx(0.0, abs=0.01)


class TestCalcMinimumAirflow:
    """Tests für Mindestluftwechsel q_v,min."""

    def test_wolfsburg_room3_volume(self):
        """Raum 3: V=53.14 → q_v,min=26.57 m³/h."""
        result = calc_minimum_airflow(53.14)
        assert result == pytest.approx(26.57, abs=0.01)

    def test_standard_formula(self):
        """Mindestluftwechsel = 0.5 × V."""
        result = calc_minimum_airflow(100.0)
        assert result == pytest.approx(50.0, abs=0.01)

    def test_zero_volume(self):
        """Volumen = 0 → Mindestluftwechsel = 0."""
        result = calc_minimum_airflow(0.0)
        assert result == pytest.approx(0.0, abs=0.01)


class TestCalcVentilationLoss:
    """Tests für Lüftungswärmeverlust Φ_V."""

    def test_infiltration_only(self):
        """Nur Infiltration ohne WRG."""
        result = calc_ventilation_loss(
            q_env=26.8,
            theta_int=20.0,
            theta_e=-10.9,
        )
        # Φ_V,env = 0.34 × 26.8 × (20 - (-10.9)) = 281.56 W
        expected = 0.34 * 26.8 * 30.9
        assert result["phi_v_env"] == pytest.approx(expected, abs=0.1)
        assert result["phi_v_total"] == pytest.approx(expected, abs=0.1)

    def test_with_supply_air(self):
        """Zuluft mit temperierter Luft."""
        result = calc_ventilation_loss(
            q_env=5.0,
            q_sup=100.0,
            theta_int=20.0,
            theta_e=-10.0,
            theta_rec=16.0,
        )
        # Φ_V,env = 0.34 × 5 × 30 = 51.0
        # Φ_V,sup = 0.34 × 100 × (20 - 16) = 136.0
        assert result["phi_v_env"] == pytest.approx(51.0, abs=0.1)
        assert result["phi_v_sup"] == pytest.approx(136.0, abs=0.1)
        assert result["phi_v_total"] == pytest.approx(187.0, abs=0.1)

    def test_with_transfer_air(self):
        """Überströmung berücksichtigen."""
        result = calc_ventilation_loss(
            q_env=5.0,
            q_transfer=50.0,
            theta_int=20.0,
            theta_e=-10.0,
            theta_transfer=15.0,
        )
        # Φ_V,transfer = 0.34 × 50 × (20 - 15) = 85.0
        assert result["phi_v_transfer"] == pytest.approx(85.0, abs=0.1)

    def test_return_values_structure(self):
        """Rückgabewerte enthalten alle Schlüssel."""
        result = calc_ventilation_loss(q_env=10.0)
        assert "phi_v_env" in result
        assert "phi_v_sup" in result
        assert "phi_v_transfer" in result
        assert "phi_v_total" in result
        assert "q_env" in result
        assert "q_sup" in result
        assert "q_transfer" in result


class TestCalcRecuperationTemp:
    """Tests für Zulufttemperatur nach WRG."""

    def test_wolfsburg_wrg85(self):
        """Wolfsburg: η_rec=0.85, θ_exh=21.1 → θ_rec=16.3 °C."""
        result = calc_recuperation_temp(
            theta_e=-10.9,
            eta_rec=0.85,
            theta_exh=21.1,
        )
        # θ_rec = -10.9 + 0.85 × (21.1 - (-10.9)) = 16.3
        assert result == pytest.approx(16.3, abs=0.1)

    def test_no_recuperation(self):
        """WRG-Wirkungsgrad = 0 → θ_rec = θ_e."""
        result = calc_recuperation_temp(
            theta_e=-10.0,
            eta_rec=0.0,
            theta_exh=20.0,
        )
        assert result == pytest.approx(-10.0, abs=0.01)

    def test_full_recuperation(self):
        """WRG-Wirkungsgrad = 1 → θ_rec = θ_exh."""
        result = calc_recuperation_temp(
            theta_e=-10.0,
            eta_rec=1.0,
            theta_exh=20.0,
        )
        assert result == pytest.approx(20.0, abs=0.01)

    def test_50_percent_recuperation(self):
        """WRG-Wirkungsgrad = 0.5 → Mittelwert."""
        result = calc_recuperation_temp(
            theta_e=0.0,
            eta_rec=0.5,
            theta_exh=20.0,
        )
        assert result == pytest.approx(10.0, abs=0.01)
