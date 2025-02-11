import employer
from shared.utility import set_last_refreshed

def main():
    employer.assign_missing_facility_ids()
    set_last_refreshed()
    
if __name__ == "__main__":
    main() 