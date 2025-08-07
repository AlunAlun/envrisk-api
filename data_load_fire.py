import json
from shapely.geometry import shape, Polygon

def load_geojson(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_polygons_and_values(geojson):
    result = []
    for feature in geojson["features"]:
        try:
            poly = shape(feature["geometry"])

            # Directly access the flat properties
            properties = feature["properties"]
            fire_count = None

            for key, val in properties.items():
                if "incendios" in key.lower():
                    try:
                        fire_count = int(val.replace(".", "").replace(",", ""))
                        break
                    except Exception as e:
                        print(f"⚠️ Could not parse fire count: {val}")
                        fire_count = None

            result.append((poly, fire_count))
        except Exception as e:
            print("⚠️ Skipped a feature:", e)
    return result


# === Load at startup ===
geojson_9605 = load_geojson("data/fire_1996_2005.geojson")
geojson_0615 = load_geojson("data/fire_2006_2015.geojson")

polys_9605 = extract_polygons_and_values(geojson_9605)
polys_0615 = extract_polygons_and_values(geojson_0615)
