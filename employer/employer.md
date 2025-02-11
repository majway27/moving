# employer

## Employer Module

### Functional Description

- This module manages employer-related data and operations for healthcare facilities
- It maintains a list of employers and their locations
- It handles employer name normalization and mapping
- It manages facility IDs for healthcare locations

### Technical Design (by layer)

1. *Data Management* `employer/employer.py`
    - Handles loading and saving of employer data
    - Maintains employer-location relationships
    - Manages excluded employers list
    - Handles employer name normalization and mapping
    - Manages facility IDs and sorting

2. *Data Files*
    - `employers.json` - Stores employer names and their associated locations
    - `exclude-employers.json` - List of employers to exclude from searches
    - `map-employers.json` - Mapping dictionary for canonical employer names
    - `source/facilities-colorado.json` - List of healthcare facilities with their IDs

3. *Control* `employer/runner-employer.py`
    - Execution & pipeline management logic
    - Currently handles facility ID assignment
    - Set the last-refreshed timestamp in `index.html` via `shared/utility.py`

### Key Functions

1. **Employer Management**
    - `load_employers()` - Loads employer data from JSON file
    - `save_employers()` - Saves employer data to JSON file
    - `update_employers()` - Updates employer list with new companies and locations

2. **Name Processing**
    - `normalize_employer_name()` - Standardizes employer names for comparison
    - `remap_employer_name()` - Maps alternate names to canonical employer names

3. **Exclusion Management**
    - `load_excluded_employers()` - Loads list of employers to exclude
    - `load_employer_map()` - Loads employer name mapping dictionary

4. **Facility Management**
    - `sort_facilities_json()` - Sorts facilities alphabetically by name
    - `assign_missing_facility_ids()` - Assigns unique IDs to facilities

### TODO

1. Add validation for employer data formats
2. Implement employer name fuzzy matching
3. Add facility location geocoding
4. Create API for employer data queries

### Roadmap

- Implement employer data versioning
- Add support for facility types and specialties
- Create employer data visualization tools
- Develop employer relationship mapping 