from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.strtree import STRtree
from shapely.ops import transform
from pyproj import Transformer
from io import BytesIO
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
import base64
import geopandas as gpd

def filter_polygons_near_pointn(polygons_with_values, lat, lon, max_km=100):
    # Step 1: Build GeoDataFrame from input list
    geometries = []
    values = []

    for poly, val in polygons_with_values:
        if isinstance(poly, (Polygon, MultiPolygon)) and poly.is_valid:
            geometries.append(poly)
            values.append(val)

    gdf = gpd.GeoDataFrame({'geometry': geometries, 'value': values}, geometry='geometry', crs='EPSG:4326')

    # Step 2: Project to EPSG:25830 for distance calculation
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
    gdf_proj = gdf.to_crs("EPSG:25830")

    # Step 3: Create projected point and buffer box
    x, y = transformer.transform(lon, lat)
    point_proj = Point(x, y)
    buffer_m = max_km * 1000
    bbox = box(x - buffer_m, y - buffer_m, x + buffer_m, y + buffer_m)

    # Step 4: Spatial index query
    sindex = gdf_proj.sindex
    candidate_idx = list(sindex.intersection(bbox.bounds))
    candidates = gdf_proj.iloc[candidate_idx]

    # Step 5: Final filter based on centroid distance
    nearby = []
    for _, row in candidates.iterrows():
        try:
            centroid = row.geometry.centroid
            if point_proj.distance(centroid) <= buffer_m:
                val = float(row.value) if row.value not in [None, ""] else 0.0
                nearby.append((row.geometry, val))
        except Exception as e:
            print(f"⚠️ Skipping geometry: {e}")

    print(f"✅ Found {len(nearby)} nearby polygons")
    return nearby




def filter_polygons_near_point(polygons_with_values, lat, lon, max_km=100):
    point_wgs = Point(lon, lat)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
    point_proj = transform(transformer.transform, point_wgs)

    nearby = []
    for poly, value in polygons_with_values:
        if not poly.is_valid:
            continue
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            numeric_value = 0.0

        centroid_proj = transform(transformer.transform, poly.centroid)
        if point_proj.distance(centroid_proj) <= max_km * 1000:
            nearby.append((poly, numeric_value))
    return nearby

def generate_fire_map(poly_and_values, lat, lon):
    point = Point(lon, lat)
    fig, ax = plt.subplots(figsize=(6, 5))

    fire_counts = [v for _, v in poly_and_values if v is not None]
    if not fire_counts:
        return ""

    norm = Normalize(vmin=min(fire_counts), vmax=max(fire_counts))
    cmap = cm.Reds

    for poly, value in poly_and_values:
        if isinstance(poly, Polygon):
            x, y = poly.exterior.xy
            color = cmap(norm(value)) if value is not None else "#cccccc"
            ax.fill(x, y, color=color, edgecolor="k", linewidth=0.2, alpha=0.7)

    ax.scatter(lon, lat, color="black", marker="x", s=100, linewidths=2)
    ax.axis("off")
    plt.tight_layout(pad=0)

    buf_png = BytesIO()
    plt.savefig(buf_png, format="png", dpi=100, bbox_inches="tight", pad_inches=0)
    plt.close()
    buf_png.seek(0)

    image = Image.open(buf_png).convert("RGB")
    buf_jpg = BytesIO()
    image.save(buf_jpg, format="JPEG", quality=80, optimize=True)
    buf_jpg.seek(0)

    base64_img = base64.b64encode(buf_jpg.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_img}"

def filter_polygons_near_point_desert(gdf, lat, lon, max_km=100):
    """
    Use spatial index to find polygons within max_km of the point.
    """
    # Transform point to projected coords (for distance in meters)
    point_wgs = Point(lon, lat)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
    x, y = transformer.transform(lon, lat)

    buffer_m = max_km * 1000
    bbox = box(x - buffer_m, y - buffer_m, x + buffer_m, y + buffer_m)

    # Reproject bbox back to WGS84 for filtering
    transformer_back = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)
    min_lon, min_lat = transformer_back.transform(bbox.bounds[0], bbox.bounds[1])
    max_lon, max_lat = transformer_back.transform(bbox.bounds[2], bbox.bounds[3])
    query_box = box(min_lon, min_lat, max_lon, max_lat)

    # Use spatial index to pre-select candidates
    possible_matches_index = list(gdf.sindex.intersection(query_box.bounds))
    possible_matches = gdf.iloc[possible_matches_index]

    # Final filter: check exact distance to centroid in projected coords
    point_proj = Point(x, y)
    transformer_centroids = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)

    def within_distance(row):
        try:
            centroid = row.geometry.centroid
            cx, cy = transformer_centroids.transform(centroid.x, centroid.y)
            return point_proj.distance(Point(cx, cy)) <= buffer_m
        except:
            return False

    return possible_matches[possible_matches.apply(within_distance, axis=1)]


def plot_full_dataset_with_point(GDF, lat, lon, risk_labels, risk_colors):
    GDF = filter_polygons_near_point_desert(GDF, lat, lon, max_km=100)

    point = Point(lon, lat)

    fig, ax = plt.subplots(figsize=(6, 5))

    GDF["color"] = GDF["DESER_CLA"].map(risk_colors).fillna("black")
    GDF.plot(ax=ax, color=GDF["color"], alpha=0.5, edgecolor="k", linewidth=0.2)

    # Plot black X for queried location
    ax.scatter(lon, lat, color="black", marker="x", s=100, linewidths=2)

    # Remove all non-essentials
    ax.axis("off")

    plt.tight_layout(pad=0)  # Minimize surrounding space

    # Save to PNG buffer
    buf_png = BytesIO()
    plt.savefig(buf_png, format="png", dpi=100, bbox_inches="tight", pad_inches=0)
    plt.close()
    buf_png.seek(0)

    # Convert to optimized JPEG
    image = Image.open(buf_png).convert("RGB")
    buf_jpg = BytesIO()
    image.save(buf_jpg, format="JPEG", quality=80, optimize=True)
    buf_jpg.seek(0)

    # Encode to base64
    base64_img = base64.b64encode(buf_jpg.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_img}"
