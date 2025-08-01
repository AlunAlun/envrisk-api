import requests
from pyproj import Transformer

# Step 1: Input coordinates in EPSG:4326

#known no risk
# lat = 41.27698190957095
# lon = 2.0510802904312824

# known 100y & 500y risk
# lat = 41.27270457818908
# lon = 2.0520473550222307

# known 500y only risk
# lat = 41.27374622035448
# lon = 2.0522067636329004

def run(lat, lon):

    # Step 2: Convert to EPSG:3857
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(lon, lat)

    # Step 3: Build GetFeatureInfo WMS query
    buffer = 76 / 2  # Tile covers 76x76m with 256px → ≈ 0.3m/px
    minx = x - buffer
    maxx = x + buffer
    miny = y - buffer
    maxy = y + buffer

    url100 = (
        "https://wmts.mapama.gob.es/sig/costas/zim_laminas_q100/ows?"
        f"SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&FORMAT=image/png"
        "&TRANSPARENT=true"
        "&LAYERS=zim_laminas_q100"
        "&QUERY_LAYERS=zim_laminas_q100"
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

    # Step 4: Make the request and process the response
    response100 = requests.get(url100)
    data100 = response100.json()

    url500 = (
        "https://wmts.mapama.gob.es/sig/costas/zim_laminas_q500/ows?"
        f"SERVICE=WMS&VERSION=1.3.0&REQUEST=GetFeatureInfo&FORMAT=image/png"
        "&TRANSPARENT=true"
        "&LAYERS=zim_laminas_q500"
        "&QUERY_LAYERS=zim_laminas_q500"
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

    # Step 4: Make the request and process the response
    response500 = requests.get(url500)
    data500 = response500.json()
    output = {}

    # Step 5: Extract and print relevant properties
    if data100["features"]:
        props = data100["features"][0]["properties"]
        cota_max = props.get("Cota máxima (m)")
        cota_media = props.get("Cota media (m)")
        area_km2 = props.get("Área (km2)")

        output['100'] = {'cota_max': cota_max, 'cota_media': cota_media, 'area_km2': area_km2}
        print("100y Flood risk data:")
        print(f"  Cota máxima (m): {cota_max}")
        print(f"  Cota media (m):  {cota_media}")
        print(f"  Área (km²):      {area_km2}")
    else:
        output['100'] = "None"
        print("No 100 year flood risk found at this location.")

    if data500["features"]:
        props = data500["features"][0]["properties"]
        cota_max = props.get("Cota máxima (m)")
        cota_media = props.get("Cota media (m)")
        area_km2 = props.get("Área (km2)")
        output['500'] = {'cota_max': cota_max, 'cota_media': cota_media, 'area_km2': area_km2}

        print("500y Flood risk data:")
        print(f"  Cota máxima (m): {cota_max}")
        print(f"  Cota media (m):  {cota_media}")
        print(f"  Área (km²):      {area_km2}")
    else:
        output['500'] = "None"
        print("No 500 year flood risk found at this location.")

    return output

# output = run(41.27374622035448, 2.0522067636329004)
# print(output)