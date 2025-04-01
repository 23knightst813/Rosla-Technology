import requests
import math
import dotenv
import os
from shapely.geometry import Polygon
from shapely.ops import transform
import geopandas as gpd
from pyproj import CRS
# Load environment variables from .env file
dotenv.load_dotenv()



def address_coordinates(address):
    # Use Nominatim for geocoding (OpenStreetMap's geocoding service)
    encoded_address = requests.utils.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_address}&limit=1"
    
    headers = {
        'User-Agent': 'BuildingAreaCalculator/1.0'  # Nominatim requires a User-Agent
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise exception for HTTP errors
    
    data = response.json()

    if data:
        # Extract latitude and longitude from the first result and convert to float
        latitude = float(data[0].get('lat'))
        longitude = float(data[0].get('lon'))
        return latitude, longitude
    else:
        print("No location found for this address")
        return None, None

def get_building_geometry(lat, lon):
    base_url = "https://api.geoapify.com/v2/place-details"
    params = {
        'lat': lat,
        'lon': lon,
        'features': 'building',
        'apiKey': os.getenv('GEOAPIFY_API_KEY')
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    for feature in data.get('features', []):
        if feature.get('properties', {}).get('feature_type') == 'building':
            return feature['geometry']['coordinates'][0]  # List of [lon, lat] pairs
    raise ValueError("Building geometry not found.")

def calculate_orientation(building_coords):
    if len(building_coords) < 2:
        raise ValueError("Insufficient coordinates to determine orientation.")
    start = building_coords[0]
    end = building_coords[1]
    delta_lon = end[0] - start[0]
    delta_lat = end[1] - start[1]
    angle_rad = math.atan2(delta_lat, delta_lon)
    angle_deg = math.degrees(angle_rad)
    compass_brackets = ["East", "North-East", "North", "North-West", "West", "South-West", "South", "South-East", "East"]
    compass_index = round(angle_deg / 45) % 8
    return compass_brackets[compass_index]


def calculate_area_shapely(building_coords):
    if not building_coords or len(building_coords) < 3:
        return 0

    # Create a Shapely Polygon
    polygon_geom = Polygon(building_coords)
    
    # Create a GeoDataFrame with the polygon
    gdf = gpd.GeoDataFrame(geometry=[polygon_geom], crs=CRS.from_epsg(4326))
    
    # Auto-project to UTM zone appropriate for the polygon's location
    gdf_projected = gdf.to_crs(gdf.estimate_utm_crs())
    
    # Calculate area
    area_sq_meters = gdf_projected.geometry[0].area
    return round(area_sq_meters)

if __name__ == "__main__":
    address = "10 Little Oak, Partridge Green, UK"
    lat, lon = address_coordinates(address)
    print(f"Address geocoded to: {lat}, {lon}")

    if lat is not None and lon is not None:
        building_coords = get_building_geometry(lat, lon)
        if building_coords:
            print(f"Building coordinates: {building_coords}")
            
            # Calculate building area using Shapely simplified
            area_shapely_simplified = calculate_area_shapely(building_coords)
            print(f"Building area (Shapely simplified): {area_shapely_simplified} square meters")
            
            # Calculate the building orientation
            orientation = calculate_orientation(building_coords)
            print(f"Building orientation: {orientation}")
        else:
            print("Failed to get building geometry")
    else:
        print("Failed to geocode address")
