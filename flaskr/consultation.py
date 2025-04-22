from flask import flash  # Import flash from Flask
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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def address_coordinates(address):
    try:
        # Use Geoapify API for geocoding
        base_url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            'text': address,
            'apiKey': os.getenv('GEOAPIFY_API_KEY')
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()

        if data.get('features'):
            # Extract latitude and longitude from the first result
            latitude = data['features'][0]['geometry']['coordinates'][1]
            longitude = data['features'][0]['geometry']['coordinates'][0]
            return latitude, longitude
        else:
            flash("No location found for this address", "error")
            return None, None
    except Exception as e:
        flash(f"Error fetching address coordinates: {str(e)}", "danger")
        logger.error(f"Error fetching address coordinates: {str(e)}")
        return None, None

def get_building_geometry(lat, lon):
    try:
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
        flash("Building geometry not found.", "error")
        raise ValueError("Building geometry not found.")
    except Exception as e:
        flash(f"Error fetching building geometry: {str(e)}", "danger")
        logger.error(f"Error fetching building geometry: {str(e)}")
        raise

def calculate_orientation(building_coords):
    try:
        if len(building_coords) < 2:
            flash("Insufficient coordinates to determine orientation.", "error")
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
    except Exception as e:
        flash(f"Error calculating orientation: {str(e)}", "danger")
        logger.error(f"Error calculating orientation: {str(e)}")
        raise

def calculate_area_shapely(building_coords):
    try:
        if not building_coords or len(building_coords) < 3:
            flash("Invalid building coordinates for area calculation.", "error")
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
    except Exception as e:
        flash(f"Error calculating area: {str(e)}", "danger")
        logger.error(f"Error calculating area: {str(e)}")
        return 0

def solar_potential(adress):
    try:
        solar_efficiency = {
            "South": 1.00,
            "South-East": 0.92,  
            "South-West": 0.90,  
            "East": 0.80,       
            "West": 0.78,        
            "North-East": 0.65, 
            "North-West": 0.60,  
            "North": 0.50
        }

        lat, lon = address_coordinates(adress)

        if lat is not None and lon is not None:
            building_coords = get_building_geometry(lat, lon)
            area = calculate_area_shapely(building_coords)
            orientation = calculate_orientation(building_coords)

            usable_area = area * 0.6
            energy_potential = usable_area * 1000 * 0.18 * solar_efficiency[orientation]

            pannel_count = ( usable_area / 1.7 ) / 2
            pannel_count = round(pannel_count, 2)

            price_estimate = pannel_count * 300

            # Calculate the monthly payment for a 10-year loan at 5% interest
            monthly_payment = (price_estimate * 0.0041666666666667 * (1 + 0.0041666666666667) ** 120) / ((1 + 0.0041666666666667) ** 120 - 1)

            energy_savings = energy_potential * 27.03 / 1000  # Convert kWh to GBP (assuming 27.03 pence per kWh)

            logger.info(f"Building area: {area} m²")
            logger.info(f"Building orientation: {orientation}")
            logger.info(f"Useable space: {usable_area} m²")
            logger.info(f"Energy potential: {energy_potential} kWh/year")
            logger.info(f"Number of panels: {pannel_count}")
            logger.info(f"Price estimate: {price_estimate} GBP")
            logger.info(f"Yearly payment: {monthly_payment*12} GBP")
            logger.info(f"Energy savings: {energy_savings} GBP/year")

            flash("Solar potential calculation completed successfully.", "success")
            return (
                round(area, 2), 
                orientation, 
                round(usable_area, 2), 
                round(energy_potential, 2), 
                round(pannel_count, 2), 
                round(price_estimate, 2), 
                round(monthly_payment, 2), 
                round(energy_savings, 2)
            )
        else:
            flash("Failed to calculate solar potential due to missing coordinates.", "error")
            return None
    except Exception as e:
        flash(f"Error calculating solar potential: {str(e)}", "danger")
        logger.error(f"Error calculating solar potential: {str(e)}")
        return None
