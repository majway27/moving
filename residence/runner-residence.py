from intake_listings import ResidenceSearch
from format_listings import generate_listings_data, save_filtered_listings
from pathlib import Path
from datetime import datetime
from location.location import load_locations, format_location
from shared.utility import update_last_refreshed

def main():
    # Create residence search instance
    residence_search = ResidenceSearch()
    
    # Load locations from configuration
    metro_areas = load_locations()
    
    # Define price ranges for each modality
    price_ranges = {
        "rent": {
            "min_price": 1500,
            "max_price": 2700
        },
        "own": {
            "min_price": 450000,
            "max_price": 500000
        }
    }
    
    # Track whether each modality had results
    has_results = {
        "rent": False,
        "own": False
    }
    
    # Search for both rental and sale properties
    for modality in ["rent", "own"]:
        print(f"\n=== Searching {modality.upper()} listings ===")
        
        for metro in metro_areas:
            # Process hub city
            hub = metro["hub_city"]
            location = format_location(hub["name"], hub["state"])
            
            print(f"\nSearching {location}...")
            
            # Search with price filters
            results = residence_search.search_by_location(
                modality=modality,
                location=location,
                min_price=price_ranges[modality]["min_price"],
                max_price=price_ranges[modality]["max_price"]
            )
            
            if results:
                print(f"Found {len(results)} total listings")
                
                # Filter results
                filtered_results = residence_search.filter_results(
                    results=results,
                    modality=modality,
                    exclude_pending=True,
                    exclude_new_construction=False
                )
                
                print(f"Found {len(filtered_results)} filtered listings")
                
                if filtered_results:
                    has_results[modality] = True
                    # Save filtered results
                    save_filtered_listings(filtered_results, modality, location)
                    
                    # Display sample of results
                    for listing in filtered_results[:3]:  # Show first 3 listings
                        print("\n---")
                        print(f"Address: {listing.get('full_street_line', 'N/A')}")
                        print(f"Price: ${listing.get('list_price', 'N/A')}")
                        print(f"Beds/Baths: {listing.get('beds', 'N/A')}/{listing.get('full_baths', 'N/A')}")
                        print(f"Sqft: {listing.get('sqft', 'N/A')}")
            else:
                print(f"No results found for {location}")
            
            # Process suburbs
            for suburb in metro["suburbs"]:
                location = format_location(suburb["name"], suburb["state"])
                print(f"\nSearching {location}...")
                
                results = residence_search.search_by_location(
                    modality=modality,
                    location=location,
                    min_price=price_ranges[modality]["min_price"],
                    max_price=price_ranges[modality]["max_price"]
                )
                
                if results:
                    print(f"Found {len(results)} total listings")
                    
                    filtered_results = residence_search.filter_results(
                        results=results,
                        modality=modality,
                        exclude_pending=True,
                        exclude_new_construction=False
                    )
                    
                    print(f"Found {len(filtered_results)} filtered listings")
                    
                    if filtered_results:
                        has_results[modality] = True
                        # Save filtered results
                        save_filtered_listings(filtered_results, modality, location)
                        
                        # Display sample of results
                        for listing in filtered_results[:3]:
                            print("\n---")
                            print(f"Address: {listing.get('full_street_line', 'N/A')}")
                            print(f"Price: ${listing.get('list_price', 'N/A')}")
                            print(f"Beds/Baths: {listing.get('beds', 'N/A')}/{listing.get('full_baths', 'N/A')}")
                            print(f"Sqft: {listing.get('sqft', 'N/A')}")
                else:
                    print(f"No results found for {location}")
    
    # Generate the formatted data files only for modalities with results
    print("\nGenerating formatted listing data...")
    for modality in ["rent", "own"]:
        if has_results[modality]:
            print(f"Generating {modality} data file...")
            try:
                generate_listings_data(modality)
            except RuntimeError as e:
                print(f"Error generating {modality} data: {e}")
        else:
            print(f"Skipping {modality} data generation - no results found")
    
    print("\nResidence search pipeline complete!")
    
    # Update the last-refreshed timestamp
    try:
        update_last_refreshed('residence')
        print("Updated last-refreshed timestamp")
    except Exception as e:
        print(f"Error updating last-refreshed timestamp: {e}")

if __name__ == "__main__":
    main() 