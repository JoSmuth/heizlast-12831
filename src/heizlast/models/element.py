"""
Datenmodelle für Bauteile nach DIN EN 12831-1.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field


class ElementType(str, Enum):
    """Bauteiltypen nach DIN EN 12831-1."""
    WALL = "wand"
    CEILING = "decke"
    FLOOR = "boden"
    WINDOW = "fenster"
    DOOR = "tuer"
    GROUND_SLAB = "bodenplatte"
    ROOF = "dach"


class Element(BaseModel):
    """
    Einzelnes Bauteil nach DIN EN 12831-1.
    
    Enthält alle geometrischen und thermischen Parameter
    für die Transmissionswärmeverlustberechnung.
    """
    name: str = Field(..., description="Bauteilbezeichnung")
    element_type: ElementType = Field(..., description="Bauteiltyp")
    
    # Geometrie
    area: float = Field(..., gt=0, description="Bauteilfläche A_k in m²")
    u_value: float = Field(..., gt=0, description="Wärmedurchgangskoeffizient U_k in W/(m²K)")
    
    # Orientierung
    orientation: Optional[float] = Field(
        default=None,
        ge=0,
        lt=360,
        description="Orientierung in Grad (0=N, 90=O, 180=S, 270=W)"
    )
    
    # Temperaturanpassungsfaktor
    temperature_factor: float = Field(
        default=1.0,
        ge=0,
        le=1,
        description="Temperaturanpassungsfaktor f_ia,k / f_x,k"
    )
    
    # Angrenzende Temperatur
    boundary_temp: Optional[float] = Field(
        default=None,
        description="Angrenzende Temperatur θ_x,k in °C"
    )
    
    # Erdreichberührende Bauteile
    perimeter: Optional[float] = Field(
        default=None,
        ge=0,
        description="Erdreichberührter Umfang P in m"
    )
    depth: Optional[float] = Field(
        default=None,
        ge=0,
        description="Tiefe Bodenplatte z in m"
    )
    groundwater_depth: Optional[float] = Field(
        default=None,
        ge=0,
        description="Grundwassertiefe in m"
    )
    
    # Wärmebrückenzuschlag (flächenbezogen)
    delta_u_tb: float = Field(
        default=0.0,
        ge=0,
        description="Flächenbezogener Wärmebrückenzuschlag ΔU_TB,k in W/(m²K)"
    )
    
    @computed_field
    @property
    def effective_u_value(self) -> float:
        """Effektiver U-Wert inklusive Wärmebrückenzuschlag in W/(m²K)."""
        return round(self.u_value + self.delta_u_tb, 4)
    
    @computed_field
    @property
    def characteristic_length(self) -> Optional[float]:
        """
        Charakteristisches Bodenplattenmaß B' in m.
        
        Nur für Bodenplten gegen Erdreich: B' = A / (0.5 * P)
        """
        if self.element_type == ElementType.GROUND_SLAB and self.perimeter is not None and self.perimeter > 0:
            return round(self.area / (0.5 * self.perimeter), 2)
        return None


class WindowElement(Element):
    """
    Fenster nach DIN EN 12831-1.
    
    Erweitert das Basiselement um spezifische Fensterparameter.
    """
    element_type: ElementType = Field(default=ElementType.WINDOW, frozen=True)
    
    # Verglasung
    glass_u: float = Field(..., gt=0, description="Verglasung-U-Wert U_g in W/(m²K)")
    
    # Rahmen
    frame_u: float = Field(..., gt=0, description="Rahmen-U-Wert U_f in W/(m²K)")
    frame_fraction: float = Field(
        ...,
        ge=0,
        le=1,
        description="Rahmenanteil (0-1)"
    )
    
    # Rollladenkasten
    shutter_box_u: Optional[float] = Field(
        default=None,
        ge=0,
        description="Rollladenkasten-U-Wert in W/(m²K)"
    )
    shutter_box_fraction: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Rollladenkastenanteil (0-1)"
    )
