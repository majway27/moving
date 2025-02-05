from healthcare_jobs import ImagingJobSearch
from generate_jobs_page import generate_jobs_data
import json
from pathlib import Path
from datetime import datetime

def save_filtered_jobs(filtered_jobs, modality, location):
    """Save filtered jobs in the format expected by generate_jobs_page.py"""
    jobs_to_save = []
    for job in filtered_jobs:
        formatted_job = {
            'title': job.get('job_title', 'N/A'),
            'company': job.get('employer_name', 'N/A'),
            'location': f"{job.get('job_city', '')}, {job.get('job_state', '')}",
            'date_posted': job.get('job_posted_at_datetime_utc', ''),
            'description': job.get('job_description', ''),
            'url': job.get('job_apply_link', '#')
        }
        jobs_to_save.append(formatted_job)
    
    # Save to a JSON file in job_results directory
    output_dir = Path('job_results')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{modality.lower()}_{location.replace(', ', '_').lower()}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(jobs_to_save, f, ensure_ascii=False, indent=2)

def main():
    # Create radiology job search instance
    job_search = ImagingJobSearch()
    
    '''
    # Example 1: Search for MRI jobs in Denver
    print(f"Searching for MRI jobs in Denver...")
    mri_jobs = job_search.search_by_modality(
        modality="mri",
        location="Denver, CO"
    )
    
    if mri_jobs:
        # Filter out travel, contract, and PRN positions
        filtered_mri_jobs = job_search.filter_results(
            jobs=mri_jobs,
            exclude_travel=True,
            exclude_contract=True,
            exclude_prn=True
        )
        print(f"\nFound {len(filtered_mri_jobs)} permanent MRI jobs:")
        for job in filtered_mri_jobs:
            print("\n---")
            print(f"Title: {job['job_title']}")
            print(f"Company: {job['employer_name']}")
            print(f"Location: {job['job_city']}, {job['job_state']}")
            print(f"Link: {job['job_apply_link']}")
    
    '''
    
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