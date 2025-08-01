import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# === 1. Load shapefile ===
shapefile_path = "pand-p-shp/pand_p.shp"  # Adjust if running locally
gdf = gpd.read_file(shapefile_path)

shapefile_path2 = "pand-p-shp/pand_c.shp"  # Adjust if running locally
gdf2 = gpd.read_file(shapefile_path2)

# === 2. Reproject to EPSG:4326 if needed ===
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")
if gdf2.crs != "EPSG:4326":
    gdf2 = gdf2.to_crs("EPSG:4326")

# === 3. Risk code mapping ===
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

# === 4. Main function ===
def get_desertification_risk(lat, lon, GDF):
    point = Point(lon, lat)  # Note: (lon, lat) order
    match = GDF[GDF.contains(point)]

    if match.empty:
        return "No Data"
    
    risk_code = int(match.iloc[0]["DESER_CLA"])
    return RISK_LABELS.get(risk_code, f"Unknown code: {risk_code}")

def plot_full_dataset_with_point(GDF, lat, lon, filename=None):
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from shapely.geometry import Point

    point = Point(lon, lat)

    fig, ax = plt.subplots(figsize=(14, 12))

    # Plot polygons by desertification class
    legend_patches = []
    for code, label in RISK_LABELS.items():
        subset = GDF[GDF["DESER_CLA"] == code]
        color = RISK_COLORS.get(code, "black")
        subset.plot(ax=ax, color=color, alpha=0.7, edgecolor="k", linewidth=0.2)
        patch = mpatches.Patch(color=color, label=f"{label} ({code})")
        legend_patches.append(patch)

    # Plot the query point as a thick black X
    ax.scatter(
        lon, lat,
        color="black",
        marker="x",
        s=200,         # size
        linewidths=2,  # thickness of the X
        label="Queried Point (X)"
    )

    # Add point to legend
    legend_patches.append(mpatches.Patch(color="black", label="Queried Point (X)"))

    # Style legend outside plot
    ax.set_title("Desertification Risk Map (PAND) with Query Location", fontsize=14)
    ax.axis('off')
    ax.legend(
        handles=legend_patches,
        title="Risk Categories",
        loc="center left",
        bbox_to_anchor=(1.0, 0.5)
    )

    plt.tight_layout()
    # Save if filename provided
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        print(f"Plot saved to {filename}")

    # plt.show()



# === 5. Example usage ===
def run(latitude, longitude):
    # High risk
    # latitude = 37.216683162769684
    # longitude = -7.316882654272187
    # medium risk
    # latitude = 37.272084560683986
    # longitude = -7.115860474641874
    #canarias
    # latitude = 28.391352258611125
    # longitude =  -13.99126909512573
    # asturias
    # latitude = 42.97697120364747
    # longitude = -5.850930512651173
    # outside
    # latitude = 31.144015780847376
    # longitude = -11.430494039736288

    risk = get_desertification_risk(latitude, longitude, gdf)
    fName = f"desertification_at_{latitude}_{longitude}.png"
    if risk != "No Data":
        print(f"Desertification risk at ({latitude}, {longitude}): {risk}")
        # plot_full_dataset_with_point(gdf, latitude, longitude, fName)
    else:
        print("trying canarias...")
        risk = get_desertification_risk(latitude, longitude, gdf2)
        print(f"Desertification risk at ({latitude}, {longitude}): {risk}")
        # if risk != "No Data":
            # plot_full_dataset_with_point(gdf2, latitude, longitude, fName)
    output = {'risk': risk, 'filename': fName}
    return output

# output = run(37.216683162769684, -7.316882654272187)
# print(output)
    

