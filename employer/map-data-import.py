import xml.etree.ElementTree as ET
import folium
import json

# Parse the KML file
tree = ET.parse('denver.kml')
root = tree.getroot()

# Define the KML namespace
namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

# Create a map centered around Denver
map_center = [39.7392, -104.9903]  # Denver coordinates
m = folium.Map(location=map_center, zoom_start=10)

# Extract points of interest
for placemark in root.findall('.//kml:Placemark', namespace):
    name = placemark.find('kml:name', namespace).text
    coordinates = placemark.find('.//kml:coordinates', namespace).text.strip()
    lon, lat, _ = map(float, coordinates.split(','))  # Extract longitude and latitude

    # Add marker to the map
    folium.Marker(location=[lat, lon], popup=name).add_to(m)

# Save the map to an HTML file
m.save('index.html')

# Load both files
with open('employer/source/coordinates-facilities.json', 'r') as f:
    coordinates = json.load(f)

with open('employer/source/facilities-colorado.json', 'r') as f:
    facilities = json.load(f)

# Create lookup dictionary from coordinates data
coord_lookup = {}
for facility in coordinates:
    name = facility[0]
    lat = facility[1]
    lng = facility[2]
    id = facility[3]
    coord_lookup[id] = {
        'latitude': lat,
        'longitude': lng
    }

# Add coordinates to facilities data
for facility in facilities:
    facility_id = facility['id']
    if facility_id in coord_lookup:
        facility['latitude'] = coord_lookup[facility_id]['latitude']
        facility['longitude'] = coord_lookup[facility_id]['longitude']
    else:
        facility['latitude'] = ""
        facility['longitude'] = ""

# Write updated facilities data
with open('employer/source/facilities-colorado.json', 'w') as f:
    json.dump(facilities, f, indent=2)