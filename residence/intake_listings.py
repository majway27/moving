from typing import List, Dict, Any, Optional
from client.rapid_api_client import ZillowClient
import json
import os
import csv
import datetime
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

class ResidenceSearch:
    """Specialized search class for residential properties."""
    
    def __init__(self):
        self.client = ZillowClient()
        self.output_dir = {
            "own": "own/own_results",
            "rent": "rent/rent_results"
        }
        self.modalities = {
            "own": "sale",
            "rent": "rent"
        }
        # Create output directories if they don't exist
        for dir_path in self.output_dir.values():
            os.makedirs(dir_path, exist_ok=True)

    def _generate_csv_filename(self, modality: str, location: str) -> str:
        """Generate a filename for the CSV based on modality and location."""
        safe_location = location.replace(",", "").replace(" ", "_").lower() if location else "all"
        return os.path.join(self.output_dir[modality], f"{safe_location}-{self.modalities[modality].capitalize()}.csv")

    def _generate_filtered_csv_filename(self, original_filename: str) -> str:
        """Generate a filename for filtered results CSV."""
        base, ext = os.path.splitext(original_filename)
        return f"{base}_filtered{ext}"

    def _save_to_csv(self, results: List[Dict[str, Any]], modality: str, location: str, filename: Optional[str] = None) -> None:
        """Save search results to CSV file."""
        if not results:
            print(f"No results to save for {location}")
            return

        output_file = filename or self._generate_csv_filename(modality, location)
        
        # Get all possible fields from all results
        fieldnames = set()
        for result in results:
            fieldnames.update(result.keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Saved {len(results)} results to {output_file}")

    def search_by_location(self, 
                          modality: str,
                          location: str,
                          max_price: Optional[int] = None,
                          min_price: Optional[int] = None,
                          page: int = 1,
                          num_pages: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        Search for properties by location with retry logic.
        
        Args:
            modality: "own" or "rent"
            location: City and state (e.g., "Denver, CO")
            max_price: Maximum price filter
            min_price: Minimum price filter
            page: Starting page number
            num_pages: Number of pages to retrieve
        """
        if modality not in self.modalities:
            raise ValueError(f"Invalid modality. Must be one of: {list(self.modalities.keys())}")

        all_results = []
        max_retries = 3

        for attempt in range(max_retries):
            try:
                results = self.client.search_properties(
                    location=location,
                    property_type=self.modalities[modality],
                    max_price=max_price,
                    min_price=min_price,
                    page=page,
                    num_pages=num_pages
                )
                
                if results and "data" in results:
                    all_results.extend(results["data"])
                break  # Success - exit retry loop
                
            except Exception as e:
                wait_time = (2 ** attempt)  # Exponential backoff: 1, 2, 4 seconds
                
                if attempt < max_retries - 1:  # Don't log on last attempt
                    error_type = str(e)
                    if "429" in error_type:
                        print(f"Rate limit exceeded. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    elif "500" in error_type:
                        print(f"Server error. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    else:
                        print(f"Error: {e}. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")

        if all_results:
            # Save raw results
            self._save_to_csv(all_results, modality, location)
            
            # Apply filters and save filtered results
            filtered_results = self.filter_results(all_results, modality)
            if filtered_results:
                filtered_filename = self._generate_filtered_csv_filename(
                    self._generate_csv_filename(modality, location)
                )
                self._save_to_csv(filtered_results, modality, location, filename=filtered_filename)
            
            return filtered_results
        
        return None

    def filter_results(self, 
                      results: List[Dict[str, Any]], 
                      modality: str,
                      exclude_pending: bool = True,
                      exclude_new_construction: bool = False) -> List[Dict[str, Any]]:
        """
        Filter results based on various criteria.
        
        Args:
            results: List of property results to filter
            modality: "own" or "rent"
            exclude_pending: Remove pending sales/applications
            exclude_new_construction: Remove new construction properties
        """
        if not results:
            return []

        original_count = len(results)
        filtered_results = results.copy()

        # Remove pending listings if requested
        if exclude_pending:
            before_count = len(filtered_results)
            filtered_results = [
                result for result in filtered_results
                if not any(status.lower() in str(result.get("status", "")).lower() 
                          for status in ["pending", "application pending", "under contract"])
            ]
            print(f"Pending filter removed {before_count - len(filtered_results)} listings")

        # Remove new construction if requested
        if exclude_new_construction:
            before_count = len(filtered_results)
            filtered_results = [
                result for result in filtered_results
                if not result.get("new_construction", False)
            ]
            print(f"New construction filter removed {before_count - len(filtered_results)} listings")

        print(f"Total: Started with {original_count} listings, ended with {len(filtered_results)} listings")
        
        return filtered_results 