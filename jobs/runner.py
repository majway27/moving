from intake_postings import ImagingJobSearch
from format_postings import generate_jobs_data, save_filtered_jobs
import json
from pathlib import Path
from datetime import datetime

def main():
    # Create radiology job search instance
    job_search = ImagingJobSearch()
    
    # Example 2: Search all Imaging jobs in Denver
    print("\nSearching all imaging modalities in Denver...")
    all_jobs = job_search.search_all_modalities(
        location="Denver, CO"
    )
    
    for modality, jobs in all_jobs.items():
        if jobs:
            print(f"\n=== {modality.upper()} Jobs ===")
            print(f"Found {len(jobs)} total jobs")
            
            # Filter for full-time permanent positions
            filtered_jobs = job_search.filter_results(
                jobs=jobs,
                employment_type="FULLTIME",
                exclude_travel=True,
                exclude_contract=True,
                exclude_prn=True,
                modality=modality,
                location="Denver, CO"
            )
            
            print(f"Found {len(filtered_jobs)} permanent full-time positions")
            
            # Save filtered jobs in the format expected by generate_jobs_page.py
            save_filtered_jobs(filtered_jobs, modality, "Denver_CO")
            
            for job in filtered_jobs[:3]:  # Show first 3 jobs
                print("\n---")
                print(f"Title: {job['job_title']}")
                print(f"Company: {job['employer_name']}")
                print(f"Location: {job['job_city']}, {job['job_state']}")

    # Generate the jobs webpage after completing the search
    print("\nGenerating jobs webpage...")
    generate_jobs_data()

if __name__ == "__main__":
    main() 