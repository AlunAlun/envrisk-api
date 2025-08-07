import requests
from pyproj import Transformer

LAYERS = {
    "HazardArea2015.PGA475_p": {
        "description": "Peak Ground Acceleration (g) with 475-year return period.",
        "property": "PGA_g",
    },
    "HazardArea2015.PGA475_c": {
        "description": "PGA isolines for seismic hazard mapping.",
        "property": None
    },
    "HazardArea2015.Int475": {
        "description": "Expected seismic intensity with 475-year return period.",
        "property": "Int475",
    },
    "HazardArea2002.NCSE-02": {
        "description": "Seismic hazard based on NCSE-02 norm (2002).",
        "property": "ab",
    },
    "NZ.ObservedEvent": {
        "description": "Full earthquake catalog from 1370 to present.",
        "property": "magnitude",
    },
    "Ultimos10dias": {
        "description": "Recent earthquakes (last 10 days).",
        "property": "magnitude",
    },
    "Ultimos30dias": {
        "description": "Recent earthquakes (last 30 days).",
        "property": "magnitude",
    },
    "Ultimos365dias": {
        "description": "Recent earthquakes (last 12 months).",
        "property": "magnitude",
    },
    "GE.Geophysics.seismologicalStation": {
        "description": "Seismic velocity stations of the IGN.",
        "property": "stationCode",
    },
}

def run(lat, lon):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(lon, lat)

    buffer = 76 / 2
    minx = x - buffer
    maxx = x + buffer
    miny = y - buffer
    maxy = y + buffer

    def build_url(layer):
        return (
            "https://www.ign.es/wms-inspire/geofisica?"
            "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo"
            "&FORMAT=image/png"
            "&TRANSPARENT=true"
            f"&LAYERS={layer}"
            f"&QUERY_LAYERS={layer}"
            "&STYLES="
            "&WIDTH=256&HEIGHT=256"
            "&CRS=EPSG:3857"
            f"&BBOX={minx},{miny},{maxx},{maxy}"
            "&I=128&J=128"
            "&INFO_FORMAT=application/json"
        )

    def fetch_data(url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching seismic data from IGN:\n  {e}")
            return None

    output = {}

    for layer_name, meta in LAYERS.items():
        url = build_url(layer_name)
        if (layer_name != "HazardArea2002.NCSE-02"):
            continue
        data = fetch_data(url)

        if data and data.get("features") and len(data["features"]) > 0:
            feature_list = []
            for feature in data["features"]:
                parsed = {
                    "id": feature.get("id"),
                    "properties": feature.get("properties"),
                    "geometry": feature.get("geometry"),
                }
                feature_list.append(parsed)

            output[layer_name] = {
                "description": meta.get("description", ""),
                "features": feature_list
            }
            print(f"✓ {layer_name} returned {len(feature_list)} features.")
        else:
            output[layer_name] = {
                "description": meta.get("description", ""),
                "features": []
            }
            print(f"⚠ {layer_name} returned no features.")
    return output

