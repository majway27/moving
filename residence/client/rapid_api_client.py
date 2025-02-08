import requests
from typing import Dict, Any, Optional
from credentials.credentials import RAPID_API_KEY

class JobSearchClient:
    """Client for interacting with the JSearch RapidAPI."""
    
    def __init__(self):
        self.base_url = "https://zillow56.p.rapidapi.com/"
        self.headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "zillow56.p.rapidapi.com"
        }

    