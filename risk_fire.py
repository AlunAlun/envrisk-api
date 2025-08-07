from shapely.geometry import shape, Point
import data_load_fire  # import the preloaded module
from utils import filter_polygons_near_point, generate_fire_map  # reuse existing helpers

def run(lat, lon):
    point = Point(lon, lat)
    output = {}

    match_9605 = next((f for f in data_load_fire.geojson_9605["features"] if shape(f["geometry"]).contains(point)), None)
    match_0615 = next((f for f in data_load_fire.geojson_0615["features"] if shape(f["geometry"]).contains(point)), None)
    print(match_9605)

    output["96_05"] = {
        "name": match_9605["properties"].get("Término municipal", "Unknown"),
        "data": match_9605["properties"]
    } if match_9605 else "No risk"

    output["06_15"] = {
        "name": match_0615["properties"].get("Término municipal", "Unknown"),
        "data": match_0615["properties"]
    } if match_0615 else "No risk"

    filtered_9605 = filter_polygons_near_point(data_load_fire.polys_9605, lat, lon)
    filtered_0615 = filter_polygons_near_point(data_load_fire.polys_0615, lat, lon)
    

    output["image_96_05"] = generate_fire_map(filtered_9605, lat, lon)
    output["image_06_15"] = generate_fire_map(filtered_0615, lat, lon)

    return output



# import json
# from shapely.geometry import shape, Point, Polygon
# from shapely.ops import transform
# from shapely.validation import explain_validity
# from pyproj import Transformer
# from io import BytesIO
# import base64
# from PIL import Image
# import matplotlib.pyplot as plt
# from matplotlib import cm
# from matplotlib.colors import Normalize

# def load_geojson(filepath):
#     with open(filepath, "r", encoding="utf-8") as f:
#         return json.load(f)

# def filter_polygons_near_point(polygons_with_values, lat, lon, max_km=100):
#     point_wgs = Point(lon, lat)
#     transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
#     point_proj = transform(transformer.transform, point_wgs)

#     nearby = []
#     for poly, value in polygons_with_values:
#         if not poly.is_valid:
#             continue
#         try:
#             numeric_value = float(value)
#         except (ValueError, TypeError):
#             numeric_value = 0.0

#         centroid_proj = transform(transformer.transform, poly.centroid)
#         if point_proj.distance(centroid_proj) <= max_km * 1000:
#             nearby.append((poly, numeric_value))
#     return nearby

# def generate_fire_map(poly_and_values, lat, lon):
#     point = Point(lon, lat)
#     fig, ax = plt.subplots(figsize=(6, 5))

#     fire_counts = [v for _, v in poly_and_values if v is not None]
#     if not fire_counts:
#         return ""

#     norm = Normalize(vmin=min(fire_counts), vmax=max(fire_counts))
#     cmap = cm.Reds

#     for poly, value in poly_and_values:
#         if isinstance(poly, Polygon):
#             x, y = poly.exterior.xy
#             color = cmap(norm(value)) if value is not None else "#cccccc"
#             ax.fill(x, y, color=color, edgecolor="k", linewidth=0.2, alpha=0.7)

#     ax.scatter(lon, lat, color="black", marker="x", s=100, linewidths=2)
#     ax.axis("off")
#     plt.tight_layout(pad=0)

#     buf_png = BytesIO()
#     plt.savefig(buf_png, format="png", dpi=100, bbox_inches="tight", pad_inches=0)
#     plt.close()
#     buf_png.seek(0)

#     image = Image.open(buf_png).convert("RGB")
#     buf_jpg = BytesIO()
#     image.save(buf_jpg, format="JPEG", quality=80, optimize=True)
#     buf_jpg.seek(0)

#     base64_img = base64.b64encode(buf_jpg.read()).decode("utf-8")
#     return f"data:image/jpeg;base64,{base64_img}"

# def extract_polygons_and_values(geojson):
#     result = []

#     for feature in geojson["features"]:
#         try:
#             poly = shape(feature["geometry"])
#             desc_html = feature["properties"].get("description", "")

#             fire_count = None

#             if desc_html:
#                 # Parse the HTML safely
#                 soup = BeautifulSoup(unescape(desc_html), "html.parser")
#                 inner_table = soup.find("table")
#                 if inner_table:
#                     nested_table = inner_table.find("table")
#                     if nested_table:
#                         rows = nested_table.find_all("tr")
#                         for row in rows:
#                             cells = row.find_all("td")
#                             if len(cells) == 2:
#                                 key = cells[0].get_text(strip=True).lower()
#                                 val = cells[1].get_text(strip=True).replace(".", "").replace(",", "")
#                                 if "nº total de incendios" in key:
#                                     fire_count = int(val)
#                                     break

#             result.append((poly, fire_count))
#         except Exception as e:
#             print("⚠️ Skipped a feature:", e)

#     return result

# def run(lat, lon):
#     output = {}

#     data_9605 = load_geojson("data/fire_1996_2005.geojson")
#     data_0615 = load_geojson("data/fire_2006_2015.geojson")

#     polys_9605 = extract_polygons_and_values(data_9605)
#     polys_0615 = extract_polygons_and_values(data_0615)

#     point = Point(lon, lat)

#     match_9605 = next((val for poly, val in polys_9605 if poly.contains(point)), None)
#     match_0615 = next((val for poly, val in polys_0615 if poly.contains(point)), None)
#     # match_9605 = next((f for f in data_9605["features"] if shape(f["geometry"]).contains(point)), None)
#     # match_0615 = next((f for f in data_0615["features"] if shape(f["geometry"]).contains(point)), None)

#     if match_9605:
#         output['96_05'] = {
#             "name": match_9605["properties"].get("name", "Unknown"),
#             "data": match_9605["properties"].get("description", {})
#         }
#     else:
#         output['96_05'] = "No risk"

#     if match_0615:
#         output['06_15'] = {
#             "name": match_0615["properties"].get("name", "Unknown"),
#             "data": match_0615["properties"].get("description", {})
#         }
#     else:
#         output['06_15'] = "No risk"

#     filtered_9605 = filter_polygons_near_point(polys_9605, lat, lon)
#     filtered_0615 = filter_polygons_near_point(polys_0615, lat, lon)
#     output['image_96_05'] = generate_fire_map(filtered_9605, lat, lon)
#     output['image_06_15'] = generate_fire_map(filtered_0615, lat, lon)

#     return output

# # print(run(41.27270457818908, 2.0520473550222307))