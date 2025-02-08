import requests
import time
from typing import Dict, Any, Optional
import os
from pathlib import Path

# Add project root to Python path to import credentials
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from credentials.credentials import RAPID_API_KEY
except ImportError:
    print("Warning: Failed to import RAPID_API_KEY. Please ensure credentials.py exists.")
    RAPID_API_KEY = os.getenv("RAPID_API_KEY")

class ZillowClient:
    """
    Client for interacting with the Zillow Rapid API.
    
    This client provides methods to search for residential properties
    for both sale and rent through the Zillow API interface.
    
    Attributes:
        base_url (str): The base URL for the Zillow API endpoint
        headers (dict): Headers required for API authentication
    """
    
    def __init__(self):
        if not RAPID_API_KEY:
            raise ValueError("RAPID_API_KEY is required. Set it in credentials.py or as an environment variable.")
            
        self.base_url = "https://zillow56.p.rapidapi.com/search"
        self.headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "zillow56.p.rapidapi.com"
        }

    def search_properties(self,
                         location: str,
                         property_type: str = "sale",  # "sale" or "rent"
                         min_price: Optional[int] = None,
                         max_price: Optional[int] = None,
                         page: int = 1,
                         num_pages: int = 1) -> Dict[str, Any]:
        """
        Search for residential properties using the Zillow API.
        
        Args:
            location: City and state (e.g., "Denver, CO")
            property_type: Type of listing - either "sale" or "rent"
            min_price: Minimum price filter in USD
            max_price: Maximum price filter in USD
            page: Starting page number for pagination
            num_pages: Number of pages to retrieve
            
        Returns:
            Dict containing:
                - data: List of property results
                - total_results: Number of results found
                - pages_retrieved: Number of pages successfully retrieved
                
        Raises:
            ValueError: If property_type is invalid
            Exception: For API-related errors (rate limits, server errors, etc.)
        """
        if property_type.lower() not in ["sale", "rent"]:
            raise ValueError("property_type must be either 'sale' or 'rent'")
            
        all_results = []
        
        for current_page in range(page, page + num_pages):
            querystring = {
                "location": location,
                "page": str(current_page)
            }
            
            # Add optional filters if provided
            if min_price:
                querystring["price_min"] = str(min_price)
            if max_price:
                querystring["price_max"] = str(max_price)
            
            # Add property type filter
            if property_type.lower() == "rent":
                querystring["status_type"] = "ForRent"
            else:  # sale
                querystring["status_type"] = "ForSale"
            
            try:
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=querystring
                )
                response.raise_for_status()
                
                data = response.json()
                if "results" in data:
                    all_results.extend(data["results"])
                
                # Respect API rate limits
                if current_page < page + num_pages - 1:
                    time.sleep(1)  # Basic rate limiting between pages
                    
            except requests.exceptions.RequestException as e:
                if hasattr(e, 'response') and e.response is not None:
                    if e.response.status_code == 429:
                        raise Exception("429: Rate limit exceeded") from e
                    elif e.response.status_code == 500:
                        raise Exception("500: Server error") from e
                raise Exception(f"API request failed: {str(e)}") from e
        
        return {
            "data": all_results,
            "total_results": len(all_results),
            "pages_retrieved": num_pages
        } 