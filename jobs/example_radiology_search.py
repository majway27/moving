from healthcare_jobs import RadiologyJobSearch

def main():
    # Create radiology job search instance
    job_search = RadiologyJobSearch()
    
    # Example 1: Search for MRI jobs in Chicago
    print("Searching for MRI jobs in Chicago...")
    mri_jobs = job_search.search_by_modality(
        modality="mri",
        location="Chicago, IL"
    )
    
    if mri_jobs:
        print(f"\nFound {len(mri_jobs)} MRI jobs:")
        for job in mri_jobs:
            print("\n---")
            print(f"Title: {job['job_title']}")
            print(f"Company: {job['employer_name']}")
            print(f"Location: {job['job_city']}, {job['job_state']}")
            print(f"Link: {job['job_apply_link']}")
    
    # Example 2: Search all radiology jobs in Boston
    print("\nSearching all radiology modalities in Boston...")
    all_jobs = job_search.search_all_modalities(
        location="Boston, MA"
    )
    
    for modality, jobs in all_jobs.items():
        if jobs:
            print(f"\n=== {modality.upper()} Jobs ===")
            print(f"Found {len(jobs)} jobs")
            
            # Filter for full-time jobs only
            filtered_jobs = job_search.filter_results(
                jobs=jobs,
                employment_type="FULLTIME"
            )
            
            for job in filtered_jobs[:3]:  # Show first 3 jobs
                print("\n---")
                print(f"Title: {job['job_title']}")
                print(f"Company: {job['employer_name']}")
                print(f"Location: {job['job_city']}, {job['job_state']}")

if __name__ == "__main__":
    main() 