import json
from pathlib import Path
from typing import Set, Dict, List


# Employer
def load_employers() -> Dict[str, List[str]]:
    """Load existing employers from JSON file or create empty dict if file doesn't exist."""
    employer_path = Path(__file__).parent / "employers.json"
    try:
        with open(employer_path, 'r') as f:
            data = json.load(f)
            # Convert to dictionary for easier lookup
            return {emp["name"]: emp["locations"] for emp in data["employers"]}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_employers(employers: Dict[str, List[str]]) -> None:
    """Save employers dictionary to JSON file."""
    employer_path = Path(__file__).parent / "employers.json"
    # Convert to sorted list of dictionaries
    sorted_employers = [
        {"name": name, "locations": locations}
        for name, locations in sorted(employers.items())
    ]
    with open(employer_path, 'w') as f:
        json.dump({"employers": sorted_employers}, f, indent=2)

def update_employers(jobs: list) -> None:
    """Update employers set with new companies and locations from job results."""
    employers = load_employers()
    
    for job in jobs:
        company = job.get('employer_name')
        location = job.get('location')
        
        if not company or not location:
            continue
            
        if company not in employers:
            employers[company] = []
            
        if location not in employers[company]:
            employers[company].append(location)
            employers[company].sort()  # Keep locations sorted
            
    save_employers(employers)

def normalize_employer_name(employer_name: str) -> str:
    """Normalize employer name for consistent comparison."""
    if not employer_name:
        return ""
    # Remove extra spaces, convert to lowercase
    return " ".join(employer_name.lower().split())


# Excluded Employers
def load_excluded_employers() -> set:
    """Load the list of employers to exclude from searches."""
    try:
        exclude_path = Path(__file__).parent / "exclude-employers.json"
        with open(exclude_path, 'r') as f:
            # Normalize all excluded employer names
            return {normalize_employer_name(name) for name in json.load(f)}
    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: Could not load excluded employers list")
        return set()

def load_employer_map() -> dict:
    """Load the employer name mapping dictionary."""
    try:
        map_path = Path(__file__).parent / "map-employers.json"
        with open(map_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: Could not load employer mapping")
        return {}


# Cannoical Name Re-Mapping
def remap_employer_name(employer_name: str, employer_map: dict) -> str:
    """Remap employer name using the mapping dictionary."""
    if not employer_name:
        return employer_name
    return employer_map.get(employer_name, employer_name) 