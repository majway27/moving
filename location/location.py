import json
from pathlib import Path
import re
import hashlib
from typing import Dict, List, Tuple

# State abbreviation to full name mapping
STATE_MAPPING = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

def load_locations() -> List[Dict]:
    """Load and parse the location.json file"""
    location_path = Path(__file__).parent / "location.json"
    with open(location_path) as f:
        data = json.load(f)
    return data["metro_areas"]

def format_location(city, state):
    """Format city and state into search string"""
    return f"{city}, {state}"

def get_state_from_location(location: str) -> str:
    """Extract and normalize state from location string.
    
    Args:
        location: Location string (e.g. "Denver, CO")
        
    Returns:
        Full state name (e.g. "Colorado") or original location if state not found
    """
    if not location or ',' not in location:
        return location
        
    state_abbrev = location.split(',')[-1].strip().upper()
    return STATE_MAPPING.get(state_abbrev, location)

class BuildingMarker:
    def __init__(self, lat: float, lon: float, popup: str, icon_type: str):
        self.lat = lat
        self.lon = lon
        self.popup = popup
        self.icon_type = icon_type

def generate_id(data: Dict) -> str:
    """Generate a stable ID from residence/job data"""
    # Create a string of key identifying data
    if 'url' in data:
        id_string = data['url']  # Use URL as unique identifier if available
    else:
        # Otherwise combine location and price
        id_string = f"{data.get('latitude','')}{data.get('longitude','')}{data.get('price','')}"
    
    # Create a hash of the string
    return hashlib.md5(id_string.encode()).hexdigest()[:12]

def generate_map(
    city: str,
    template_path: Path,
    output_path: Path,
    residences: List[Dict],
    facilities: List[Dict],
    jobs: List[Dict]
) -> None:
    """
    Generate an interactive map for a city using the provided data.
    
    Args:
        city: Name of the city
        template_path: Path to the template HTML file
        output_path: Path to write the output HTML file
        residences: List of residence data
        facilities: List of healthcare facility data
        jobs: List of job posting data
    """
    # Read template
    with open(template_path) as f:
        template = f.read()
    
    # Generate marker JavaScript
    markers = []
    
    # Add icon definitions
    markers.append("""
    var BuildingIcon = L.Icon.extend({
        options: {
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32]
        }
    });
    
    var careBuilding = new BuildingIcon({iconUrl: '../../../icon/hospital.png'});
    var houseBuilding = new BuildingIcon({iconUrl: '../../../icon/house.png'});
    var rentalBuilding = new BuildingIcon({iconUrl: '../../../icon/rental.png'});
    var jobBuilding = new BuildingIcon({iconUrl: '../../../icon/job.png'});
    """)

    # Add markers for facilities
    for facility in facilities:
        try:
            if 'id' not in facility:
                facility['id'] = generate_id(facility)
            name = facility['name'].replace("'", "\\'")
            markers.append(f"""
            var marker_{facility['id']} = L.marker([{facility['latitude']}, {facility['longitude']}], {{icon: careBuilding}})
                .bindPopup('{name}');
            """)
        except KeyError as e:
            print(f"Warning: Skipping facility due to missing data: {e}")
            continue
    
    # Add markers for residences
    for residence in residences:
        try:
            # Skip if missing required data
            if not all(k in residence for k in ['latitude', 'longitude', 'price', 'url']):
                print(f"Warning: Skipping residence due to missing required data")
                continue
                
            # Format price with commas but no decimal places
            price = "{:,.0f}".format(float(residence['price']))
            
            # Determine icon based on type
            icon = 'rentalBuilding' if residence.get('type') == 'rent' else 'houseBuilding'
            
            # Escape single quotes and create popup
            popup = f"<a href=\'{residence['url']}\' target=\'_blank\'>${price}</a>"
            markers.append(f"""
            var marker_{residence['id']} = L.marker([{residence['latitude']}, {residence['longitude']}], {{icon: {icon}}})
                .bindPopup('{popup}');
            """)
        except (KeyError, ValueError) as e:
            print(f"Warning: Skipping residence due to invalid data: {e}")
            continue
    
    # Add markers for jobs
    for job in jobs:
        try:
            # Escape single quotes in strings
            title = job['title'].replace("'", "\\'")
            company = job['company'].replace("'" "\\'")
            url = job['url'].replace("'", "\\'")
            popup = f"<a href=\'{url}\' target=\'_blank\'>{title}<br>{company}</a>"
            markers.append(f"""
            var marker_{job['id']} = L.marker([{job['latitude']}, {job['longitude']}], {{icon: jobBuilding}})
                .bindPopup('{popup}');
            """)
        except KeyError as e:
            print(f"Warning: Skipping job due to missing data: {e}")
            continue

    # Create layer groups - separate rentals and houses
    facility_markers = [f"marker_{f['id']}" for f in facilities if 'id' in f]
    house_markers = [f"marker_{r['id']}" for r in residences 
                    if 'id' in r and r.get('type') == 'own']
    rental_markers = [f"marker_{r['id']}" for r in residences 
                     if 'id' in r and r.get('type') == 'rent']
    job_markers = [f"marker_{j['id']}" for j in jobs if 'id' in j]

    # Add layer groups
    markers.append(f"var hospitals = L.layerGroup([{', '.join(facility_markers) if facility_markers else ''}]);")
    markers.append(f"var houses = L.layerGroup([{', '.join(house_markers) if house_markers else ''}]);")
    markers.append(f"var rentals = L.layerGroup([{', '.join(rental_markers) if rental_markers else ''}]);")
    markers.append(f"var jobs = L.layerGroup([{', '.join(job_markers) if job_markers else ''}]);")

    # Insert markers into template
    template = template.replace('// coordinate data is inserted here', '\n'.join(markers))
    
    # Write output file
    with open(output_path, 'w') as f:
        f.write(template)

def load_facilities(metro_name: str) -> List[Dict]:
    """Load healthcare facility data for a specific metro area"""
    # Look in the employer/facility directory from project root
    facility_path = Path(__file__).parent.parent / "employer" / "facility" / f"facilities-{metro_name}.json"
    
    with open(facility_path) as f:
        facilities = json.load(f)
    return facilities

def load_residences() -> List[Dict]:
    """Load residence data from own and rent JSON files"""
    residences = []
    
    # Load owned residences from residence/own directory
    own_path = Path(__file__).parent.parent / "residence" / "own" / "own_results" / "own_data.json"
    try:
        with open(own_path) as f:
            own_data = json.load(f)
            # Add type and generate IDs for owned residences
            for residence in own_data:
                residence['type'] = 'own'
                if 'id' not in residence:
                    residence['id'] = generate_id(residence)
            residences.extend(own_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load own residences: {e}")
    
    # Load rental residences from residence/rent directory
    rent_path = Path(__file__).parent.parent / "residence" / "rent" / "rent_results" / "rent_data.json"
    try:
        with open(rent_path) as f:
            rent_data = json.load(f)
            # Add type and generate IDs for rental residences
            for residence in rent_data:
                residence['type'] = 'rent'
                if 'id' not in residence:
                    residence['id'] = generate_id(residence)
            residences.extend(rent_data)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load rental residences: {e}")
    
    return residences

def load_jobs() -> List[Dict]:
    """Load job postings data"""
    # Look in the job directory from project root
    job_path = Path(__file__).parent.parent / "job" / "job_data.json"
    
    try:
        with open(job_path) as f:
            jobs = json.load(f)
            # Add IDs if they don't exist
            for job in jobs:
                if 'id' not in job:
                    job['id'] = generate_id(job)
        return jobs
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load job postings: {e}")
        return []