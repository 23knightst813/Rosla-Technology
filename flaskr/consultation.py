import requests
import math

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
    if not building_coords or len(building_coords) < 3:
        print("Not enough corners to make a shape!")
        return 0
    
    total_area = 0
    
    # We need the earth to be round for our math
    earth_radius = 6371000
    
    # Find the middle
    sum_lat = 0
    sum_lon = 0
    for point in building_coords:
        sum_lat = sum_lat + point[0]
        sum_lon = sum_lon + point[1]
    
    mid_lat = sum_lat / len(building_coords)
    
    # Convert to radians
    lat_to_meters = (math.pi / 180) * earth_radius
    lon_to_meters = (math.pi / 180) * earth_radius * math.cos(math.radians(mid_lat))
    
    # Loop around the shape and add up pieces
    for i in range(len(building_coords)):
        # Get current point and next point
        p1 = building_coords[i]
        p2 = building_coords[0] if i == len(building_coords)-1 else building_coords[i+1]
        
        # Convert to meters
        x1 = p1[1] * lon_to_meters
        y1 = p1[0] * lat_to_meters
        x2 = p2[1] * lon_to_meters
        y2 = p2[0] * lat_to_meters
        
        # Classic math formula for area of a polygon
        total_area = total_area + (x1*y2 - x2*y1)
    
    # Divide by 2
    area_sq_meters = abs(total_area) / 2
    
    # Make the number look nice with no decimals
    return round(area_sq_meters)

def house_direction():
    # Function not implemented, as it requires external data or specific API calls
    pass

if __name__ == "__main__":
    address = "10 Little Oak, Partridge Green, UK"
    api_key = "6e308214d092485198271dbc7b0d9d53"
    lat, lon = address_coordinates(address)
    print(f"Address geocoded to: {lat}, {lon}")

    if lat is not None and lon is not None:
        building_coords = get_building_geometry(lat, lon, api_key)
        if building_coords:
            print(f"Building coordinates: {building_coords}")
            
            # Calculate building area
            area = calculate_area(building_coords)
            print(f"Building area: {area} square meters")
            
            # Calculate the building orientation
            orientation = calculate_orientation(building_coords)
            print(f"Building orientation: {orientation}")
        else:
            print("Failed to get building geometry")
    else:
        print("Failed to geocode address")
