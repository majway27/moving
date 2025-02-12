import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import location.py directly since we're in the same directory
from location import load_locations, load_facilities, load_residences, load_jobs, generate_map
from shared.utility import update_last_refreshed

def generate_maps_for_metro(metro_name: str) -> None:
    """
    Generate map for a specific metropolitan area.
    
    Args:
        metro_name: Name of the metropolitan area (e.g., 'denver', 'phoenix', 'minneapolis')
    """
    print(f"\nGenerating map for {metro_name.title()}...")
    
    # Define paths
    template_path = Path(__file__).parent / "map" / "template" / f"base-{metro_name}.html"
    output_path = Path(__file__).parent / "map" / f"{metro_name}.html"
    
    # Load data for markers
    try:
        residences = load_residences()
        print(f"Loaded {len(residences)} residence listings")
    except Exception as e:
        print(f"Warning: Error loading residences: {e}")
        residences = []
        
    try:
        facilities = load_facilities(metro_name)
        print(f"Loaded {len(facilities)} healthcare facilities")
    except Exception as e:
        print(f"Warning: Error loading facilities: {e}")
        facilities = []
        
    try:
        jobs = load_jobs()
        print(f"Loaded {len(jobs)} job postings")
    except Exception as e:
        print(f"Warning: Error loading jobs: {e}")
        jobs = []
    
    # Generate the map
    try:
        generate_map(
            city=metro_name,
            template_path=template_path,
            output_path=output_path,
            residences=residences,
            facilities=facilities,
            jobs=jobs
        )
        print(f"Successfully generated map at {output_path}")
    except Exception as e:
        print(f"Error generating map for {metro_name}: {e}")

def main() -> None:
    """Main function to run the location pipeline."""
    print("Starting location pipeline...")
    
    # Load metro areas from configuration
    metro_areas = load_locations()
    
    # Generate maps for each metro area
    for metro in metro_areas:
        metro_name = metro["hub_city"]["name"].lower()
        generate_maps_for_metro(metro_name)
    
    # Update the last-refreshed timestamp in index.html
    update_last_refreshed()
    
    print("\nLocation pipeline complete")

if __name__ == "__main__":
    main() 