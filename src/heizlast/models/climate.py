"""
Klimadaten nach DIN EN 12831-1.
"""

from __future__ import annotations
from pydantic import BaseModel, Field


class ClimateData(BaseModel):
    """
    Klimadaten für einen Standort nach DIN EN 12831-1.
    
    Enthält Auslegungsaußentemperatur, Jahresmitteltemperatur
    und Standortparameter für die Höhenkorrektur.
    """
    # Auslegungsaußentemperatur (kältester 2-Tages-Mittel, 1995-2012)
    theta_e_ref: float = Field(
        ...,
        description="Auslegungsaußentemperatur θ_e,ref in °C"
    )
    
    # Jahresmitteltemperatur
    theta_e_mean: float = Field(
        ...,
        description="Jahresmittlere Außentemperatur θ_e,m in °C"
    )
    
    # Höhenbezug
    altitude_ref: float = Field(
        default=0.0,
        ge=0,
        description="Referenzhöhe h_Ref in m"
    )
    altitude_build: float = Field(
        default=0.0,
        ge=0,
        description="Standorthöhe h_build in m"
    )
    
    # Wind
    wind_speed: float = Field(
        default=3.0,
        ge=0,
        description="Mittlere Windgeschwindigkeit in m/s"
    )
    wind_direction: str = Field(
        default="S",
        description="Hauptwindrichtung (N, NO, O, SO, S, SW, W, NW)"
    )
    
    # Standort
    location: str = Field(
        default="",
        description="Ortsname / Standort"
    )

    # PLZ
    plz: str = Field(
        ...,
        description="Postleitzahl"
    )
    
    def height_correction(self, theta_e_corrected: float | None = None) -> float:
        """
        Höhenkorrektur nach DIN EN 12831-1 §6.3.7.
        
        Gradient: -0,01 K/m bei Abweichung >= 200 m.
        Rückgabe der Korrektur in K (additiv zu θ_e,ref).
        """
        delta_h = abs(self.altitude_build - self.altitude_ref)
        if delta_h >= 200:
            return round(-0.01 * delta_h, 1)
        return 0.0
    
    def get_corrected_theta_e(self) -> float:
        """Korrigierte Auslegungsaußentemperatur mit Höhenkorrektur."""
        return round(self.theta_e_ref + self.height_correction(), 1)
