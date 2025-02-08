import json
import os
from datetime import datetime
from pathlib import Path
import csv

def load_listing_file(listing_file):
    """Load and parse a single listing CSV file."""
    try:
        listings = []
        with open(listing_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                listings.append(row)
        return listings
    except Exception as e:
        print(f"Error reading {listing_file}: {str(e)}")
        return []

def format_listing(listing):
    """Format a single listing entry for the table."""
    return {
        'address': listing.get('full_street_line', 'N/A'),
        'price': listing.get('list_price', 'N/A'),
        'beds': listing.get('beds', 'N/A'),
        'baths': listing.get('full_baths', 'N/A'),
        'sqft': listing.get('sqft', 'N/A'),
        'year_built': listing.get('year_built', 'N/A'),
        'description': listing.get('text', ''),
        'url': listing.get('property_url', '#'),
        'location': f"{listing.get('city', '')}, {listing.get('state', '')}",
        'list_date': listing.get('list_date', ''),
        'primary_photo': listing.get('primary_photo', ''),
        'alt_photos': listing.get('alt_photos', '').split(', ') if listing.get('alt_photos') else []
    }

def generate_listings_data(modality):
    """
    Generate consolidated listings data JSON file for a specific modality.
    
    Args:
        modality: Either "own" or "rent"
    """
    # Get the current script's directory
    current_dir = Path(__file__).parent
    
    # Define paths relative to the script location
    listings_dir = current_dir / f"{modality}/{modality}_results"
    output_file = listings_dir / f"{modality}_data.json"
    
    # Ensure the listings directory exists
    if not listings_dir.exists():
        print(f"Creating listings directory at {listings_dir}")
        listings_dir.mkdir(parents=True, exist_ok=True)
        return
    
    # Process all listing files
    all_listings = []
    for listing_file in listings_dir.glob('*filtered.csv'):
        listing_data = load_listing_file(listing_file)
        formatted_listings = [format_listing(listing) for listing in listing_data]
        all_listings.extend(formatted_listings)

    # Sort listings by date (newest first), handling missing dates
    all_listings.sort(
        key=lambda x: x.get('list_date', '') or '',  # Use empty string if date is None
        reverse=True
    )
    
    # Write the combined listing data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_listings, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {modality} data file with {len(all_listings)} listings at {output_file}")

def save_filtered_listings(filtered_listings, modality, location):
    """
    Save filtered listings to a JSON file in the appropriate results directory
    
    Args:
        filtered_listings: List of filtered listing results
        modality: "own" or "rent"
        location: Location string (e.g., "Denver, CO")
    """
    listings_to_save = []
    for listing in filtered_listings:
        # Ensure we have a valid date, default to empty string if missing
        list_date = listing.get('list_date', '')
        if not list_date:
            list_date = datetime.now().isoformat()
            
        formatted_listing = format_listing(listing)
        listings_to_save.append(formatted_listing)
    
    # Save to a JSON file in appropriate results directory
    output_dir = Path(f"{modality}/{modality}_results")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename based on location
    safe_location = location.replace(", ", "_").lower()
    output_file = output_dir / f"{safe_location}_{modality}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(listings_to_save, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    # Generate both rental and sale listing data
    generate_listings_data("rent")
    generate_listings_data("own") 