import json
from pathlib import Path

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

def load_locations():
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