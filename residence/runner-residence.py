from intake_listings import ResidenceSearch
from format_listings import generate_listings_data, save_filtered_listings
from pathlib import Path
from datetime import datetime

def main():
    # Create residence search instance
    residence_search = ResidenceSearch()
    
    # Define search locations
    locations = [
        'Aurora, CO',
    ]
    
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
    
    # Search for both rental and sale properties
    for modality in ["rent", "own"]:
        print(f"\n=== Searching {modality.upper()} listings ===")
        
        for location in locations:
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
    
    # Generate the formatted data files for both modalities
    print("\nGenerating formatted listing data...")
    generate_listings_data("rent")
    generate_listings_data("own")
    
    print("\nResidence search pipeline complete!")

if __name__ == "__main__":
    main() 