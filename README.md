# Moving to Denver Project

## Summary

- This is a project to map useful geographic data in Denver, CO.
- The major points of interest are:
  - Hospitals/Clinics
  - New Housing, by price ~500k
  - Apartments / Rentals

## Setup

### Python VENV

1. `pip install folium`
2. `pip install geopy`

Optional: `pip install -U homeharvest`

### Local Development

`python -m http.server 8000`

## Data

- https://cha.com/find-a-hospital/

### Icons

- https://www.iconfinder.com/search?q=apartment&price=free
- https://favicon.io/favicon-generator/

## Tools

### Nominatim (via geopy)

- https://geopy.readthedocs.io/en/stable/
- https://nominatim.org/release-docs/develop/api/Search/

### RapidAPI

- https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
- https://rapidapi.com/s.mahmoud97/api/zillow56
- https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-glassdoor-data

### Healthcare Data Sets

- https://data.cms.gov/provider-data/topics/hospitals
  - https://data.cms.gov/provider-data/topics/provider-data/
    - "A list of the state averages for the HCAHPS survey responses. HCAHPS is a national, standardized survey of hospital patients about their experiences during a recent inpatient hospital stay."
    - "The national average for the HCAHPS survey categories. HCAHPS is a national, standardized survey of hospital patients about their experiences during a recent inpatient hospital stay."
    - "The Medicare Spending Per Beneficiary (MSPB) Measure shows whether Medicare spends more, less, or about the same for an episode of care (episode) at a specific hospital compared to all hospitals nationally. An MSPB episode..."
    - "A list of ambulatory surgical center ratings for the Outpatient and Ambulatory Surgery Consumer Assessment of Healthcare Providers and Systems (OAS CAHPS) survey. The OAS CAHPS survey collects information about patients' experiences of care in..."
  - https://data.cms.gov/provider-data/about
    - "Centers for Medicare & Medicaid Services’ (CMS) official data that are used on the Medicare Care Compare website and directories. Our goal is to make our data readily available in open, accessible, and machine-readable formats."
    - "Works of the U.S. Government are in the public domain and you don’t need permission to reuse them, but an attribution to the agency as the source is appreciated. Your materials, however, shouldn’t give the false impression that the government’s endorsing your commercial products or services. See [42 U.S.C 1320b-10](https://www.ssa.gov/OP_Home/ssact/title11/1140.htm)."


### Other

- https://github.com/Bunsly/HomeHarvest
- https://leafletjs.com/examples/quick-start/
- https://tabulator.info/
