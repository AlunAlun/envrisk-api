from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse
from typing import Dict
import requests
from xml.etree import ElementTree as ET

import risk_fluvial_flood
import risk_coastal_flood
import risk_fire
import risk_desert
import data_load_fire
import data_load_desert

app = FastAPI(title="Environmental Risk API")

# ✅ Allow cross-origin from localhost:3000 (React dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://clownfish-app-hrwwx.ondigitalocean.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Risk Model ===
class RiskResult(BaseModel):
    fluvial_flood: Dict
    coastal_flood: Dict
    fire: Dict
    desertification: Dict

def ensure_dict(data):
    return data if isinstance(data, dict) else {"error": str(data)}

# === Load data on startup ===
@app.on_event("startup")
def load_datasets():
    # Fire datasets
    _ = data_load_fire.geojson_9605
    _ = data_load_fire.geojson_0615
    _ = data_load_fire.polys_9605
    _ = data_load_fire.polys_0615
    print("✅ Fire datasets loaded into memory.")

    # Desertification datasets
    _ = data_load_desert.gdf
    _ = data_load_desert.gdf2
    print("✅ Desertification datasets loaded into memory.")

# === Combined Risk Endpoint ===
@app.get("/risk", response_model=RiskResult)
def get_risks(lat: float = Query(...), lon: float = Query(...)):
    return {
        "fluvial_flood": ensure_dict(risk_fluvial_flood.run(lat, lon)),
        "coastal_flood": ensure_dict(risk_coastal_flood.run(lat, lon)),
        "fire": ensure_dict(risk_fire.run(lat, lon)),
        "desertification": ensure_dict(risk_desert.run(lat, lon)),
    }

@app.get("/risk/fire")
def get_fire(lat: float, lon: float):
    return {"fire": ensure_dict(risk_fire.run(lat, lon))}

@app.get("/risk/flood")
def get_flood(lat: float, lon: float):
    return {
        "fluvial_flood": ensure_dict(risk_fluvial_flood.run(lat, lon)),
        "coastal_flood": ensure_dict(risk_coastal_flood.run(lat, lon)),
    }

@app.get("/risk/desert")
def get_desert(lat: float, lon: float):
    return {"desertification": ensure_dict(risk_desert.run(lat, lon))}

## python -m venv venv
# source venv/bin/activate  # or `venv\Scripts\activate` on Windows
## pip install -r requirements.txt
# uvicorn main:app --reload


# test url
# http://127.0.0.1:8000/risk?lat=41.27270457818908&lon=2.0520473550222307