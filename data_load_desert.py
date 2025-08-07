import geopandas as gpd

# === Load shapefiles once ===
shapefile_path1 = "data/pand_p.shp"
shapefile_path2 = "data/pand_c.shp"

gdf = gpd.read_file(shapefile_path1)
gdf2 = gpd.read_file(shapefile_path2)

# Reproject if needed
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")
if gdf2.crs != "EPSG:4326":
    gdf2 = gdf2.to_crs("EPSG:4326")
