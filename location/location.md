# location

## Location Module

### Functional Description

- This module manages cartographically plotted data relevant to core residence, job, and healthcare facility data.

### Technical Design (by layer)

1. *Client*  `location/client/nominatim_client.py`
    - This is the client for the Nominatim API. It provides cooridinate lookups and address searches for a given location.
    - Additional clients could be defined here.

2. *Data Management* `location/location.py`
    - Handles loading and saving of location data
    - Writing to `location/maps/*.html` maps.
    - General geo-orriented utility functions.

3. *Data Files*
    - `location/location.json` - Stores location data
    - `icon/*.png` - Icon files for map markers.

3A. *Data Files*
    - `employer/facility/facilities-colorado.json` - source data for healthcare facilities in Colorado.
    - [TODO]  `employer/facility/facilities-minnesota.json` - source data for healthcare facilities in Minnesota.
    - [TODO]  `employer/facility/facilities-arizona.json` - source data for healthcare facilities in Arizona.

3B. *Data Files*
    - `residence/own/own_results/own_data.json` - home sale listings source data for all locations.
    - `residence/rent/rent_results/rent_data.json` - rental listings source data for all locations.

3C. *Data Files*
    - job_data.json has a location string.  This can be matched to location.json, which contains a location string and coordinates pair.
    - `job/job_data.json` - job postings source data, a posting has a location.
    - `location/location.json` - location data, a location has a name, state, and coordinates.

4. *View*  `location/location.html` - The responsibility of this file is:
    - This is the end user view of the combined residence and job data.
    - This html file is directly altered by the pipeline, showing calculated metro profile scores.

4A. *View*  `location/map/denver.html` - The responsibility of this file is:
    - This is the *output* file; the end user view of the combined residence and job data for location: *Denver, CO*.
    - `location/map/template/base-denver.html` is the base map for Denver, CO.  The base map is used as a *template* for `location/map/denver.html` during pipeline map generation.
    - This html file is directly altered by the pipeline, coordinates are plotted on a map for for residence (rent|own), healthcare facilities, and job postings.

4B. *View*  `location/map/phoenix.html` - The responsibility of this file is:
    - This is the *output* file; the end user view of the combined residence and job data for location: *Phoenix, AZ*.
    - `location/map/template/base-phoenix.html` is the base map for Phoenix, AZ.  The base map is used as a *template* for `location/map/phoenix.html` during pipeline map generation.
    - This html file is directly altered by the pipeline, coordinates are plotted on a map for for residence (rent|own), healthcare facilities, and job postings.

4C. *View*  `location/map/minneapolis.html` - The responsibility of this file is:
    - This is the *output* file; the end user view of the combined residence and job data for location: *Minneapolis, MN*.
    - `location/map/template/base-minneapolis.html` is the base map for Minneapolis, MN.  The base map is used as a *template* for `location/map/minneapolis.html` during pipeline map generation.
    - This html file is directly altered by the pipeline, coordinates are plotted on a map for for residence (rent|own), healthcare facilities, and job postings.

5. *Control* `location/runner-location.py`
    - Execution & pipeline management logic
    - Abstract surface for overarching orchestration
    - Set the last-refreshed timestamp in `index.html` via `shared/utility.py`

### Leaflet.js

- Leaflet.js is a JavaScript library for creating interactive maps.
- Leaflet.js is used to create the output maps in `location/map/*.html`.

#### Example Leaflet.js Code

```javascript

// Icon files
var careBuilding = new BuildingIcon({iconUrl: 'icon/hospital.png'});  // healthcare facility
var houseBuilding = new BuildingIcon({iconUrl: 'icon/house.png'});  // residence (own)
var rentalBuilding = new BuildingIcon({iconUrl: 'icon/rental.png'});  // residence (rent)
var jobBuilding = new BuildingIcon({iconUrl: 'icon/job.png'});  // job

// Major Hospitals with Imaging
var marker_banner_university = L.marker([33.4757, -112.0436], {icon: careBuilding}).bindPopup('Banner University Medical Center Phoenix');
var marker_st_josephs = L.marker([33.4789, -112.0668], {icon: careBuilding}).bindPopup('St. Joseph\'s Hospital and Medical Center');
var marker_banner_estrella = L.marker([33.4933, -112.2607], {icon: careBuilding}).bindPopup('Banner Estrella Medical Center');
var marker_honor_health_deer_valley = L.marker([33.6800, -112.0279], {icon: careBuilding}).bindPopup('HonorHealth Deer Valley Medical Center');
var marker_mayo_clinic = L.marker([33.5817, -111.9642], {icon: careBuilding}).bindPopup('Mayo Clinic Hospital');

// Dedicated Imaging Centers
var marker_simon_med_central = L.marker([33.4982, -112.0738], {icon: careBuilding}).bindPopup('SimonMed Imaging - Central Phoenix');
var marker_valley_rad_downtown = L.marker([33.4789, -112.0731], {icon: careBuilding}).bindPopup('Valley Radiologists - Downtown Phoenix');
var marker_arizona_diagnostic = L.marker([33.5081, -112.0731], {icon: careBuilding}).bindPopup('Arizona Diagnostic Radiology');
var marker_simon_med_scottsdale = L.marker([33.5722, -111.9277], {icon: careBuilding}).bindPopup('SimonMed Imaging - Scottsdale');
var marker_valley_rad_glendale = L.marker([33.5317, -112.1859], {icon: careBuilding}).bindPopup('Valley Radiologists - Glendale');

// Update the hospitals layer group
var hospitals = L.layerGroup([
    marker_banner_university,
    marker_st_josephs,
    marker_banner_estrella,
    marker_honor_health_deer_valley,
    marker_mayo_clinic,
    marker_simon_med_central,
    marker_valley_rad_downtown,
    marker_arizona_diagnostic,
    marker_simon_med_scottsdale,
    marker_valley_rad_glendale
]);

// Residence (own)
var marker_3164891363374874266 = L.marker([39.955654, -104.801868], {icon: houseBuilding}).bindPopup('<a href=\'https://www.realtor.com/realestateandhomes-detail/2174-Farmlore-Dr_Brighton_CO_80601_M99752-70619\' target=\'_blank\'>$489K</a>');
	var marker_6356970073918225306 = L.marker([39.9533, -104.789393], {icon: houseBuilding}).bindPopup('<a href=\'https://www.realtor.com/realestateandhomes-detail/2305-Serenidad-St_Brighton_CO_80601_M92319-81314\' target=\'_blank\'>$471K</a>');
	var marker_1366429735587325399 = L.marker([39.990665, -104.753292], {icon: houseBuilding}).bindPopup('<a href=\'https://www.realtor.com/realestateandhomes-detail/224-Kino-Ct_Brighton_CO_80601_M90467-75809\' target=\'_blank\'>$500K</a>');

```

### TODO

1. Enhanced matching of job location, from coarse location.json coordinates to exact facility coordinates (ie from employer/facility/facilities-colorado.json)
2. ?

### Roadmap

- You could use this data structure to:
  - Power a comparison tool between different metro areas
  - Filter locations based on specific criteria (e.g., max home price, climate preferences)
  - Calculate commute times from suburbs to hub cities
  - Generate detailed reports for different locations
  - Create interactive maps showing the relationship between hub cities and suburbs
- Political leanings mapping

### Comparison Notes

#### Denver, CO

- ?

#### Phoenix, AZ

- ?

#### Minneapolis, MN

- Lower cost of living than Denver but higher than Phoenix.
- Strong public transit score.
- Diverse job market with emphasis on healthcare (Mayo Clinic, UnitedHealth) and financial services.
- Distinctive climate data showing the significant winter cold and moderate summers.
