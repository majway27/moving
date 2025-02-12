import employer
from shared.utility import update_last_refreshed

def main():
    employer.assign_missing_facility_ids()
    
    # Update the last-refreshed timestamp in index.html
    update_last_refreshed()
    
if __name__ == "__main__":
    main() 