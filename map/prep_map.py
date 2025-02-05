def prep_map():
    # Read the contents of map-base.html
    with open('map/map-base.html', 'r', encoding='utf-8') as base_file:
        base_content = base_file.read()
    
    # Write the base content to index.html, effectively overwriting any existing content
    with open('index.html', 'w', encoding='utf-8') as map_file:
        map_file.write(base_content)

if __name__ == "__main__":
    prep_map() 