import csv
import json
import os
import glob

def create_house_markers():
    sale_markers = []
    rental_markers = []
    sale_layer_group = []
    rental_layer_group = []
    
    # Get all CSV files in the home directory
    csv_files = glob.glob('home/*.csv')
    
    for csv_file in csv_files:
        is_rental = '-Rent.csv' in csv_file
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip rows with missing data
                if not all([row['latitude'], row['longitude'], row['list_price'], row['property_url']]):
                    continue
                    
                lat = float(row['latitude'])
                lng = float(row['longitude'])
                price = int(float(row['list_price']))
                url = row['property_url']
                
                # Apply different price filters for rentals vs sales
                if is_rental:
                    if not (1000 <= price <= 3000):
                        continue
                else:  # Sale properties
                    if not (450000 <= price <= 500000):
                        continue
                
                # Format price - add '/mo' for rentals
                price_text = f"${price}/mo" if is_rental else f"${round(price/1000)}K"
                
                # Use different icons for rentals vs sales
                icon = 'rentalBuilding' if is_rental else 'houseBuilding'
                
                marker_var = f"marker_{abs(hash(f'{lat}{lng}'))}"
                
                # Create popup with hyperlinked price, using escaped quotes
                popup_content = f"<a href=\\'{url}\\' target=\\'_blank\\'>{price_text}</a>"
                marker = f"var {marker_var} = L.marker([{lat}, {lng}], {{icon: {icon}}}).bindPopup('{popup_content}');"
                
                # Add to appropriate lists
                if is_rental:
                    rental_markers.append(marker)
                    rental_layer_group.append(marker_var)
                else:
                    sale_markers.append(marker)
                    sale_layer_group.append(marker_var)
    
    # Write the markers and layer group to index.html
    with open('index.html', 'r') as file:
        content = file.read()
    
    # Find the position to insert markers (before the hospitals layer group)
    insert_pos = content.find('var hospitals = L.layerGroup([')
    
    # Create the markers text blocks
    markers_text = '\n\t' + '\n\t'.join(sale_markers + rental_markers) + '\n\n'
    
    # Create separate layer groups for houses and rentals
    houses_group = f'\tvar houses = L.layerGroup([{", ".join(sale_layer_group)}]);\n'
    rentals_group = f'\tvar rentals = L.layerGroup([{", ".join(rental_layer_group)}]);\n\n'
    
    # Insert the new code
    new_content = (
        content[:insert_pos] + 
        markers_text +
        houses_group +
        rentals_group +
        content[insert_pos:]
    )
    
    # Add both groups to overlayMaps
    new_content = new_content.replace(
        '"Care Facilities": hospitals,',
        '"Care Facilities": hospitals,\n\t\t"Houses": houses,\n\t\t"Rentals": rentals,'
    )
    
    with open('index.html', 'w') as file:
        file.write(new_content)

if __name__ == '__main__':
    create_house_markers() 