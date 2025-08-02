from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Dict

import fluvial_flood_risks
import coastal_flood_risks
import fire_kml_old
import desert

app = FastAPI(title="Environmental Risk API")

class RiskResult(BaseModel):
    fluvial_flood: Dict
    coastal_flood: Dict
    fire: Dict
    desertification: Dict

def ensure_dict(data):
    return data if isinstance(data, dict) else {"error": str(data)}

@app.get("/risk", response_model=RiskResult)
def get_risks(lat: float = Query(...), lon: float = Query(...)):
    return {
        "fluvial_flood": ensure_dict(fluvial_flood_risks.run(lat, lon)),
        "coastal_flood": ensure_dict(coastal_flood_risks.run(lat, lon)),
        "fire": ensure_dict(fire_kml_old.run(lat, lon)),
        "desertification": ensure_dict(desert.run(lat, lon)),
    }

# python -m venv venv
# source venv/bin/activate  # or `venv\Scripts\activate` on Windows
# pip install -r requirements.txt
# uvicorn main:app --reload


# test url
# http://127.0.0.1:8000/risk?lat=41.27270457818908&lon=2.0520473550222307