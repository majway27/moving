import json
from pathlib import Path
import re
import hashlib
from typing import Dict, List, Tuple, Optional
import sys
from pathlib import Path

# Change the import to use relative path from current file location
from client.nominatim_client import RateLimitedNominatim

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

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

# Add this after the existing imports but before other code
_nominatim = None

def get_nominatim_client() -> RateLimitedNominatim:
    """Get or create the Nominatim client singleton"""
    global _nominatim
    if _nominatim is None:
        _nominatim = RateLimitedNominatim(user_agent="healthcare_housing_search")
    return _nominatim

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
    # Delete existing map file for this city
    map_dir = Path(__file__).parent / "map"
    city_map = map_dir / f"{city.lower()}.html"
    
    try:
        if city_map.exists():
            city_map.unlink()
            # Verify deletion completed
            while city_map.exists():
                continue
            print(f"Deleted existing map: {city_map.name}")
    except Exception as e:
        print(f"Warning: Could not delete {city_map.name}: {e}")
        # If we can't delete the file, we should not proceed
        raise

    # Ensure file is deleted before proceeding
    if city_map.exists():
        raise RuntimeError(f"Could not delete existing map file for {city}")

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
    
    var careBuilding = new BuildingIcon({iconUrl: 'icon/hospital.png'});
    var houseBuilding = new BuildingIcon({iconUrl: 'icon/house.png'});
    var rentalBuilding = new BuildingIcon({iconUrl: 'icon/rental.png'});
    var jobBuilding = new BuildingIcon({iconUrl: 'icon/job.png'});
    """)

    # Track used IDs to prevent duplicates
    used_ids = set()

    # Add markers for facilities
    for facility in facilities:
        try:
            # Convert coordinates to float if they're strings
            try:
                if isinstance(facility.get('latitude'), str):
                    facility['latitude'] = float(facility['latitude'])
                if isinstance(facility.get('longitude'), str):
                    facility['longitude'] = float(facility['longitude'])
            except (ValueError, TypeError):
                print(f"Warning: Could not convert coordinates for facility: {facility.get('name', 'Unknown')}")
                continue

            if not (all(k in facility for k in ['latitude', 'longitude']) and
                   facility['latitude'] is not None and 
                   facility['longitude'] is not None and
                   isinstance(facility['latitude'], (int, float)) and
                   isinstance(facility['longitude'], (int, float))):
                print(f"Warning: Skipping facility due to invalid coordinates: {facility.get('name', 'Unknown')}")
                continue
                
            if 'id' not in facility:
                facility['id'] = generate_id(facility)
            
            if facility['id'] in used_ids:
                continue
                
            used_ids.add(facility['id'])
            
            # Double escape the name for JavaScript string
            name = facility['name'].replace('"', '\\"').replace("'", "\\'")
            markers.append(f"""
            var marker_{facility['id']} = L.marker([{facility['latitude']}, {facility['longitude']}], {{icon: careBuilding}})
                .bindPopup("{name}");
            """)
        except KeyError as e:
            print(f"Warning: Skipping facility due to missing data: {e}")
            continue
    
    # Add markers for residences
    for residence in residences:
        try:
            # Convert coordinates to float if they're strings
            try:
                if isinstance(residence.get('latitude'), str):
                    residence['latitude'] = float(residence['latitude'])
                if isinstance(residence.get('longitude'), str):
                    residence['longitude'] = float(residence['longitude'])
            except (ValueError, TypeError):
                print(f"Warning: Could not convert coordinates for residence: {residence.get('url', 'Unknown')}")
                continue

            if not (all(k in residence for k in ['latitude', 'longitude', 'price', 'url']) and
                   residence['latitude'] is not None and 
                   residence['longitude'] is not None and
                   isinstance(residence['latitude'], (int, float)) and
                   isinstance(residence['longitude'], (int, float))):
                print(f"Warning: Skipping residence due to invalid coordinates: {residence.get('url', 'Unknown')}")
                continue
            
            if 'id' not in residence:
                residence['id'] = generate_id(residence)
                
            if residence['id'] in used_ids:
                continue
                
            used_ids.add(residence['id'])
                
            price = "{:,.0f}".format(float(residence['price']))
            icon = 'rentalBuilding' if residence.get('type') == 'rent' else 'houseBuilding'
            
            # Double escape the URL for JavaScript string
            url = residence['url'].replace('"', '\\"').replace("'", "\\'")
            popup = f"<a href=\\'{url}\\' target=\\'_blank\\'>${price}</a>"
            
            markers.append(f"""
            var marker_{residence['id']} = L.marker([{residence['latitude']}, {residence['longitude']}], {{icon: {icon}}})
                .bindPopup("{popup}");
            """)
        except (KeyError, ValueError) as e:
            print(f"Warning: Skipping residence due to invalid data: {e}")
            continue
    
    # Add markers for jobs
    for job in jobs:
        try:
            # Convert coordinates to float if they're strings
            try:
                if isinstance(job.get('latitude'), str):
                    job['latitude'] = float(job['latitude'])
                if isinstance(job.get('longitude'), str):
                    job['longitude'] = float(job['longitude'])
            except (ValueError, TypeError):
                print(f"Warning: Could not convert coordinates for job: {job.get('title', 'Unknown')}")
                continue

            if not (all(k in job for k in ['latitude', 'longitude', 'title', 'company', 'url']) and
                   job['latitude'] is not None and 
                   job['longitude'] is not None and
                   isinstance(job['latitude'], (int, float)) and
                   isinstance(job['longitude'], (int, float))):
                print(f"Warning: Skipping job due to invalid coordinates: {job.get('title', 'Unknown')}")
                continue
                
            if 'id' not in job:
                job['id'] = generate_id(job)
                
            if job['id'] in used_ids:
                continue
                
            used_ids.add(job['id'])
            
            # Double escape all strings for JavaScript
            title = job['title'].replace('"', '\\"').replace("'", "\\'")
            company = job['company'].replace('"', '\\"').replace("'", "\\'")
            url = job['url'].replace('"', '\\"').replace("'", "\\'")
            popup = f"<a href=\\'{url}\\' target=\\'_blank\\'>{title}<br>{company}</a>"
            
            markers.append(f"""
            var marker_{job['id']} = L.marker([{job['latitude']}, {job['longitude']}], {{icon: jobBuilding}})
                .bindPopup("{popup}");
            """)
        except KeyError as e:
            print(f"Warning: Skipping job due to missing data: {e}")
            continue

    # Create layer groups with string-to-float conversion
    facility_markers = list(set(f"marker_{f['id']}" for f in facilities 
                              if 'id' in f and f['id'] in used_ids))
    
    house_markers = list(set(f"marker_{r['id']}" for r in residences 
                           if 'id' in r and r['id'] in used_ids 
                           and r.get('type') == 'own'))
    
    rental_markers = list(set(f"marker_{r['id']}" for r in residences 
                            if 'id' in r and r['id'] in used_ids 
                            and r.get('type') == 'rent'))
    
    job_markers = list(set(f"marker_{j['id']}" for j in jobs 
                          if 'id' in j and j['id'] in used_ids))

    # Sort markers for consistent ordering
    facility_markers.sort()
    house_markers.sort()
    rental_markers.sort()
    job_markers.sort()

    # Add layer groups only if they have markers
    if facility_markers:
        markers.append(f"var hospitals = L.layerGroup([{', '.join(facility_markers)}]);")
    else:
        markers.append("var hospitals = L.layerGroup([]);")
        
    if house_markers:
        markers.append(f"var houses = L.layerGroup([{', '.join(house_markers)}]);")
    else:
        markers.append("var houses = L.layerGroup([]);")
        
    if rental_markers:
        markers.append(f"var rentals = L.layerGroup([{', '.join(rental_markers)}]);")
    else:
        markers.append("var rentals = L.layerGroup([]);")
        
    if job_markers:
        markers.append(f"var jobs = L.layerGroup([{', '.join(job_markers)}]);")
    else:
        markers.append("var jobs = L.layerGroup([]);")

    # Create overlay maps with all layers
    markers.append("""
    var overlayMaps = {
        "Care Facilities": hospitals,
        "Houses": houses,
        "Rentals": rentals,
        "Jobs": jobs
    };
    """)

    # Insert markers into template
    marker_js = '\n'.join(markers)
    template = template.replace('// coordinate data is inserted here', marker_js)
    
    # Write output file
    with open(output_path, 'w') as f:
        f.write(template)

def load_facilities(metro_name: str) -> List[Dict]:
    """Load healthcare facility data for a specific metro area"""
    # Build state mapping from location.json
    state_mapping = {}
    try:
        metro_areas = load_locations()
        for metro in metro_areas:
            hub = metro["hub_city"]
            # Get full state name and convert to lowercase
            state = get_state_from_location(f"City, {hub['state']}")
            state_mapping[hub["name"].lower()] = state.lower()
    except Exception as e:
        print(f"Warning: Error building state mapping: {e}")
        return []
    
    state = state_mapping.get(metro_name.lower())
    if not state:
        print(f"Warning: No state mapping found for {metro_name}")
        return []
    
    # Look in the employer/facility directory from project root
    facility_path = Path(__file__).parent.parent / "employer" / "facility" / f"facilities-{state}.json"
    
    try:
        with open(facility_path) as f:
            facilities = json.load(f)
        return facilities
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load facilities for {state}: {e}")
        return []

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

def get_coordinates_from_location_local(location: str, metro_areas: List[Dict]) -> Tuple[float, float]:
    """
    Get coordinates for a location from local metro_areas data only.
    
    Args:
        location: Location string (e.g. "Denver, CO" or "Denver, Colorado")
        metro_areas: List of metro area dictionaries from location.json
        
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    if not location or ',' not in location:
        return None
        
    city, state = [part.strip() for part in location.split(',')]
    
    # Normalize city name (handle St. vs St)
    city = city.replace('St ', 'St. ')
    
    # Convert full state name to abbreviation if needed
    state_abbrev = state
    for abbrev, full_name in STATE_MAPPING.items():
        if state.upper() == full_name.upper():
            state_abbrev = abbrev
            break
    
    # Check hub cities
    for metro in metro_areas:
        hub = metro["hub_city"]
        if city.lower() == hub["name"].lower() and state_abbrev.upper() == hub["state"].upper():
            return hub["coordinates"]["lat"], hub["coordinates"]["lng"]
            
        # Check suburbs
        for suburb in metro["suburbs"]:
            if city.lower() == suburb["name"].lower() and state_abbrev.upper() == suburb["state"].upper():
                return suburb["coordinates"]["lat"], suburb["coordinates"]["lng"]
    
    return None

def save_to_location_json(city: str, state: str, lat: float, lng: float) -> None:
    """
    Save a new location to location.json under the appropriate metro area
    
    Args:
        city: City name
        state: State abbreviation
        lat: Latitude
        lng: Longitude
    """
    location_path = Path(__file__).parent / "location.json"
    try:
        # Load current data
        with open(location_path) as f:
            data = json.load(f)
            
        # Find the appropriate metro area
        state_full = STATE_MAPPING.get(state.upper(), state)
        found_metro = None
        
        for metro in data["metro_areas"]:
            hub_state = metro["hub_city"]["state"]
            if hub_state == state:
                found_metro = metro
                break
                
        if found_metro:
            # Check if city already exists
            all_cities = ([found_metro["hub_city"]] + 
                         found_metro.get("suburbs", []))
            
            for existing_city in all_cities:
                if (existing_city["name"].lower() == city.lower() and 
                    existing_city["state"].upper() == state.upper()):
                    return  # City already exists, don't add duplicate
            
            # Add as new suburb
            new_suburb = {
                "name": city,
                "state": state.upper(),
                "coordinates": {
                    "lat": lat,
                    "lng": lng
                }
            }
            
            if "suburbs" not in found_metro:
                found_metro["suburbs"] = []
            found_metro["suburbs"].append(new_suburb)
            
            # Save updated data
            with open(location_path, 'w') as f:
                json.dump(data, f, indent=2)
                
    except Exception as e:
        print(f"Warning: Failed to save location to JSON: {e}")

def lookup_coordinates(location: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates for a location using multiple methods.
    First tries the metro areas data, then falls back to Nominatim.
    If Nominatim succeeds, saves the result to location.json.
    
    Args:
        location: Location string (e.g. "Denver, CO" or "Denver, Colorado")
        
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    if not location or ',' not in location:
        return None
        
    # Parse city and state
    city, state = [part.strip() for part in location.split(',')]
    
    # Convert state to abbreviation if needed
    state_abbrev = state
    for abbrev, full_name in STATE_MAPPING.items():
        if state.upper() == full_name.upper():
            state_abbrev = abbrev
            break

    # First try getting coordinates from our metro areas data
    metro_areas = load_locations()
    coords = get_coordinates_from_location_local(location, metro_areas)
    if coords:
        return coords
        
    # If not found in metro areas, try Nominatim
    try:
        nominatim = get_nominatim_client()
        # Try with state abbreviation first
        search_location = f"{city}, {state_abbrev}"
        result = nominatim.geocode(search_location)
        
        # If that fails, try with full state name
        if not result and state_abbrev in STATE_MAPPING:
            search_location = f"{city}, {STATE_MAPPING[state_abbrev]}, United States"
            result = nominatim.geocode(search_location)
        
        if result:
            # Save to location.json
            save_to_location_json(city, state_abbrev, result.latitude, result.longitude)
            return (result.latitude, result.longitude)
            
    except Exception as e:
        print(f"Warning: Nominatim geocoding failed for {location}: {e}")
    
    return None

def load_jobs() -> List[Dict]:
    """Load job postings data and add coordinates"""
    # Look in the job directory from project root
    job_path = Path(__file__).parent.parent / "job" / "job_data.json"
    
    try:
        # Load jobs
        with open(job_path) as f:
            jobs = json.load(f)
        
        # Process each job
        for job in jobs:
            try:
                # Generate ID if needed
                if 'id' not in job:
                    job['id'] = generate_id(job)
                
                # Add coordinates if missing
                if 'latitude' not in job or 'longitude' not in job:
                    if 'location' in job:
                        coords = lookup_coordinates(job['location'])  # Use lookup_coordinates instead
                        if coords:
                            job['latitude'], job['longitude'] = coords
                        else:
                            print(f"Warning: Could not find coordinates for job posting location: {job['location']}")
                    else:
                        print(f"Warning: Job missing location field: {job.get('title', 'Unknown title')}")
                        
            except Exception as e:
                print(f"Warning: Error processing job: {e}")
                continue
                
        # Return only jobs with coordinates
        valid_jobs = [job for job in jobs if 'latitude' in job and 'longitude' in job]
        if len(valid_jobs) < len(jobs):
            print(f"Note: {len(jobs) - len(valid_jobs)} jobs skipped due to missing coordinates")
            
        return valid_jobs
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load job postings: {e}")
        return []