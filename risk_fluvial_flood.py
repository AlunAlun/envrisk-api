import requests
from pyproj import Transformer


def run(lat, lon):
    # return("MITECO service is offline or unavailable.")
    # Step 2: Convert to EPSG:3857 (Web Mercator)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(lon, lat)

    # Step 3: Create bounding box around the point (256x256 tile, 128m buffer)
    buffer = 128  # meters
    minx = x - buffer
    maxx = x + buffer
    miny = y - buffer
    maxy = y + buffer

    # Step 4: Set pixel location (center of tile)
    i = 128
    j = 128

    layers = ["NZ.Flood.FluvialT10", "NZ.Flood.FluvialT100", "NZ.Flood.FluvialT500"]
    results = []
    wasError = False
    print()

    for n in range(3):
        # Step 5: Construct WMS GetFeatureInfo request
        url = "https://servicios.idee.es/wms-inspire/riesgos-naturales/inundaciones"
        params = {
            "SERVICE": "WMS",
            "VERSION": "1.3.0",
            "REQUEST": "GetFeatureInfo",
            "LAYERS": layers[n],
            "QUERY_LAYERS": layers[n],
            "CRS": "EPSG:3857",
            "BBOX": f"{minx},{miny},{maxx},{maxy}",
            "WIDTH": "256",
            "HEIGHT": "256",
            "I": str(i),
            "J": str(j),
            "INFO_FORMAT": "text/plain"
        }

        # Step 6: Make the request
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                text = response.text
                val = float(text.split("GRAY_INDEX =")[1].split('\n')[0].strip())
                if val > -1e+38:
                    results.append(val)
                    # print(f"Reading: {val}")
                else:
                    results.append(0)
                    # print(f"Reading: 0")
        except Exception as e:
            wasError = True
            print(f"Error at offset {n}:", e)

    # Step 7: Print results
    if wasError == False:
        risks = {'10': results[0], '100': results[1], '500': results[2]}
        # print()
        # print("Risks")
        # print("-----")
        # print(f"10 year {risks['10']}")
        # print(f"100 year {risks['100']}")
        # print(f"500 year {risks['500']}")
        # print()
        output = risks
        print("Fluvial risks successfully returned")
        return output
    else:
        print("There was an error fetching the data")
        return("MITECO service is offline or unavailable.")

# output = run(41.283645999461406, 2.064729668547003)
# print(output)