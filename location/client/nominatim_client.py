from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from functools import lru_cache
import time

class RateLimitedNominatim:
    def __init__(self, user_agent, cache_size=1024):
        """
        Initialize the rate-limited Nominatim client
        
        Args:
            user_agent (str): User agent string identifying your application
            cache_size (int): Number of results to cache (default 1024)
        """
        self.geocoder = Nominatim(user_agent=user_agent)
        self.last_request_time = 0
        self._enforce_rate_limit()
        
        # Create cached versions of geocode and reverse methods
        self.geocode = lru_cache(maxsize=cache_size)(self._geocode)
        self.reverse_geocode = lru_cache(maxsize=cache_size)(self._reverse_geocode)

    def _enforce_rate_limit(self):
        """Ensure at least 1 second between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < 1.0:
            time.sleep(1.0 - time_since_last_request)
            
        self.last_request_time = time.time()

    def _geocode(self, address, exactly_one=True):
        """
        Geocode an address to (latitude, longitude)
        
        Args:
            address (str): Address to geocode
            exactly_one (bool): Return only the first result if True
            
        Returns:
            Location object or None if not found
        """
        self._enforce_rate_limit()
        try:
            location = self.geocoder.geocode(address, exactly_one=exactly_one)
            if location:
                return location
            return None
        except GeocoderTimedOut:
            return None

    def _reverse_geocode(self, latitude, longitude, exactly_one=True):
        """
        Reverse geocode coordinates to address
        
        Args:
            latitude (float): Latitude
            longitude (float): Longitude
            exactly_one (bool): Return only the first result if True
            
        Returns:
            Location object or None if not found
        """
        self._enforce_rate_limit()
        try:
            location = self.geocoder.reverse((latitude, longitude), exactly_one=exactly_one)
            if location:
                return location
            return None
        except GeocoderTimedOut:
            return None

    def clear_cache(self):
        """Clear the geocoding caches"""
        self.geocode.cache_clear()
        self.reverse_geocode.cache_clear() 