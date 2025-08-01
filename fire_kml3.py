import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, Point
from zipfile import ZipFile
from io import BytesIO
import re
from html import unescape
import json
from bs4 import BeautifulSoup

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

    for polygon in placemark_elem.findall(".//kml:Polygon", ns):
        outer = polygon.find(".//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
        if outer is not None:
            outer_coords = parse_coordinates(outer.text)
            inner_rings = polygon.findall(".//kml:innerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
            holes = [parse_coordinates(inner.text) for inner in inner_rings]
            try:
                poly = Polygon(outer_coords, holes)
                if poly.is_valid:
                    polygons.append(poly)
            except Exception as e:
                print("⚠️ Error creating polygon:", e)
    return polygons

def description_table_to_json(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    data = {}

    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            key = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            data[key] = value

    return data

def find_placemark_from_kmz(lat, lon, kmz_path):
    point = Point(lon, lat)
    kml_text = load_kml_content(kmz_path)
    root = ET.fromstring(kml_text)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    placemarks = root.findall(".//kml:Placemark", ns)

    for placemark in placemarks:
        name = placemark.find("kml:name", ns)
        description = placemark.find("kml:description", ns)
        name_text = name.text.strip() if name is not None else "(Unnamed)"
        desc_text = description.text.strip() if description is not None else ""

        polygons = extract_polygons(placemark)
        for poly in polygons:
            if poly.contains(point):
                return {
                    "name": name_text,
                    "description_json": description_table_to_json(desc_text)
                }
    return None

# === Example usage ===
def run(latitude, longitude):
    output = {}
    FILE_2006_2015 = "frecuenciadeincendiosperiodo2006a2015_tcm30-525840.kmz"
    FILE_1996_2005 = "frecuenciadeincendiosperiodo1996a2005_tcm30-199965.kmz"

    result = find_placemark_from_kmz(latitude, longitude, FILE_1996_2005)
    
    if result:
        output['96_05'] = {'name':result["name"], 'data': json.dumps(result["description_json"], indent=2, ensure_ascii=False)}
        print()
        print("1996 to 2005:")
        print("✅ Point is inside placemark:")
        print("📍 Name:", result["name"])
        print("📦 Description as JSON:")
        print(json.dumps(result["description_json"], indent=2, ensure_ascii=False))
    else:
        print("❌ No matching placemark found.")

    result = find_placemark_from_kmz(latitude, longitude, FILE_2006_2015)
    if result:
        output['06_15'] = {'name':result["name"], 'data': json.dumps(result["description_json"], indent=2, ensure_ascii=False)}
        print()
        print("2006 to 2015:")
        print("✅ Point is inside placemark:")
        print("📍 Name:", result["name"])
        print("📦 Description as JSON:")
        print(json.dumps(result["description_json"], indent=2, ensure_ascii=False))
        return output
    else:
        print("❌ No matching placemark found.")
        return("No match")

# output = run(43.18021446088912, -6.542169479579782)
# print(output)