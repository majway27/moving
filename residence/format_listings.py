import json
from datetime import datetime
from pathlib import Path
import csv
import time

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
    # Map the incoming data fields to our expected fields
    address = f"{listing.get('streetAddress', '')}, {listing.get('city', '')}, {listing.get('state', '')}"
    
    # Only format if we have actual data
    if not listing or not all([
        listing.get('streetAddress'),
        listing.get('price'),
        listing.get('bedrooms'),
        listing.get('bathrooms')
    ]):
        print("Rejecting listing due to missing critical data")
        return None
        
    # Construct Zillow URL using ZPID if available
    zpid = listing.get('zpid')
    url = f"https://www.zillow.com/homedetails/{zpid}_zpid/" if zpid else '#'
        
    formatted = {
        'address': address,
        'price': listing.get('price', 'N/A'),
        'beds': listing.get('bedrooms', 'N/A'),
        'baths': listing.get('bathrooms', 'N/A'),
        'sqft': listing.get('livingArea', 'N/A'),
        'year_built': listing.get('yearBuilt', 'N/A'),
        'description': listing.get('description', ''),
        'url': url,
        'location': f"{listing.get('city', '')}, {listing.get('state', '')}",
        'list_date': listing.get('timeOnZillow', ''),
        'primary_photo': listing.get('imgSrc', ''),
        'alt_photos': []  # We'll need to handle additional photos differently if available
    }
    
    #print(f"Successfully formatted listing for: {formatted['address']}")
    return formatted

def generate_listings_data(modality):
    """
    Generate consolidated listings data JSON file for a specific modality.
    If called, there is an expectation that there are listings to process.
    Logic is added to deal with moderate filesystem latency.
    
    Args:
        modality: Either "own" or "rent"
        
    Raises:
        RuntimeError: If no CSV files are found after retries
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
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        # Look for both filtered.csv and _filtered.csv patterns
        csv_files = list(listings_dir.glob('*filtered.csv'))
        if modality == "own":
            csv_files.extend(list(listings_dir.glob('*Sale_filtered.csv')))
        if modality == "rent":
            csv_files.extend(list(listings_dir.glob('*rent_filtered.csv')))
            
        print(f"Found {len(csv_files)} CSV files in {listings_dir}")
        if csv_files:
            break
            
        if attempt < max_retries - 1:
            print(f"No CSV files found for {modality}, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
    
    if not csv_files:
        raise RuntimeError(f"No CSV files found for {modality} after {max_retries} attempts. Expected filtered CSV files in {listings_dir}")
    
    # Process each CSV file
    for listing_file in csv_files:
        print(f"Processing file: {listing_file}")
        listing_data = load_listing_file(listing_file)
        print(f"Found {len(listing_data)} entries in {listing_file}")
        
        formatted_listings = []
        for listing in listing_data:
            fmt = format_listing(listing)
            if fmt is not None:
                formatted_listings.append(fmt)
        
        print(f"Formatted {len(formatted_listings)} valid listings from {listing_file}")
        all_listings.extend(formatted_listings)

    if not all_listings:
        print(f"Warning: No valid listings found in CSV files for {modality}")
        return

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
    if not filtered_listings:
        print(f"No filtered listings to save for {location} {modality}")
        return
        
    listings_to_save = []
    for listing in filtered_listings:
        formatted_listing = format_listing(listing)
        if formatted_listing:  # Only add non-None listings
            listings_to_save.append(formatted_listing)
    
    if not listings_to_save:
        print(f"No valid listings to save for {location} {modality}")
        return
    
    # Save to a JSON file in appropriate results directory
    output_dir = Path(f"{modality}/{modality}_results")
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename based on location
    safe_location = location.replace(", ", "_").lower()
    output_file = output_dir / f"{safe_location}_{modality}.json"
    
    # Write the file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(listings_to_save, f, ensure_ascii=False, indent=2)
    
    # Verify the file was written successfully with retries
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        if output_file.exists() and output_file.stat().st_size > 0:
            print(f"Saved {len(listings_to_save)} listings to {output_file}")
            return
            
        if attempt < max_retries - 1:
            print(f"Waiting for file write to complete... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
    
    raise RuntimeError(f"Failed to verify file write for {output_file} after {max_retries} attempts")
