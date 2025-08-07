import zipfile
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, mapping
from shapely.validation import explain_validity
from bs4 import BeautifulSoup
from html import unescape
import json

def parse_coordinates(coord_text):
    coords = []
    for line in coord_text.strip().split():
        parts = line.split(",")
        if len(parts) >= 2:
            lon, lat = float(parts[0]), float(parts[1])
            coords.append((lon, lat))
    return coords

def extract_description_data(description_html):
    """
    Parses the HTML in a KML <description> field and extracts structured fire risk info.
    Returns a dictionary of values.
    """
    soup = BeautifulSoup(unescape(description_html), "html.parser")
    result = {}

    try:
        inner_table = soup.find("table").find("table")  # Get the nested table
        for row in inner_table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            key = cells[0].get_text(strip=True).strip(":")
            value = cells[1].get_text(strip=True)
            result[key] = value
    except Exception as e:
        print(f"⚠️ Error parsing description: {e}")
    return result

def extract_polygons(placemark_elem):
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    polygons = []

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
            if not poly.is_valid:
                poly = poly.buffer(0)  # Attempt repair
            if poly.is_valid:
                polygons.append(poly)
            else:
                print(f"⚠️ Invalid polygon after repair: {explain_validity(poly)}")
        except Exception as e:
            print(f"⚠️ Error creating polygon {idx}: {e}")
    return polygons

def kmz_to_geojson(kmz_path, output_path):
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    features = []

    with zipfile.ZipFile(kmz_path, 'r') as z:
        kml_filename = next((f for f in z.namelist() if f.endswith('.kml')), None)
        if not kml_filename:
            raise ValueError("No .kml file found in KMZ")

        with z.open(kml_filename) as f:
            tree = ET.parse(f)
            root = tree.getroot()

            for placemark in root.findall(".//kml:Placemark", ns):
                polygons = extract_polygons(placemark)
                desc_elem = placemark.find("kml:description", ns)
                props = extract_description_data(desc_elem.text) if desc_elem is not None else {}

                for poly in polygons:
                    features.append({
                        "type": "Feature",
                        "geometry": mapping(poly),
                        "properties": props
                    })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported GeoJSON to {output_path} with {len(features)} features.")


if __name__ == "__main__":
    # === Adjust paths as needed
    kmz_to_geojson(
        "data/frecuenciadeincendiosperiodo1996a2005_tcm30-199965.kmz",
        "data/fire_1996_2005.geojson"
    )
    kmz_to_geojson(
        "data/frecuenciadeincendiosperiodo2006a2015_tcm30-525840.kmz",
        "data/fire_2006_2015.geojson"
    )
