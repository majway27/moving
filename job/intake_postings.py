import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import os
import csv
import datetime

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from job.client.rapid_api_client import JobSearchClient
from employer.employer import (
    update_employers, 
    load_excluded_employers,
    load_employer_map,
    normalize_employer_name,
    remap_employer_name
)
from location.location import get_state_from_location

class ImagingJobSearch:
    """Specialized job search class for medical imaging positions."""
    
    def __init__(self):
        self.client = JobSearchClient()
        self.output_dir = "job_results"
        self.job_types = {
            "cat_scan": ["CT Technologist", "CAT Scan Technician", "CT Tech"],
            "mri": ["MRI Technologist", "MRI Tech", "Magnetic Resonance Imaging"],
            #"radiology": ["Radiologist", "Radiology Technician", "X-Ray Tech", "Radiologic Technologist"],
            #"ultrasound": ["Sonographer", "Ultrasound Technician", "Ultrasound Tech"],
            #"nuclear_medicine": ["Nuclear Medicine Technologist", "Nuclear Med Tech"]
        }
        self.max_retries = 3
        self.excluded_employers = load_excluded_employers()
        self.employer_map = load_employer_map()
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_csv_filename(self, modality: str, location: str) -> str:
        """Generate a filename for the CSV based on modality and location."""
        safe_location = location.replace(",", "").replace(" ", "_").lower() if location else "all"
        return os.path.join(self.output_dir, f"{modality}_{safe_location}_jobs.csv")

    def _generate_filtered_csv_filename(self, original_filename: str) -> str:
        """Generate a filename for filtered results CSV."""
        base, ext = os.path.splitext(original_filename)
        return f"{base}_filtered{ext}"

    def _save_to_csv(self, 
                     jobs: List[Dict[str, Any]], 
                     modality: str, 
                     location: str,
                     filename: Optional[str] = None) -> None:
        """Save job results to a CSV file."""
        if not jobs:
            return

        if filename is None:
            filename = self._generate_csv_filename(modality, location)
        
        # Define the fields we want to include in the CSV
        fields = [
            'employer_name',
            'job_title',
            'job_city',
            'job_state',
            'job_min_salary',
            'job_max_salary',
            'job_employment_type',
            'job_apply_link',
            'job_posted_at_datetime_utc'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for job in jobs:
                row = {field: job.get(field, '') for field in fields}
                writer.writerow(row)

    def search_by_modality(self, 
                          modality: str,
                          location: str = "",
                          page: int = 1,
                          num_pages: int = 1) -> Optional[List[Dict[str, Any]]]:
        """Search for jobs by specific imaging modality with retry logic."""
        if modality not in self.job_types:
            raise ValueError(f"Invalid modality. Must be one of: {list(self.job_types.keys())}")

        search_terms = self.job_types[modality]
        all_results = []

        for term in search_terms:
            query = f"{term} {location}".strip()
            
            # Add retry logic
            for attempt in range(self.max_retries):
                try:
                    results = self.client.search_jobs(
                        query=query,
                        page=page,
                        num_pages=num_pages
                    )
                    
                    if results and "data" in results:
                        # Process each job to ensure location is properly set
                        for job in results["data"]:
                            if job_state := job.get('job_state'):
                                # Set the location field for employer tracking
                                job['location'] = job_state
                            elif location:
                                # If no job_state but location was provided in search
                                job['location'] = get_state_from_location(location)
                            
                        all_results.extend(results["data"])
                    break  # Success - exit retry loop
                    
                except Exception as e:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1, 2, 4 seconds
                    
                    if attempt < self.max_retries - 1:  # Don't log on last attempt
                        error_type = str(e)
                        if "429" in error_type:
                            print(f"Rate limit exceeded. Waiting {wait_time} seconds before retry {attempt + 1}/{self.max_retries}")
                        elif "500" in error_type:
                            print(f"Server error. Waiting {wait_time} seconds before retry {attempt + 1}/{self.max_retries}")
                        else:
                            print(f"Error occurred: {error_type}. Waiting {wait_time} seconds before retry {attempt + 1}/{self.max_retries}")
                        
                        import time
                        time.sleep(wait_time)
                    else:
                        print(f"Failed after {self.max_retries} attempts for query: {query}")
                        continue  # Move to next search term

        if all_results:
            # Remap employer names before saving
            for job in all_results:
                if employer_name := job.get('employer_name'):
                    job['employer_name'] = remap_employer_name(employer_name, self.employer_map)
            
            # Only update employers if we have location information
            update_employers(all_results)
            self._save_to_csv(all_results, modality, location)
            
        return all_results if all_results else None

    def search_all_modalities(self, 
                            location: str = "",
                            page: int = 1,
                            num_pages: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for all types of imaging jobs.
        
        Args:
            location (str): Location for the search (e.g. "Denver, CO")
            page (int): Page number to fetch
            num_pages (int): Number of pages to fetch
            
        Returns:
            Dictionary with modality as key and list of jobs as value
        """
        results = {}
        
        for modality in self.job_types.keys():
            jobs = self.search_by_modality(
                modality=modality,
                location=location,
                page=page,
                num_pages=num_pages
            )
            results[modality] = jobs if jobs else []
            
        return results

    def filter_results(self, 
                      jobs: List[Dict[str, Any]], 
                      min_salary: Optional[float] = None,
                      employment_type: Optional[str] = None,
                      exclude_prn: bool = False,
                      exclude_travel: bool = False,
                      exclude_contract: bool = False,
                      modality: Optional[str] = None,
                      location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filter job results based on criteria.
        
        Args:
            jobs: List of job dictionaries to filter
            min_salary: Minimum salary requirement
            employment_type: Type of employment (e.g. "FULLTIME", "PARTTIME")
            exclude_prn: If True, exclude PRN/per-diem positions
            exclude_travel: If True, exclude travel positions
            exclude_contract: If True, exclude contract/temporary positions
            modality: Type of imaging job (needed for CSV filename)
            location: Location of search (needed for CSV filename)
            
        Returns:
            Filtered list of jobs
        """
        filtered_jobs = jobs.copy()
        original_count = len(filtered_jobs)
        
        # Update employer exclusion filter to use normalized names
        if self.excluded_employers:
            before_count = len(filtered_jobs)
            filtered_jobs = [
                job for job in filtered_jobs
                if normalize_employer_name(job.get("employer_name", "")) not in self.excluded_employers
            ]
            print(f"Excluded employers filter removed {before_count - len(filtered_jobs)} jobs")

        if min_salary:
            before_count = len(filtered_jobs)
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.get("job_min_salary") and float(job["job_min_salary"]) >= min_salary
            ]
            print(f"Salary filter removed {before_count - len(filtered_jobs)} jobs")
            
        if employment_type:
            before_count = len(filtered_jobs)
            # Debug: print unique employment types
            unique_types = set(job.get("job_employment_type", "") for job in filtered_jobs)
            print(f"Found employment types: {unique_types}")
            
            filtered_jobs = [
                job for job in filtered_jobs 
                if str(job.get("job_employment_type", "")).upper() in ["FULLTIME", "FULL_TIME", "FULL-TIME", "FULL-TIME AND PART-TIME"]
            ]
            print(f"Employment type filter removed {before_count - len(filtered_jobs)} jobs")

        if exclude_prn:
            before_count = len(filtered_jobs)
            prn_terms = ["prn", "per diem", "as needed", "pro re nata", "p.r.n.", "perdiem", "per-diem"]
            filtered_jobs = [
                job for job in filtered_jobs
                if not any(term.lower() in str(job.get("job_title", "")).lower() or
                          term.lower() in str(job.get("job_description", "")).lower()
                          for term in prn_terms)
            ]
            print(f"PRN filter removed {before_count - len(filtered_jobs)} jobs")

        if exclude_travel:
            before_count = len(filtered_jobs)
            # Terms that strongly indicate a travel position
            travel_terms = [
                "Job Type Travel",
                "Job Type: Travel",
                "locum position",
                "locum tenens",
                "locums position",
                "required regular travel",
                "travel agencies",
                "travel assignment",
                "travel basis",
                "travel career",
                "travel contract",
                "travel experience",
                "travel experiences",
                "travel healthcare",
                "travel interventional",
                "travel job",
                "travel opportunities",
                "travel opportunity",
                "travel position",
                "travel tech",
                "traveling professional",
                "traveling professionals",
                "traveling tech"
            ]
            # Terms that might indicate a travel position if they appear alone
            basic_travel_terms = [
                "locum",
                "locums",
                "traveler",
                "traveling"
            ]
            
            # Terms that indicate it's NOT a travel position
            non_travel_indicators = [
                "limited travel",
                "minimal travel",
                "no travel",
                "no traveling",
                "travel hub",
                "travel is not",
                "travel not"
            ]
            
            filtered_jobs = [
                job for job in filtered_jobs
                if (
                    # Check if any non-travel indicators are present
                    any(indicator.lower() in str(job.get("job_description", "")).lower() 
                        for indicator in non_travel_indicators)
                    or not (
                        # Original travel position checks
                        any(term.lower() in str(job.get("job_title", "")).lower() or
                            term.lower() in str(job.get("job_description", "")).lower()
                            for term in travel_terms) or
                        any(term.lower() in str(job.get("job_title", "")).lower()
                            for term in basic_travel_terms) or
                        "travel" in str(job.get("job_title", "")).lower()
                    )
                )
            ]
            print(f"Travel filter removed {before_count - len(filtered_jobs)} jobs")

        if exclude_contract:
            before_count = len(filtered_jobs)
            filtered_jobs = [
                job for job in filtered_jobs
                if not any(term.lower() in str(job.get("job_title", "")).lower() 
                          for term in ["contract", "temporary"])
            ]
            print(f"Contract filter removed {before_count - len(filtered_jobs)} jobs")
            
        print(f"Total: Started with {original_count} jobs, ended with {len(filtered_jobs)} jobs")
        
        # Save filtered results to CSV if modality and location are provided
        if modality and location and filtered_jobs:
            original_filename = self._generate_csv_filename(modality, location)
            filtered_filename = self._generate_filtered_csv_filename(original_filename)
            self._save_to_csv(filtered_jobs, modality, location, filename=filtered_filename)
            
        return filtered_jobs
    
    