"""FastAPI Web-GUI für Heizlast-Rechentool."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import pathlib

# Parent directory imports
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from heizlast.calc.transmission import calc_transmission_loss
from heizlast.calc.ventilation import calc_ventilation_loss, calc_minimum_airflow
from heizlast.calc.time_constant import calc_time_constant, calc_theta_correction
from heizlast.data.climate_data import get_climate_data
from heizlast.models.element import Element, ElementType

app = FastAPI(title="Heizlast-Rechentool")

# Paths
BASE_DIR = pathlib.Path(__file__).parent
STATIC_DIR = BASE_DIR.parent.parent.parent / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class ElementInput(BaseModel):
    """Input model for building element."""
    name: str
    type: str  # wall, window, floor, ceiling, roof
    area: float
    u_value: float
    orientation: Optional[str] = None
    is_ground_contact: bool = False
    perimeter: Optional[float] = None


class RoomInput(BaseModel):
    """Input model for room."""
    name: str
    theta_int: float = 20.0
    area: float
    height: float = 2.5
    elements: List[ElementInput] = []


class BuildingInput(BaseModel):
    """Input model for building."""
    plz: str
    name: str = "Mein Gebäude"
    rooms: List[RoomInput] = []
    effective_heat_capacity: float = 10000


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/calculate")
async def calculate(building: BuildingInput):
    """Berechne Heizlast für alle Räume."""
    try:
        climate = get_climate_data(building.plz)
        theta_e = climate.theta_e_ref
    except Exception as e:
        return {"error": f"Ungültige PLZ: {building.plz}"}

    results = []
    total_ht = 0
    total_hv = 0

    for room in building.rooms:
        # Elemente verarbeiten
        elements = []
        for e in room.elements:
            elem_type_map = {
                "wall": ElementType.WALL,
                "window": ElementType.WINDOW,
                "floor": ElementType.FLOOR,
                "ceiling": ElementType.CEILING,
                "roof": ElementType.ROOF,
            }
            elem_type = elem_type_map.get(e.type, ElementType.WALL)
            
            elements.append(Element(
                name=e.name,
                element_type=elem_type,
                area=e.area,
                u_value=e.u_value,
                perimeter=e.perimeter if e.is_ground_contact else None,
            ))

        # Berechnung
        phi_t = calc_transmission_loss(elements, room.theta_int, theta_e)
        q_min = calc_minimum_airflow(room.area * room.height)
        phi_v_result = calc_ventilation_loss(q_min, theta_int=room.theta_int, theta_e=theta_e)
        phi_v = phi_v_result["phi_v_total"] if isinstance(phi_v_result, dict) else phi_v_result

        h_t = phi_t / (room.theta_int - theta_e) if (room.theta_int - theta_e) != 0 else 0
        h_v = 0.34 * room.area * room.height * 0.5

        total_ht += h_t
        total_hv += h_v

        results.append({
            "name": room.name,
            "area": room.area,
            "volume": round(room.area * room.height, 2),
            "phi_t": round(phi_t, 1),
            "phi_v": round(phi_v, 1) if isinstance(phi_v, (int, float)) else 0,
            "phi_total": round(phi_t + (phi_v if isinstance(phi_v, (int, float)) else 0), 1)
        })

    # Zeitkonstante
    tau = calc_time_constant(building.effective_heat_capacity, total_ht, total_hv)
    theta_e_corr = calc_theta_correction(theta_e, tau)

    return {
        "climate": {
            "plz": building.plz,
            "theta_e": theta_e,
            "theta_e_corrected": round(theta_e_corr, 1)
        },
        "building": {"tau": round(tau, 1)},
        "rooms": results,
        "totals": {
            "h_t": round(total_ht, 1),
            "h_v": round(total_hv, 1),
            "phi_total": sum(r["phi_total"] for r in results)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
