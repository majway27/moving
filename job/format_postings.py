import json
import os
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

def load_job_file(job_file):
    """Load and parse a single job file."""
    try:
        with open(job_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error reading {job_file}")
        return []

def format_job(job):
    """Format a single job entry for the table."""
    return {
        'title': job.get('title', 'N/A'),
        'company': job.get('company', 'N/A'),
        'location': job.get('location', 'N/A'),
        'date_posted': job.get('date_posted', ''),
        'description': job.get('description', ''),
        'url': job.get('url', '#')
    }

def is_duplicate_posting(job1, job2, similarity_threshold=0.85):
    """
    Compare two job postings to determine if they are duplicates.
    Returns True if the jobs are likely duplicates, False otherwise.
    """
    # If jobs are from same company and location, do detailed comparison
    if (job1['company'].lower() == job2['company'].lower() and 
        job1['location'].lower() == job2['location'].lower()):
        
        # Compare titles
        title_similarity = SequenceMatcher(None, 
            job1['title'].lower(), 
            job2['title'].lower()
        ).ratio()
        
        # Compare descriptions, but only if titles are similar
        if title_similarity > similarity_threshold:
            desc_similarity = SequenceMatcher(None, 
                job1['description'].lower(), 
                job2['description'].lower()
            ).ratio()
            
            # Consider jobs duplicate if both title and description are very similar
            return desc_similarity > similarity_threshold
    
    return False

def remove_duplicates(jobs):
    """Remove duplicate job postings from a list of jobs."""
    unique_jobs = []
    
    for job in jobs:
        # Check if this job is a duplicate of any job we've already kept
        is_duplicate = any(
            is_duplicate_posting(job, existing_job) 
            for existing_job in unique_jobs
        )
        
        if not is_duplicate:
            unique_jobs.append(job)
    
    return unique_jobs

def generate_jobs_data():
    """Generate consolidated jobs data JSON file."""
    # Get the current script's directory
    current_dir = Path(__file__).parent
    
    # Define paths relative to the script location
    jobs_dir = current_dir / 'job_results'
    output_file = current_dir / 'job_data.json'
    
    # Ensure the job_results directory exists
    if not jobs_dir.exists():
        print(f"Creating job results directory at {jobs_dir}")
        jobs_dir.mkdir(parents=True, exist_ok=True)
        return
    
    # Process all job files
    all_jobs = []
    for job_file in jobs_dir.glob('*.json'):
        job_data = load_job_file(job_file)
        formatted_jobs = [format_job(job) for job in job_data]
        all_jobs.extend(formatted_jobs)

    # Remove duplicates before sorting
    unique_jobs = remove_duplicates(all_jobs)
    print(f"Removed {len(all_jobs) - len(unique_jobs)} duplicate postings")

    # Sort jobs by date (newest first), handling missing dates
    unique_jobs.sort(
        key=lambda x: x.get('date_posted', '') or '',  # Use empty string if date is None
        reverse=True
    )
    
    # Write the combined job data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
    
    print(f"Generated job data file with {len(unique_jobs)} jobs at {output_file}")

def save_filtered_jobs(filtered_jobs, modality, location):
    """Save filtered jobs to a JSON file in the job_results directory"""
    jobs_to_save = []
    for job in filtered_jobs:
        # Ensure we have a valid date, default to empty string if missing
        date_posted = job.get('job_posted_at_datetime_utc', '')
        if not date_posted:
            date_posted = datetime.now().isoformat()
            
        formatted_job = {
            'title': job.get('job_title', 'N/A'),
            'company': job.get('employer_name', 'N/A'),
            'location': f"{job.get('job_city', '')}, {job.get('job_state', '')}",
            'date_posted': date_posted,
            'description': job.get('job_description', ''),
            'url': job.get('job_apply_link', '#')
        }
        jobs_to_save.append(formatted_job)
    
    # Remove duplicates before saving
    unique_jobs = remove_duplicates(jobs_to_save)
    print(f"Removed {len(jobs_to_save) - len(unique_jobs)} duplicate postings for {modality} in {location}")
    
    # Save to a JSON file in job_results directory
    output_dir = Path('job_results')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{modality.lower()}_{location.replace(', ', '_').lower()}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_jobs, f, ensure_ascii=False, indent=2)
