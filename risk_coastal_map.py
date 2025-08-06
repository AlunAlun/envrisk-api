import math
from pyproj import Transformer

def get_tile_urls(lat, lon, zoom=18):
    TILE_SIZE = 256
    LAYERS = {
        "100": "zim_laminas_q100",
        "500": "zim_laminas_q500"
    }
    
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(lon, lat)

    # Convert to tile numbers
    initial_resolution = 2 * math.pi * 6378137 / TILE_SIZE
    origin_shift = 2 * math.pi * 6378137 / 2.0
    resolution = initial_resolution / (2**zoom)
    
    tx = int((x + origin_shift) / (TILE_SIZE * resolution))
    ty = int((origin_shift - y) / (TILE_SIZE * resolution))

    urls = {
        "100": [],
        "500": []
    }

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            tile_x = tx + dx
            tile_y = ty + dy

            minx = tile_x * TILE_SIZE * resolution - origin_shift
            maxx = (tile_x + 1) * TILE_SIZE * resolution - origin_shift
            miny = origin_shift - (tile_y + 1) * TILE_SIZE * resolution
            maxy = origin_shift - tile_y * TILE_SIZE * resolution

            bbox = f"{minx},{miny},{maxx},{maxy}"

            for key, layer in LAYERS.items():
                url = (
                    f"https://wmts.mapama.gob.es/sig/costas/{layer}/ows?"
                    f"SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap"
                    f"&FORMAT=image/png"
                    f"&TRANSPARENT=true"
                    f"&LAYERS={layer}"
                    f"&STYLES="
                    f"&WIDTH={TILE_SIZE}&HEIGHT={TILE_SIZE}"
                    f"&CRS=EPSG:3857"
                    f"&BBOX={bbox}"
                )
                urls[key].append(url)

    return urls

lat = 41.27270457818908
lon = 2.0520473550222307

tile_urls = get_tile_urls(lat, lon)

# Print sample
for layer, urls in tile_urls.items():
    print(f"\nLayer {layer} year flood risk tiles:")
    for url in urls:
        print(url)