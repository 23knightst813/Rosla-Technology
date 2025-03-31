import requests

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
        # Extract latitude and longitude from the first result
        latitude = data[0].get('lat')
        longitude = data[0].get('lon')
        return latitude, longitude
    else:
        return None, None

def fetch_raw_building_data(lat, lon):
    # Construct Overpass API query to find buildings around the coordinates
        query = f"""
        [out:json];
        (
          way["building"](around:20, {lat}, {lon});
          relation["building"](around:20, {lat}, {lon});
        );
        out body;
        >;
        out skel qt;
        """
        
        url = "https://overpass-api.de/api/interpreter"
        response = requests.post(url, data={'data': query})
        response.raise_for_status()
        
        return response.json()

def get_building_cords(building_data):
    # Get all the elements from the data
    all_elements = building_data.get('elements', [])
    
    # Make a dictionary of nodes
    nodes = {}
    for element in all_elements:
        if element['type'] == 'node':
            nodes[element['id']] = element
    
    # Find buildings in the data
    buildings = []
    for element in all_elements:
        if element['type'] == 'way':
            if 'tags' in element:
                if 'building' in element['tags']:
                    buildings.append(element)
    
    # Check if we found any buildings
    if len(buildings) == 0:
        print("Error: No buildings found!")
        return None
    
    # Use the first building we found
    building = buildings[0]
    
    # Get the coordinates of the building
    building_coords = []
    for node_id in building['nodes']:
        if node_id in nodes:
            node = nodes[node_id]
            lon = node['lon']
            lat = node['lat']
            coords = (lon, lat)
            building_coords.append(coords)

    return building_coords


if __name__ == "__main__":
    address = "10 Downing Street, London, UK"
    lat, lon = address_coordinates(address)

    raw_data = fetch_raw_building_data(lat, lon)

    building_coords = get_building_cords(raw_data)

    print(f"Coordinates of the building: {building_coords}")