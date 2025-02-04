from typing import List, Dict, Any, Optional
from .rapid_api_client import JobSearchClient

class RadiologyJobSearch:
    """Specialized job search class for radiology and medical imaging positions."""
    
    def __init__(self):
        self.client = JobSearchClient()
        self.job_types = {
            "cat_scan": ["CT Technologist", "CAT Scan Technician", "CT Tech"],
            "mri": ["MRI Technologist", "MRI Tech", "Magnetic Resonance Imaging"],
            "radiology": ["Radiologist", "Radiology Technician", "X-Ray Tech", "Radiologic Technologist"],
            "ultrasound": ["Sonographer", "Ultrasound Technician", "Ultrasound Tech"],
            "nuclear_medicine": ["Nuclear Medicine Technologist", "Nuclear Med Tech"]
        }

    def search_by_modality(self, 
                          modality: str,
                          location: str = "",
                          page: int = 1,
                          num_pages: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        Search for jobs by specific radiology modality.
        
        Args:
            modality (str): Type of radiology job ("cat_scan", "mri", "radiology", "ultrasound", "nuclear_medicine")
            location (str): Location for the search (e.g. "Chicago, IL")
            page (int): Page number to fetch
            num_pages (int): Number of pages to fetch
            
        Returns:
            List of jobs matching the criteria, or None if the request failed
        """
        if modality not in self.job_types:
            raise ValueError(f"Invalid modality. Must be one of: {list(self.job_types.keys())}")

        # Get search terms for the modality
        search_terms = self.job_types[modality]
        all_results = []

        # Search for each term
        for term in search_terms:
            query = f"{term} {location}".strip()
            results = self.client.search_jobs(
                query=query,
                page=page,
                num_pages=num_pages
            )
            
            if results and "data" in results:
                all_results.extend(results["data"])

        return all_results if all_results else None

    def search_all_modalities(self, 
                            location: str = "",
                            page: int = 1,
                            num_pages: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for all types of radiology jobs.
        
        Args:
            location (str): Location for the search (e.g. "Chicago, IL")
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
                      employment_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filter job results based on criteria.
        
        Args:
            jobs: List of job dictionaries to filter
            min_salary: Minimum salary requirement
            employment_type: Type of employment (e.g. "FULLTIME", "PARTTIME")
            
        Returns:
            Filtered list of jobs
        """
        filtered_jobs = jobs.copy()
        
        if min_salary:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.get("job_min_salary") and float(job["job_min_salary"]) >= min_salary
            ]
            
        if employment_type:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.get("job_employment_type") == employment_type.upper()
            ]
            
        return filtered_jobs 