import requests
from typing import Dict, Any, Optional
from credentials.credentials import RAPID_API_KEY

class JobSearchClient:
    """Client for interacting with the JSearch RapidAPI."""
    
    def __init__(self):
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

    def search_jobs(self, 
                   query: str,
                   page: int = 1,
                   num_pages: int = 1,
                   country: str = "US",
                   date_posted: str = "all") -> Optional[Dict[str, Any]]:
        """
        Search for jobs using the JSearch API.

        Args:
            query (str): Search query (e.g. "Python developer in New York")
            page (int): Page number to fetch
            num_pages (int): Number of pages to fetch
            country (str): Country code (e.g. "US")
            date_posted (str): Filter for date posted ("all", "today", "3days", "week", "month")

        Returns:
            Dict containing the API response, or None if the request failed
        """
        querystring = {
            "query": query,
            "page": str(page),
            "num_pages": str(num_pages),
            "country": country.lower(),
            "date_posted": date_posted
        }

        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=querystring
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None 