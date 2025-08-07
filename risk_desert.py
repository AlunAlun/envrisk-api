from shapely.geometry import Point
from data_load_desert import gdf, gdf2  # ✅ Preloaded at import
from utils import filter_polygons_near_point_desert, plot_full_dataset_with_point
import base64

# === Risk code mapping ===
RISK_LABELS = {
    1: "BAJO (Low)",
    2: "MEDIO (Medium)",
    3: "ALTO (High)",
    4: "MUY ALTO (Very High)",
    8: "LÁMINAS DE AGUA (Water bodies)",
    9: "URBANO (Urban)",
    99: "FUERA DE PROGRAMA (Outside programme)"
}

RISK_COLORS = {
    1: "green",
    2: "yellow",
    3: "orange",
    4: "red",
    8: "blue",
    9: "gray",
    99: "white"
}

def get_desertification_risk(lat, lon, GDF):
    point = Point(lon, lat)
    match = GDF[GDF.contains(point)]

    if match.empty:
        return "No Data"
    
    risk_code = int(match.iloc[0]["DESER_CLA"])
    return RISK_LABELS.get(risk_code, f"Unknown code: {risk_code}")

def run(latitude, longitude):
    risk = get_desertification_risk(latitude, longitude, gdf)
    image_base64 = ""
    if risk != "No Data":
        image_base64 = plot_full_dataset_with_point(gdf, latitude, longitude, RISK_LABELS, RISK_COLORS)
    else:
        risk = get_desertification_risk(latitude, longitude, gdf2)
        # Optional: generate second image for Canarias if needed
        image_base64 = plot_full_dataset_with_point(gdf2, latitude, longitude, RISK_LABELS, RISK_COLORS)
    print("Desert risks successfully returned.")
    return {"risk": risk, "img": image_base64}