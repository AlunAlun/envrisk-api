import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, Point
from shapely.validation import explain_validity
from zipfile import ZipFile
from io import BytesIO
import re
from html import unescape
import json
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.ops import transform
from pyproj import Transformer
from matplotlib import cm
from matplotlib.colors import Normalize


def load_kml_content(file_path):
    if file_path.endswith(".kmz"):
        with ZipFile(file_path, 'r') as zf:
            for name in zf.namelist():
                if name.endswith(".kml"):
                    return zf.read(name).decode("utf-8")
        raise Exception("No .kml file found in KMZ")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

def parse_coordinates(coord_text):
    coords = []
    for line in coord_text.strip().split():
        parts = line.strip().split(",")
        if len(parts) >= 2:
            lon, lat = float(parts[0]), float(parts[1])
            coords.append((lon, lat))
    return coords

def extract_polygons(placemark_elem):
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    polygons = []

    # Handle both direct <Polygon> and those nested within <MultiGeometry>
    polygon_elems = placemark_elem.findall(".//kml:Polygon", ns)

    for idx, polygon in enumerate(polygon_elems):
        outer = polygon.find(".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
        if outer is None:
            continue

        outer_coords = parse_coordinates(outer.text)
        inner_rings = polygon.findall(".//kml:innerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
        holes = [parse_coordinates(inner.text) for inner in inner_rings]

        try:
            poly = Polygon(outer_coords, holes)

            if poly.is_valid:
                polygons.append(poly)
            else:
                # print(f"❌ Polygon {idx} invalid: {explain_validity(poly)}")
                repaired = poly.buffer(0)
                if repaired.is_valid:
                    # print(f"✅ Polygon {idx} repaired successfully")
                    polygons.append(repaired)
                else:
                    print(f"⚠️ Polygon {idx} still invalid after repair: {explain_validity(repaired)}")

        except Exception as e:
            print(f"⚠️ Error creating polygon {idx}: {e}")

    return polygons


def description_table_to_json(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    
    # Find all tables and select the second one (first is just the image header)
    tables = soup.find_all("table")
    if len(tables) < 2:
        return {}

    data_table = tables[0].find("table")  # Nested table with the data
    result = {}

    for row in data_table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            key = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            result[key] = value

    return json.dumps(result, ensure_ascii=False, separators=(',', ':'))


def filter_polygons_near_point(polygons_with_values, lat, lon, max_km=100):
    """
    Returns only (polygon, value) pairs whose centroid is within max_km of the query point.
    Falls back to 0 if the value is missing or non-numeric.
    """
    point_wgs = Point(lon, lat)

    # Use a projected CRS in meters for distance (UTM zone for Spain)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25830", always_xy=True)
    point_proj = transform(transformer.transform, point_wgs)

    nearby = []
    for poly, value in polygons_with_values:
        if not poly.is_valid:
            continue

        # Fallback for invalid or missing values
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            numeric_value = 0.0

        centroid_proj = transform(transformer.transform, poly.centroid)
        if point_proj.distance(centroid_proj) <= max_km * 1000:
            nearby.append((poly, numeric_value))

    return nearby


def find_placemark_from_kmz(lat, lon, kmz_path, debug_keyword=None):
    point = Point(lon, lat)
    kml_text = load_kml_content(kmz_path)
    root = ET.fromstring(kml_text)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    placemarks = root.findall(".//kml:Placemark", ns)

    all_polygons = []
    matched_result = None

    for placemark in placemarks:
        name = placemark.find("kml:name", ns)
        description = placemark.find("kml:description", ns)
        name_text = name.text.strip() if name is not None else "(Unnamed)"
        desc_text = description.text.strip() if description is not None else ""

        if debug_keyword and debug_keyword.lower() not in name_text.lower():
            continue

        polygons = extract_polygons(placemark)
        data_json = description_table_to_json(desc_text)
        data = json.loads(data_json)

        fire_count = None
        for key in data:
            if "incendios" in key.lower():
                try:
                    fire_count = int(data[key].replace(".", "").replace(",", ""))
                except:
                    fire_count = None
                break

        for poly in polygons:
            all_polygons.append((poly, fire_count))

            if matched_result is None and poly.contains(point):
                print(f"✅ MATCH in placemark: {name_text}")
                matched_result = {
                    "name": name_text,
                    "description_json": data_json
                }

    return matched_result, all_polygons

def generate_fire_map(poly_and_values, lat, lon):
    point = Point(lon, lat)
    fig, ax = plt.subplots(figsize=(6, 5))

    # Extract fire counts and normalize
    fire_counts = [v for _, v in poly_and_values if v is not None]
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

def run(latitude, longitude):
    output = {}
    FILE_2006_2015 = "data/frecuenciadeincendiosperiodo2006a2015_tcm30-525840.kmz"
    FILE_1996_2005 = "data/frecuenciadeincendiosperiodo1996a2005_tcm30-199965.kmz"

    result_9605, polys_9605 = find_placemark_from_kmz(latitude, longitude, FILE_1996_2005)
    result_0615, polys_0615 = find_placemark_from_kmz(latitude, longitude, FILE_2006_2015)

    if result_9605:
        output['96_05'] = {
            'name': result_9605["name"],
            'data': json.loads(result_9605["description_json"])
        }
    else:
        output['96_05'] = "No risk"

    if result_0615:
        output['06_15'] = {
            'name': result_0615["name"],
            'data': json.loads(result_0615["description_json"])
        }
    else:
        output['06_15'] = "No risk"

    print(len(polys_9605))

    # ✅ Separate images for each dataset
    filtered_9605 = filter_polygons_near_point(polys_9605, latitude, longitude, max_km=100)
    filtered_0615 = filter_polygons_near_point(polys_0615, latitude, longitude, max_km=100)
    output['image_96_05'] = generate_fire_map(filtered_9605, latitude, longitude)
    output['image_06_15'] = generate_fire_map(filtered_0615, latitude, longitude)

    return output


