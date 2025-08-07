from shapely.geometry import shape, Point
import data_load_fire  # import the preloaded module
from utils import filter_polygons_near_point, generate_fire_map  # reuse existing helpers

def run(lat, lon):
    point = Point(lon, lat)
    output = {}

    # === 1. Match polygons containing the point ===
    match_9605 = next((f for f in data_load_fire.geojson_9605["features"] if shape(f["geometry"]).contains(point)), None)
    match_0615 = next((f for f in data_load_fire.geojson_0615["features"] if shape(f["geometry"]).contains(point)), None)

    output["96_05"] = {
        "name": match_9605["properties"].get("Término municipal", "Unknown"),
        "data": match_9605["properties"]
    } if match_9605 else "No risk"

    output["06_15"] = {
        "name": match_0615["properties"].get("Término municipal", "Unknown"),
        "data": match_0615["properties"]
    } if match_0615 else "No risk"

    # === 2. Filter nearby polygons ===
    filtered_9605 = filter_polygons_near_point(data_load_fire.polys_9605, lat, lon)
    filtered_0615 = filter_polygons_near_point(data_load_fire.polys_0615, lat, lon)

    # === 3. Generate fire maps ===
    output["image_96_05"] = generate_fire_map(filtered_9605, lat, lon)
    output["image_06_15"] = generate_fire_map(filtered_0615, lat, lon)

    return output
