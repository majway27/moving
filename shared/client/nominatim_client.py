from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

class RateLimitedNominatim:
    def __init__(self, user_agent, min_delay_seconds=1):
        self.geocoder = Nominatim(user_agent=user_agent)
        self.min_delay_seconds = min_delay_seconds
        self.last_request_time = 0

    def geocode(self, location_string, exactly_one=True):
        # Ensure minimum delay between requests
        time_since_last_request = time.time() - self.last_request_time
        if time_since_last_request < self.min_delay_seconds:
            time.sleep(self.min_delay_seconds - time_since_last_request)
        
        try:
            result = self.geocoder.geocode(location_string, exactly_one=exactly_one)
            self.last_request_time = time.time()
            return result
        except GeocoderTimedOut:
            print(f"Timeout while geocoding {location_string}")
            return None 