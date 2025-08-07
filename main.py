from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import JSONResponse
from auth import verify_token
from fastapi import Depends
from typing import Dict
import requests
from xml.etree import ElementTree as ET
import time
import logging

import risk_fluvial_flood
import risk_coastal_flood
import risk_fire
import risk_desert
import risk_seismic
import data_load_fire
import data_load_desert

# Optional: configure logging if not already set
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Environmental Risk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://clownfish-app-hrwwx.ondigitalocean.app",
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
    seismic: Dict

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

# # === Combined Risk Endpoint ===
# @app.get("/risk", response_model=RiskResult)
# def get_risks(lat: float = Query(...), lon: float = Query(...)):
#     return {
#         "fluvial_flood": ensure_dict(risk_fluvial_flood.run(lat, lon)),
#         "coastal_flood": ensure_dict(risk_coastal_flood.run(lat, lon)),
#         "fire": ensure_dict(risk_fire.run(lat, lon)),
#         "desertification": ensure_dict(risk_desert.run(lat, lon)),
#     }



@app.get("/risk", response_model=RiskResult, dependencies=[Depends(verify_token)])
def get_risks(
    lat: float = Query(...), 
    lon: float = Query(...),
    token_data: dict = Depends(verify_token)
    ):
    print(f"Authenticated request by: {token_data['sub']}") # or 'email', or 'name'
    start_total = time.time()

    start = time.time()
    fluvial = ensure_dict(risk_fluvial_flood.run(lat, lon))
    logging.info(f"Fluvial flood risk took {time.time() - start:.2f}s")

    start = time.time()
    coastal = ensure_dict(risk_coastal_flood.run(lat, lon))
    logging.info(f"Coastal flood risk took {time.time() - start:.2f}s")

    start = time.time()
    fire = ensure_dict(risk_fire.run(lat, lon))
    logging.info(f"Fire risk took {time.time() - start:.2f}s")

    start = time.time()
    desert = ensure_dict(risk_desert.run(lat, lon))
    logging.info(f"Desertification risk took {time.time() - start:.2f}s")

    start = time.time()
    seismic = ensure_dict(risk_seismic.run(lat, lon))
    logging.info(f"Seismic risk took {time.time() - start:.2f}s")

    total_time = time.time() - start_total
    logging.info(f"Total /risk endpoint processing time: {total_time:.2f}s")

    return {
        "fluvial_flood": fluvial,
        "coastal_flood": coastal,
        "fire": fire,
        "desertification": desert,
        "seismic": seismic,
    }

@app.get("/risk/fire", dependencies=[Depends(verify_token)])
def get_fire(lat: float, lon: float):
    return {"fire": ensure_dict(risk_fire.run(lat, lon))}

@app.get("/risk/flood", dependencies=[Depends(verify_token)])
def get_flood(lat: float, lon: float):
    return {
        "fluvial_flood": ensure_dict(risk_fluvial_flood.run(lat, lon)),
        "coastal_flood": ensure_dict(risk_coastal_flood.run(lat, lon)),
    }

@app.get("/risk/desert", dependencies=[Depends(verify_token)])
def get_desert(lat: float, lon: float):
    return {"desertification": ensure_dict(risk_desert.run(lat, lon))}

@app.get("/risk/seismic", dependencies=[Depends(verify_token)])
def get_seismic_risk(lat: float = Query(...), lon: float = Query(...)) -> Dict:
    return {
        "seismic": ensure_dict(risk_seismic.run(lat, lon)),
    }

## python -m venv venv
# source venv/bin/activate  # or `venv\Scripts\activate` on Windows
## pip install -r requirements.txt
# uvicorn main:app --reload


# test url
# http://127.0.0.1:8000/risk?lat=41.27270457818908&lon=2.0520473550222307