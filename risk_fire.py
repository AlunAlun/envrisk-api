import time
from shapely.geometry import shape, Point
import data_load_fire  # import the preloaded module
from utils import filter_polygons_near_point, generate_fire_map  # reuse existing helpers

def run(lat, lon):
    t0 = time.perf_counter()
    point = Point(lon, lat)
    output = {}

    # === 1. Match polygons containing the point ===
    t1 = time.perf_counter()
    match_9605 = next((f for f in data_load_fire.geojson_9605["features"] if shape(f["geometry"]).contains(point)), None)
    match_0615 = next((f for f in data_load_fire.geojson_0615["features"] if shape(f["geometry"]).contains(point)), None)
    t2 = time.perf_counter()
    print(f"⏱️ Point match time: {t2 - t1:.3f} seconds")

    output["96_05"] = {
        "name": match_9605["properties"].get("Término municipal", "Unknown"),
        "data": match_9605["properties"]
    } if match_9605 else "No risk"

    output["06_15"] = {
        "name": match_0615["properties"].get("Término municipal", "Unknown"),
        "data": match_0615["properties"]
    } if match_0615 else "No risk"

    # === 2. Filter nearby polygons ===
    t3 = time.perf_counter()
    filtered_9605 = filter_polygons_near_point(data_load_fire.polys_9605, lat, lon)
    filtered_0615 = filter_polygons_near_point(data_load_fire.polys_0615, lat, lon)
    t4 = time.perf_counter()
    print(f"⏱️ Filter polygons time: {t4 - t3:.3f} seconds")

    # === 3. Generate fire maps ===
    t5 = time.perf_counter()
    output["image_96_05"] = generate_fire_map(filtered_9605, lat, lon)
    output["image_06_15"] = generate_fire_map(filtered_0615, lat, lon)
    t6 = time.perf_counter()
    print(f"⏱️ Map generation time: {t6 - t5:.3f} seconds")

    # === Total time ===
    print(f"⏱️ Total fire risk run time: {t6 - t0:.3f} seconds")

    return output




# from shapely.geometry import shape, Point
# import data_load_fire  # import the preloaded module
# from utils import filter_polygons_near_point, generate_fire_map  # reuse existing helpers

# def run(lat, lon):
#     point = Point(lon, lat)
#     output = {}

#     match_9605 = next((f for f in data_load_fire.geojson_9605["features"] if shape(f["geometry"]).contains(point)), None)
#     match_0615 = next((f for f in data_load_fire.geojson_0615["features"] if shape(f["geometry"]).contains(point)), None)
#     print(match_9605)

#     output["96_05"] = {
#         "name": match_9605["properties"].get("Término municipal", "Unknown"),
#         "data": match_9605["properties"]
#     } if match_9605 else "No risk"

#     output["06_15"] = {
#         "name": match_0615["properties"].get("Término municipal", "Unknown"),
#         "data": match_0615["properties"]
#     } if match_0615 else "No risk"

#     filtered_9605 = filter_polygons_near_point(data_load_fire.polys_9605, lat, lon)
#     filtered_0615 = filter_polygons_near_point(data_load_fire.polys_0615, lat, lon)
    

#     output["image_96_05"] = generate_fire_map(filtered_9605, lat, lon)
#     output["image_06_15"] = generate_fire_map(filtered_0615, lat, lon)

#     return output



