from jobs.client.rapid_api_client import JobSearchClient

def main():
    # Create client instance
    client = JobSearchClient()
    
    # Example search
    results = client.search_jobs(
        query="software developer in Chicago",
        page=1,
        num_pages=1
    )
    
    if results:
        # Print number of jobs found
        if "data" in results:
            jobs = results["data"]
            print(f"Found {len(jobs)} jobs")
            
            # Print basic info for each job
            for job in jobs:
                print("\n---")
                print(f"Title: {job['job_title']}")
                print(f"Company: {job['employer_name']}")
                print(f"Location: {job['job_city']}, {job['job_state']}")
                print(f"Link: {job['job_apply_link']}")
    else:
        print("No results found")

if __name__ == "__main__":
    main() 