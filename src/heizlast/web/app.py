"""
Web-GUI für Heizlast-Rechentool
FastAPI Backend mit Jinja2 Templates
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import sys

# Projekt-Root finden
HERE = Path(__file__).resolve()
SRC_DIR = HERE.parent.parent
PROJECT_ROOT = SRC_DIR.parent
TEMPLATES_DIR = SRC_DIR / "heizlast" / "web" / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

# Pfad für Imports
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from heizlast.calc.transmission import calc_transmission_loss
from heizlast.calc.ventilation import calc_ventilation_loss, calc_minimum_airflow
from heizlast.calc.time_constant import calc_time_constant, calc_theta_correction
from heizlast.data.climate_data import get_climate_data

app = FastAPI(title="Heizlast-Rechentool")

# Static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates - FIX: directory als String, nicht Path
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class ElementInput(BaseModel):
    name: str
    type: str
    area: float
    u_value: float
    is_ground_contact: bool = False
    perimeter: Optional[float] = None


class RoomInput(BaseModel):
    name: str
    theta_int: float = 20.0
    area: float
    height: float = 2.5
    elements: List[ElementInput] = []


class BuildingInput(BaseModel):
    plz: str
    name: str = "Mein Gebäude"
    rooms: List[RoomInput] = []
    effective_heat_capacity: float = 10000


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Startseite mit Eingabeformular"""
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/api/calculate")
async def calculate(building: BuildingInput):
    """Berechne Heizlast für alle Räume"""
    try:
        climate = get_climate_data(building.plz)
        theta_e = climate.theta_e_ref
        
        results = []
        total_ht = 0.0
        total_hv = 0.0
        
        for room in building.rooms:
            # Vereinfachte Berechnung ohne Element-Objekte
            phi_t = 0.0
            for e in room.elements:
                delta_t = room.theta_int - theta_e
                phi_t += e.area * e.u_value * delta_t
            
            # Lüftung
            volume = room.area * room.height
            q_min = calc_minimum_airflow(volume)
            phi_v = 0.34 * q_min * (room.theta_int - theta_e)
            
            h_t = phi_t / (room.theta_int - theta_e) if (room.theta_int - theta_e) != 0 else 0
            h_v = 0.34 * volume * 0.5
            
            total_ht += h_t
            total_hv += h_v
            
            results.append({
                "name": room.name,
                "area": room.area,
                "volume": round(volume, 1),
                "phi_t": round(phi_t, 1),
                "phi_v": round(phi_v, 1),
                "phi_total": round(phi_t + phi_v, 1)
            })
        
        # Zeitkonstante
        tau = calc_time_constant(building.effective_heat_capacity, total_ht, total_hv) if (total_ht + total_hv) > 0 else 0
        theta_e_corr = calc_theta_correction(theta_e, tau)
        
        return {
            "success": True,
            "climate": {
                "plz": building.plz,
                "theta_e": theta_e,
                "theta_e_corrected": round(theta_e_corr, 1)
            },
            "building": {
                "tau": round(tau, 1)
            },
            "rooms": results,
            "totals": {
                "h_t": round(total_ht, 1),
                "h_v": round(total_hv, 1),
                "phi_total": sum(r["phi_total"] for r in results)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
