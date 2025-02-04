import xml.etree.ElementTree as ET
import folium

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
m.save('map.html')