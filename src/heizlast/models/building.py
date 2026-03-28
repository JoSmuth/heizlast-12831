"""
Datenmodelle für Gebäude, Zonen und Räume nach DIN EN 12831-1.
"""

from __future__ import annotations
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator, computed_field

from .element import Element


class RoomType(str, Enum):
    """Raumarten nach Tabelle 32 der Norm."""
    WOHNZIMMER = "wohnzimmer"
    SCHLAFZIMMER = "schlafzimmer"
    BUERO = "buero"
    BADEZIMMER = "badezimmer"
    DUSCHE = "dusche"
    UMKEIDE = "umkleide"
    NEBENRAUM = "nebenraum"
    TREPPENHAUS = "treppenhaus"
    INDUSTRIEHALLE = "industrie_halle"
    SONSTIGES = "sonstiges"


class AirTightnessCategory(str, Enum):
    """Luftdichtheitskategorien."""
    A = "A"  # q_env,50 ≤ 2,0 m³/(m²h)
    B = "B"  # q_env,50 ≤ 3,0 m³/(m²h)
    C = "C"  # q_env,50 ≤ 6,0 m³/(m²h)
    D = "D"  # q_env,50 > 6,0 m³/(m²h)


class HeatBridgeCategory(str, Enum):
    """Wärmebrückenzuschlag-Kategorien."""
    A = "A"  # ΔU_TB = 0,05 W/(m²K)
    B = "B"  # ΔU_TB = 0,10 W/(m²K)
    C = "C"  # ΔU_TB = 0,15 W/(m²K)
    D = "D"  # ΔU_TB = 0,20 W/(m²K)


class Room(BaseModel):
    """
    Raum nach DIN EN 12831-1.
    
    Enthält alle geometrischen, thermischen und lüftungstechnischen Parameter.
    """
    name: str = Field(..., description="Raumbezeichnung")
    room_type: RoomType = Field(default=RoomType.WOHNZIMMER, description="Raumart")
    
    # Geometrie
    length: float = Field(..., ge=0, description="Länge in m")
    width: float = Field(..., ge=0, description="Breite in m")
    height: float = Field(..., ge=0, description="Höhe in m")
    
    # Temperatur
    theta_int: Optional[float] = Field(default=None, description="Auslegungsinnentemperatur in °C")
    theta_int_comfort: Optional[float] = Field(default=None, description="Komfort-Innentemperatur in °C (max. +3 K)")
    
    # Bauteile
    elements: list[Element] = Field(default_factory=list, description="Bauteilliste")
    
    # Lüftung
    q_v_sup: float = Field(default=0.0, ge=0, description="Zuluftvolumenstrom in m³/h")
    q_v_exh: float = Field(default=0.0, ge=0, description="Abluftvolumenstrom in m³/h")
    q_v_transfer: float = Field(default=0.0, ge=0, description="Überströmvolumenstrom in m³/h")
    q_v_techn: float = Field(default=0.0, ge=0, description="Technischer Volumenstrom in m³/h")
    
    # Aufheizparameter
    heating_up_enabled: bool = Field(default=False, description="Aufheizzuschlag vorsehen")
    t_hu: float = Field(default=2.0, gt=0, description="Aufheizzeit in h")
    n_sb: float = Field(default=0.1, ge=0, description="Luftwechsel während Absenkung in h⁻¹")
    
    @computed_field
    @property
    def area(self) -> float:
        """Grundfläche in m²."""
        return round(self.length * self.width, 2)
    
    @computed_field
    @property
    def volume(self) -> float:
        """Volumen in m³."""
        return round(self.length * self.width * self.height, 2)
    
    @field_validator("theta_int_comfort")
    @classmethod
    def validate_comfort_temp(cls, v: Optional[float], info) -> Optional[float]:
        """Komforttemperatur darf maximal +3 K über Standard liegen."""
        if v is not None and "theta_int" in info.data and info.data["theta_int"] is not None:
            if v > info.data["theta_int"] + 3:
                raise ValueError("Komforttemperatur darf maximal +3 K über Standardtemperatur liegen")
        return v


class Zone(BaseModel):
    """
    Zone - Gruppe von Räumen nach DIN EN 12831-1.
    
    Eine Zone kann mehrere Räume umfassen, die gemeinsam betrachtet werden.
    """
    name: str = Field(..., description="Zonenbezeichnung")
    number: Optional[str] = Field(default=None, description="Zonennummer")
    
    # Luftdichtheit
    air_tightness_category: AirTightnessCategory = Field(
        default=AirTightnessCategory.A,
        description="Luftdichtheitskategorie"
    )
    q_env_50: Optional[float] = Field(
        default=None, 
        ge=0,
        description="Hüllflächenbez. Luftdurchlässigkeit in m³/(m²h)"
    )
    
    # Lüftungsanlage
    has_ventilation_system: bool = Field(default=False, description="Lüftungsanlage vorhanden")
    eta_rec: float = Field(default=0.0, ge=0, le=1, description="WRG-Wirkungsgrad (0-1)")
    q_v_sup_zone: float = Field(default=0.0, ge=0, description="Zuluftvolumenstrom Zone in m³/h")
    q_v_exh_zone: float = Field(default=0.0, ge=0, description="Abluftvolumenstrom Zone in m³/h")
    
    # Volumenstromfaktor
    f_qv_z: float = Field(default=0.05, ge=0, description="Volumenstromfaktor für Infiltration")
    
    # Fassaden
    num_facades: int = Field(default=1, ge=1, le=4, description="Anzahl Fassaden")
    f_dir: float = Field(default=1.0, ge=1, le=4, description="Fassadenfaktor für direkte Durchströmung")
    
    # Räume
    rooms: list[Room] = Field(default_factory=list, description="Raumliste")
    
    @computed_field
    @property
    def volume(self) -> float:
        """Gesamtvolumen der Zone in m³."""
        return round(sum(r.volume for r in self.rooms), 2)
    
    @computed_field
    @property
    def envelope_area(self) -> float:
        """Hüllfläche der Zone in m²."""
        return round(sum(r.area for r in self.rooms), 2)


class Building(BaseModel):
    """
    Gebäude nach DIN EN 12831-1.
    
    Enthält alle Gebäudedaten, Klimadaten und Zonen.
    """
    name: str = Field(..., description="Gebäudebezeichnung")
    number: Optional[str] = Field(default=None, description="Gebäudenummer")
    
    # Geometrie
    gross_volume: float = Field(..., gt=0, description="Bruttovolumen V_e in m³")
    building_area: float = Field(..., gt=0, description="Grundfläche A_build in m²")
    num_floors: int = Field(default=1, ge=1, description="Anzahl Geschosse")
    
    # Wärmebrücken
    heat_bridge_category: HeatBridgeCategory = Field(
        default=HeatBridgeCategory.A,
        description="Wärmebrückenzuschlag-Kategorie"
    )
    delta_u_tb: Optional[float] = Field(
        default=None,
        ge=0,
        description="Wärmebrückenzuschlag ΔU_TB in W/(m²K)"
    )
    
    # Klimadaten (PLZ-basiert)
    plz: str = Field(..., description="Postleitzahl")
    
    # Standorthöhe
    altitude_build: float = Field(default=0.0, ge=0, description="Standorthöhe in m")
    
    # Zonen
    zones: list[Zone] = Field(default_factory=list, description="Zonenliste")
    
    @computed_field
    @property
    def volume(self) -> float:
        """Gesamtvolumen des Gebäudes in m³."""
        return round(sum(z.volume for z in self.zones), 2)
    
    def get_delta_u_tb(self) -> float:
        """
        Gibt den Wärmebrückenzuschlag zurück.
        
        Falls kein expliziter Wert gesetzt ist, wird der Kategorie-Standardwert verwendet.
        """
        if self.delta_u_tb is not None:
            return self.delta_u_tb
        
        category_values = {
            HeatBridgeCategory.A: 0.05,
            HeatBridgeCategory.B: 0.10,
            HeatBridgeCategory.C: 0.15,
            HeatBridgeCategory.D: 0.20,
        }
        return category_values[self.heat_bridge_category]
