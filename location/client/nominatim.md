# Nominatim

## API

### Overview

- /search - search OSM objects by name or type
- /reverse - search OSM object by their location
- /lookup - look up address details for OSM objects by their ID
- /status - query the status of the server
- /deletable - list objects that have been deleted in OSM but are held back in Nominatim in case the deletion was accidental
- /polygons - list of broken polygons detected by Nominatim
- /details - show internal details for an object (for debugging only)

### Search

- https://nominatim.org/release-docs/develop/api/Search/
- The search API allows you to look up a location from a textual description or address. 
- Nominatim supports structured and free-form search queries.

### Reverse

- https://nominatim.org/release-docs/develop/api/Reverse/
- Reverse geocoding generates an address from a coordinate given as latitude and longitude.

## Nominatim Usage Policy (aka Geocoding Policy) https://operations.osmfoundation.org/policies/nominatim/

- This is an Acceptable Use Policy for the server running at nominatim.openstreetmap.org and does not apply to nominatim services run by yourself or other organisations
- OSM’s Nominatim service is mainly there to power the search bar on openstreetmap.org. We are in principle happy for the public API to be used by external users for creative and unexpected uses. However, be aware that the service runs on donated servers and has a very limited capacity. We therefore ask you to limit your use and adhere to this usage policy.
-Use of any OSMF provided service is further governed by the OSMF Terms of Use .

### Requirements

- No heavy uses (an absolute maximum of 1 request per second).
- Provide a valid HTTP Referer or User-Agent identifying the application (stock User-Agents as set by http libraries will not do).
- Clearly display attribution as suitable for your medium.
- Data is provided under the ODbL license which requires to share alike (although small extractions are likely to be covered by fair usage / fair dealing).

### Websites and Apps

- Use that is directly triggered by the end-user (for example, user searches for something) is ok, provided that your number of users is moderate. Note that the usage limits above apply per website/application: the sum of traffic by all your users should not exceed the limits.
- Apps must make sure that they can switch the service at our request at any time (in particular, switching should be possible without requiring a software update). If at all possible, set up a proxy and also enable caching of requests.
- Note: periodic requests from apps are considered bulk geocoding and as such are strongly discouraged. It may be okay if your app has very few users and applies appropriate caching of results. Make sure you stay well below the API usage limits.

### Bulk Geocoding

- As a general rule, bulk geocoding of larger amounts of data is not encouraged. If you have regular geocoding tasks, please, look into alternatives below. Smaller one-time bulk tasks may be permissible, if these additional rules are followed
- limit your requests to a single thread
- limited to 1 machine only, no distributed scripts (including multiple Amazon EC2 instances or similar)
- Results must be cached on your side. Clients sending repeatedly the same query may be classified as faulty and blocked.

### Unacceptable Use

The following uses are strictly forbidden and will get you banned:

- Auto-complete search This is not yet supported by Nominatim and you must not implement such a service on the client side using the API.
- Systematic queries This includes reverse queries in a grid, searching for complete lists of postcodes, towns etc. and downloading all POIs in an area. If you need complete sets of data, get it from the OSM planet or an extract.
- Scraping of details The details page is there for debugging only and may not be downloaded automatically.

### Privacy

- Use of all services is subject to the OpenStreetMap Foundation privacy policy. Please do not submit personal data or other confidential material to any of our services.

### Changes to this Policy

- Please be aware that this usage policy may change without notice. In particular, the definition of heavy use may need to be modified in the future and you might have your access withdrawn. Commercial applications should keep that in mind when relying on this API for serving paying customers.

### Alternatives / Third-party providers

- For slightly larger requirements you may be able to use commercial third-party providers. Some are listed on the Nominatim wiki page.
- If your requirements are even larger you can install your own instance of Nominatim.
