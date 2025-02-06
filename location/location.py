import json
from pathlib import Path

def load_locations():
    """Load and parse the location.json file"""
    location_path = Path(__file__).parent / "location.json"
    with open(location_path) as f:
        data = json.load(f)
    return data["metro_areas"]

def format_location(city, state):
    """Format city and state into search string"""
    return f"{city}, {state}" 