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
    return {"risk": risk, "img": image_base64}




# from PIL import Image
# import geopandas as gpd
# from shapely.geometry import Point
# from pyproj import CRS
# import matplotlib
# matplotlib.use("Agg")  # ✅ non-interactive backend
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# import os
# import base64
# from io import BytesIO
# from pyproj import Transformer
# from shapely.ops import transform

# # === 1. Load shapefile ===
# shapefile_path = "data/pand_p.shp"  # Adjust if running locally
# gdf = gpd.read_file(shapefile_path)

# shapefile_path2 = "data/pand_c.shp"  # Adjust if running locally
# gdf2 = gpd.read_file(shapefile_path2)

# # === 2. Reproject to EPSG:4326 if needed ===
# if gdf.crs != "EPSG:4326":
#     gdf = gdf.to_crs("EPSG:4326")
# if gdf2.crs != "EPSG:4326":
#     gdf2 = gdf2.to_crs("EPSG:4326")

# # === 3. Risk code mapping ===
# RISK_LABELS = {
#     1: "BAJO (Low)",
#     2: "MEDIO (Medium)",
#     3: "ALTO (High)",
#     4: "MUY ALTO (Very High)",
#     8: "LÁMINAS DE AGUA (Water bodies)",
#     9: "URBANO (Urban)",
#     99: "FUERA DE PROGRAMA (Outside programme)"
# }

# RISK_COLORS = {
#     1: "green",
#     2: "yellow",
#     3: "orange",
#     4: "red",
#     8: "blue",
#     9: "gray",
#     99: "white"
# }

# # === 4. Main function ===
# def get_desertification_risk(lat, lon, GDF):
#     point = Point(lon, lat)  # Note: (lon, lat) order
#     match = GDF[GDF.contains(point)]

#     if match.empty:
#         return "No Data"
    
#     risk_code = int(match.iloc[0]["DESER_CLA"])
#     return RISK_LABELS.get(risk_code, f"Unknown code: {risk_code}")

# def filter_polygons_near_point_desert(gdf, lat, lon, max_km=100):
#     """
#     Filter GeoDataFrame to only include polygons whose centroid is within max_km of a given point.
#     Returns a filtered GeoDataFrame.
#     """
#     point_wgs = Point(lon, lat)
#     transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
#     point_proj = transform(transformer.transform, point_wgs)

#     nearby_indices = []
#     for idx, row in gdf.iterrows():
#         geom = row.geometry
#         if geom.is_valid:
#             centroid_proj = transform(transformer.transform, geom.centroid)
#             if point_proj.distance(centroid_proj) <= max_km * 1000:
#                 nearby_indices.append(idx)

#     return gdf.loc[nearby_indices]

# def plot_full_dataset_with_point(GDF, lat, lon):
#     GDF = filter_polygons_near_point_desert(GDF, lat, lon, max_km=100)
#     point = Point(lon, lat)

#     fig, ax = plt.subplots(figsize=(6, 5))

#     for code in RISK_LABELS.keys():
#         subset = GDF[GDF["DESER_CLA"] == code]
#         color = RISK_COLORS.get(code, "black")
#         subset.plot(ax=ax, color=color, alpha=0.5, edgecolor="k", linewidth=0.2)

#     # Plot black X for queried location
#     ax.scatter(lon, lat, color="black", marker="x", s=100, linewidths=2)

#     # Remove all non-essentials
#     ax.axis("off")

#     plt.tight_layout(pad=0)  # Minimize surrounding space

#     # Save to PNG buffer
#     buf_png = BytesIO()
#     plt.savefig(buf_png, format="png", dpi=100, bbox_inches="tight", pad_inches=0)
#     plt.close()
#     buf_png.seek(0)

#     # Convert to optimized JPEG
#     image = Image.open(buf_png).convert("RGB")
#     buf_jpg = BytesIO()
#     image.save(buf_jpg, format="JPEG", quality=80, optimize=True)
#     buf_jpg.seek(0)

#     # Encode to base64
#     base64_img = base64.b64encode(buf_jpg.read()).decode("utf-8")
#     return f"data:image/jpeg;base64,{base64_img}"

# # === 5. Example usage ===
# def run(latitude, longitude):
#     # High risk
#     # latitude = 37.216683162769684
#     # longitude = -7.316882654272187
#     # medium risk
#     # latitude = 37.272084560683986
#     # longitude = -7.115860474641874
#     #canarias
#     # latitude = 28.391352258611125
#     # longitude =  -13.99126909512573
#     # asturias
#     # latitude = 42.97697120364747
#     # longitude = -5.850930512651173
#     # outside
#     # latitude = 31.144015780847376
#     # longitude = -11.430494039736288

#     risk = get_desertification_risk(latitude, longitude, gdf)
#     image_base64 = ""
#     if risk != "No Data":
#         print()
#         image_base64 = plot_full_dataset_with_point(gdf, latitude, longitude)
#     else:
#         print("trying canarias...")
#         risk = get_desertification_risk(latitude, longitude, gdf2)
#         # if risk != "No Data":
#         #     image_base64 = plot_full_dataset_with_point(gdf2, latitude, longitude)
#     return {"risk": risk, 'img': image_base64}

# # output = run(37.216683162769684, -7.316882654272187)
# # print(output)
    

