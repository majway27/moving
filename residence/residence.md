# residence

## Residence Module

### Functional Description

- This module is a pipeline; used to search for housing; both for sale and for rent in a location of interest. 
- It uses the [Zillow Rapid API](https://rapidapi.com/s.mahmoud97/api/zillow56) to search listings and then formats the results into a table.

### Technical Design (by layer)

1. *Client*  `residence/client/rapid_api_client.py`
    - This is the client for the Zillow Rapid API. It is the entry point for multi-source postings.
    - Additional clients could be defined here.
2. *Intake*  `residence/intake_listings.py` - The responsibility of this file is:
    - Abstract and wrap 1+ API clients (Zillow Rapid API, etc.)
    - Specify modality (own|rent).  Specify key search parameters (ex: location, cost (monthly rent|sale price), etc.).
    - Bucket results by modality (own|rent) and location (Denver, Phoenix, etc.)
    - Coarsely filter client responses
    - Output both a raw and a filtered result set as csv files in the modality-repective results subdirectory (mode: overwrite)
        - `residence/own/own_results/`
        - `residence/rent/rent_results/`
3. *Transform*  `residence/format_listings.py` - The responsibility of this file is:
    - Load listing data from filtered csv files
    - For each filtered csv, output similarly named json file in the modality-repective results subdirectory (mode: overwrite) [`residence/own/own_results/`, `residence/rent/rent_results/`] a single consolidated json file (which is expected by the view layer).
4A. *View*  `residence/own/own.html` - The responsibility of this file is:
    - This is the end user view of the enhanced (filtered and formated) listing data for the modality (own).
    - This html file is not directly altered by the pipeline, rather it expects a consolidated json file (`residence/own/own_results/own_data.json`).
4B. *View*  `residence/rent/rent.html` - The responsibility of this file is:
    - This is the end user view of the enhanced (filtered and formated) listing data for the modality (rent).
    - This html file is not directly altered by the pipeline, rather it expects a consolidated json file (`residence/rent/rent_results/rent_data.json`).
5. *Control* - `residence/runner-residence.py` - The responsibility of this file is:
    - Execution & pipeline management logic
    - Abstract surface for overarching orchestration

### TODO

1. ?

### Roadmap

- ?
