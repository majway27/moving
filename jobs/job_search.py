from healthcare_jobs import ImagingJobSearch

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
            for job in filtered_jobs[:3]:  # Show first 3 jobs
                print("\n---")
                print(f"Title: {job['job_title']}")
                print(f"Company: {job['employer_name']}")
                print(f"Location: {job['job_city']}, {job['job_state']}")

if __name__ == "__main__":
    main() 