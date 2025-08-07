#known no risk
# lat = 41.27698190957095
# lon = 2.0510802904312824

# known 100y & 500y risk
# lat = 41.27270457818908
# lon = 2.0520473550222307

# known 500y only risk
# lat = 41.27374622035448
# lon = 2.0522067636329004
import requests
from pyproj import Transformer


def run(lat, lon):
    # return {'100': "MITECO service is offline or unavailable.", '500': "MITECO service is offline or unavailable."}
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(lon, lat)

    buffer = 76 / 2
    minx = x - buffer
    maxx = x + buffer
    miny = y - buffer
    maxy = y + buffer

    def build_featureinfo_url(layer, minx, miny, maxx, maxy):
        return (
            f"https://wmts.mapama.gob.es/sig/costas/{layer}/ows?"
            f"SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&FORMAT=image/png"
            "&TRANSPARENT=true"
            f"&LAYERS={layer}"
            f"&QUERY_LAYERS={layer}"
            "&TILED=true"
            "&scaleMethod=accurate"
            "&format_options=dpi:91"
            "&STYLES="
            "&WIDTH=256&HEIGHT=256"
            "&CRS=EPSG:3857"
            f"&BBOX={minx},{miny},{maxx},{maxy}"
            "&I=128&J=128"
            "&INFO_FORMAT=application/json"
        )

    def fetch_data(url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}:\n  {e}")
            return None

    url100 = build_featureinfo_url("zim_laminas_q100", minx, miny, maxx, maxy)
    url500 = build_featureinfo_url("zim_laminas_q500", minx, miny, maxx, maxy)

    data100 = fetch_data(url100)
    data500 = fetch_data(url500)

    output = {}

    if data100 and data100.get("features"):
        props = data100["features"][0]["properties"]
        output["100"] = {
            "cota_max": props.get("Cota máxima (m)"),
            "cota_media": props.get("Cota media (m)"),
            "area_km2": props.get("Área (km2)")
        }
    else:
        output["100"] = "Data not available or service error."

    if data500 and data500.get("features"):
        props = data500["features"][0]["properties"]
        output["500"] = {
            "cota_max": props.get("Cota máxima (m)"),
            "cota_media": props.get("Cota media (m)"),
            "area_km2": props.get("Área (km2)")
        }
    else:
        output["500"] = "Data not available or service error."

    return output

# output = run(41.27374622035448, 2.0522067636329004)
# print(output)