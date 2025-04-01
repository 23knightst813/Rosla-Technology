import requests
import math

def get_coordinates(address, api_key):
    base_url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        'text': address,
        'apiKey': api_key
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    if data['features']:
        location = data['features'][0]['geometry']['coordinates']
        return location[1], location[0]  # latitude, longitude
    else:
        raise ValueError("Address not found.")

def get_building_geometry(lat, lon, api_key):
    base_url = "https://api.geoapify.com/v2/place-details"
    params = {
        'lat': lat,
        'lon': lon,
        'features': 'building',
        'apiKey': api_key
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

def calculate_area(building_coords):
    """Calculates the area of a building using the Shoelace theorem."""
    if len(building_coords) < 3:
        raise ValueError("At least three coordinates are needed to calculate area.")
    
    # Convert lat/lon to meters using the Earth’s radius
    earth_radius = 6378137  # in meters
    
    def to_cartesian(lat, lon):
        """Converts lat/lon to Cartesian coordinates."""
        x = math.radians(lon) * earth_radius * math.cos(math.radians(lat))
        y = math.radians(lat) * earth_radius
        return x, y

    # Convert all lat/lon points to Cartesian coordinates
    cartesian_coords = [to_cartesian(lat, lon) for lon, lat in building_coords]

    # Apply the Shoelace theorem to find the polygon area
    n = len(cartesian_coords)
    area = 0
    for i in range(n):
        x1, y1 = cartesian_coords[i]
        x2, y2 = cartesian_coords[(i + 1) % n]  # Next vertex (wrapping around)
        area += x1 * y2 - x2 * y1

    return abs(area) / 2  # Final absolute area

if __name__ == "__main__":
    address = "10 Little Oak, Partridge Green, UK"
    api_key = "6e308214d092485198271dbc7b0d9d53"
    try:
        lat, lon = get_coordinates(address, api_key)
        print(f"Coordinates: Latitude {lat}, Longitude {lon}")
        
        building_coords = get_building_geometry(lat, lon, api_key)
        if not building_coords:
            raise ValueError("No valid building coordinates found.")

        orientation = calculate_orientation(building_coords)
        print(f"The building at '{address}' is oriented towards: {orientation}")
        
        area = calculate_area(building_coords)
        print(f"Approximate building area: {round(area, 2)} square meters")

    except Exception as e:
        print(f"Error: {e}")
