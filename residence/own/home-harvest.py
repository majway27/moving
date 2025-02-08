from homeharvest import scrape_property
from datetime import datetime

# Generate filename based on current timestamp
#current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#filename = f"HomeHarvest_{current_timestamp}.csv"

searchLocations = ['Aurora, CO', 'Brighton, CO', 'Broomfield, CO', 'Centennial, CO', 'Erie, CO', 'Lafayette, CO', 'Longmont, CO', 'Parker, CO', 'Westminster, CO']
#searchLocations = ['Parker, CO']

CHECK_FOR_SALE = False
CHECK_FOR_RENT = True

if CHECK_FOR_SALE:
  for searchLocation in searchLocations:

    properties = scrape_property(
      location=searchLocation,
      listing_type="for_sale",  # or (for_sale, for_rent, pending)
      past_days=30,  # sold in last 30 days - listed in last 30 days if (for_sale, for_rent)

      # property_type=['single_family','multi_family'],
      property_type=['single_family'],
      # date_from="2023-05-01", # alternative to past_days
      # date_to="2023-05-28",
      # foreclosure=True
      # mls_only=True,  # only fetch MLS listings
    )
    print(f"Number of properties: {len(properties)}")

    # Export to csv
    location_name = searchLocation.replace(', CO', '')
    filename = f"{location_name}-Sale.csv"
    properties.to_csv(filename, index=False)
    print(properties.head())

if CHECK_FOR_RENT:
  for searchLocation in searchLocations:
    
    properties = scrape_property(
      location=searchLocation,
      listing_type="for_rent",  # or (for_sale, for_rent, pending)
      past_days=30,  # sold in last 30 days - listed in last 30 days if (for_sale, for_rent)

      # property_type=['single_family','multi_family'],
      property_type=['single_family'],
      # date_from="2023-05-01", # alternative to past_days
      # date_to="2023-05-28",
      # foreclosure=True
      # mls_only=True,  # only fetch MLS listings
    )
    print(f"Number of properties: {len(properties)}")

    # Export to csv
    location_name = searchLocation.replace(', CO', '')
    filename = f"{location_name}-Rent.csv"
    properties.to_csv(filename, index=False)
    print(properties.head())