import pytest
from heizlast.calc.time_constant import calc_time_constant, calc_theta_correction


def test_time_constant_wolfsburg():
    """τ = 31835 / (210 + 99) ≈ 103 h"""
    tau = calc_time_constant(31835, 210, 99)
    assert abs(tau - 103) < 5


def test_theta_correction():
    """θ_e,korrigiert = -11.7 + 0.8 = -10.9 °C"""
    result = calc_theta_correction(-11.7, 103)
    assert abs(result - (-10.9)) < 0.5
