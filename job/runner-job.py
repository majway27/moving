from typing import Dict, List
from intake_postings import ImagingJobSearch
from format_postings import generate_jobs_data, save_filtered_jobs
from pathlib import Path
from datetime import datetime
from location.location import load_locations, format_location

def process_jobs_for_location(
    job_search: ImagingJobSearch,
    location: str,
    location_key: str
) -> None:
    """
    Process and save jobs for a specific location.
    
    Args:
        job_search: ImagingJobSearch instance to use for searching
        location: Formatted location string for searching
        location_key: Key used for saving filtered jobs
    """
    print(f"\nSearching all imaging modalities in {location}...")
    all_jobs = job_search.search_all_modalities(location=location)
    
    for modality, jobs in all_jobs.items():
        if not jobs:
            continue
            
        print(f"\n=== {modality.upper()} Jobs in {location} ===")
        print(f"Found {len(jobs)} total jobs")
        
        filtered_jobs = job_search.filter_results(
            jobs=jobs,
            employment_type="FULLTIME",
            exclude_travel=True,
            exclude_contract=True,
            exclude_prn=True,
            modality=modality,
            location=location
        )
        
        print(f"Found {len(filtered_jobs)} permanent full-time positions")
        save_filtered_jobs(filtered_jobs, modality, location_key)
        
        display_sample_jobs(filtered_jobs)

def display_sample_jobs(jobs: List[Dict], sample_size: int = 3) -> None:
    """
    Display a sample of jobs with basic information.
    
    Args:
        jobs: List of job dictionaries
        sample_size: Number of jobs to display
    """
    for job in jobs[:sample_size]:
        print("\n---")
        print(f"Title: {job['job_title']}")
        print(f"Company: {job['employer_name']}")
        print(f"Location: {job['job_city']}, {job['job_state']}")

def main() -> None:
    """Main function to process jobs for all configured locations."""
    job_search = ImagingJobSearch()
    metro_areas = load_locations()
    
    for metro in metro_areas:
        # Process hub city
        hub = metro["hub_city"]
        hub_location = format_location(hub["name"], hub["state"])
        hub_location_key = f"{hub['name']}_{hub['state']}"
        process_jobs_for_location(job_search, hub_location, hub_location_key)
        
        # Process suburbs
        for suburb in metro["suburbs"]:
            suburb_location = format_location(suburb["name"], suburb["state"])
            suburb_location_key = f"{suburb['name']}_{suburb['state']}"
            process_jobs_for_location(job_search, suburb_location, suburb_location_key)

    print("\nGenerating jobs formatted data...")
    generate_jobs_data()

if __name__ == "__main__":
    main() 