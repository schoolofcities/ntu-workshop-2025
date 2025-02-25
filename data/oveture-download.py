import geopandas as gpd
import json
import os
import subprocess

path = ""
input_region_polygon = "taipei-metro-area.geojson"

# overturemaps download --help # to see options


# get bounding box to download for

def get_bbox_from_geojson(file_path):
	bounds_extension = 0.08 # go beyond the exact bounding box, for some overflow of data
	gdf = gpd.read_file(file_path)
	minx, miny, maxx, maxy = gdf.total_bounds  # Get bounding box [min_lon, min_lat, max_lon, max_lat]
	return [minx - bounds_extension, miny - bounds_extension, maxx + bounds_extension,  maxy + bounds_extension]

bbox = get_bbox_from_geojson(input_region_polygon)

bbox_str = ",".join(map(str, bbox))

print(bbox_str)


# function for extracting data within dictionary columns

def extract(val, key):
    if isinstance(val, dict):  # If it's already a dictionary
        return val.get(key, None)
    elif isinstance(val, str):  # If it's a string, try converting
        try:
            data = json.loads(val)  # Use json.loads instead of ast.literal_eval
            if isinstance(data, dict):
                return data.get(key, None) if isinstance(data, dict) else None
            elif isinstance(data, list):
                return data[0].get(key, None) if isinstance(data, list) else None
            else:
                return None
        except (json.JSONDecodeError, TypeError):
            return None  # If parsing fails, return None
    return None



# water download

# command = [
#     "overturemaps", "download",
#     "--bbox", bbox_str,
#     "-f", "geojson",
#     "--type", "water",
#     "-o", path + "overture-water" + ".geojson"
# ]

# subprocess.run(command, check=True)

# gdf = gpd.read_file(path + "overture-water" + ".geojson")

# gdf = gdf[["subtype", "class", "geometry"]]

# gdf.to_file(path + "overture-water" + ".gpkg", driver="GPKG")

# os.remove(path + "overture-water" + ".geojson")




# transport segment download

command = [
    "overturemaps", "download",
    "--bbox", bbox_str,
    "-f", "geojson",
    "--type", "segment",
    "-o", path + "overture-transport" + ".geojson"
]

subprocess.run(command, check=True)

gdf = gpd.read_file(path + "overture-transport" + ".geojson")

gdf = gdf[["subtype", "class", "geometry"]]

gdf.to_file(path + "overture-transport" + ".gpkg", driver="GPKG")

os.remove(path + "overture-transport" + ".geojson")





# places download

command = [
    "overturemaps", "download",
    "--bbox", bbox_str,
    "-f", "geojson",
    "--type", "place",
    "-o", path + "overture-places" + ".geojson"
]

subprocess.run(command, check=True)

gdf = gpd.read_file(path + "overture-places" + ".geojson")

gdf['name'] = gdf['names'].apply(lambda x: extract(x, "primary"))

gdf['category'] = gdf['categories'].apply(lambda x: extract(x, "primary"))

gdf['source'] = gdf['sources'].apply(lambda x: extract(x, "dataset"))

gdf = gdf[["name", "category", "source", "geometry"]]

gdf.to_file(path + "overture-places" + ".gpkg", driver="GPKG")

os.remove(path + "overture-places" + ".geojson")



# land cover download

command = [
    "overturemaps", "download",
    "--bbox", bbox_str,
    "-f", "geojson",
    "--type", "land_cover",
    "-o", path + "overture-landcover" + ".geojson"
]

subprocess.run(command, check=True)

gdf = gpd.read_file(path + "overture-landcover" + ".geojson")

gdf['min_zoom'] = gdf['cartography'].apply(lambda x: extract(x, "min_zoom"))

gdf = gdf[gdf["min_zoom"] > 0]

gdf['max_zoom'] = gdf['cartography'].apply(lambda x: extract(x, "max_zoom"))

gdf['sort_key'] = gdf['cartography'].apply(lambda x: extract(x, "sort_key"))

gdf = gdf[["subtype", "min_zoom", "max_zoom", "sort_key", "geometry"]]

gdf.to_file(path + "overture-landcover" + ".gpkg", driver="GPKG")

os.remove(path + "overture-landcover" + ".geojson")
