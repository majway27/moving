from intake_postings import ImagingJobSearch
from format_postings import generate_jobs_data, save_filtered_jobs
from pathlib import Path
from datetime import datetime
from location.location import load_locations, format_location

def main():
    # Create radiology job search instance
    job_search = ImagingJobSearch()
    metro_areas = load_locations()
    
    for metro in metro_areas:
        # Process hub city
        hub = metro["hub_city"]
        location = format_location(hub["name"], hub["state"])
        
        print(f"\nSearching all imaging modalities in {location}...")
        all_jobs = job_search.search_all_modalities(location=location)
        
        for modality, jobs in all_jobs.items():
            if jobs:
                print(f"\n=== {modality.upper()} Jobs in {location} ===")
                print(f"Found {len(jobs)} total jobs")
                
                # Filter for full-time permanent positions
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
                
                # Save filtered jobs with location-specific filename
                location_key = f"{hub['name']}_{hub['state']}"
                save_filtered_jobs(filtered_jobs, modality, location_key)
                
                for job in filtered_jobs[:3]:  # Show first 3 jobs
                    print("\n---")
                    print(f"Title: {job['job_title']}")
                    print(f"Company: {job['employer_name']}")
                    print(f"Location: {job['job_city']}, {job['job_state']}")
        
        # Process suburbs
        for suburb in metro["suburbs"]:
            location = format_location(suburb["name"], suburb["state"])
            
            print(f"\nSearching all imaging modalities in {location}...")
            all_jobs = job_search.search_all_modalities(location=location)
            
            for modality, jobs in all_jobs.items():
                if jobs:
                    print(f"\n=== {modality.upper()} Jobs in {location} ===")
                    print(f"Found {len(jobs)} total jobs")
                    
                    # Filter for full-time permanent positions
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
                    
                    # Save filtered jobs with location-specific filename
                    location_key = f"{suburb['name']}_{suburb['state']}"
                    save_filtered_jobs(filtered_jobs, modality, location_key)
                    
                    for job in filtered_jobs[:3]:  # Show first 3 jobs
                        print("\n---")
                        print(f"Title: {job['job_title']}")
                        print(f"Company: {job['employer_name']}")
                        print(f"Location: {job['job_city']}, {job['job_state']}")

    # Generate the jobs webpage after completing all searches
    print("\nGenerating jobs formatted data...")
    generate_jobs_data()

if __name__ == "__main__":
    main() 