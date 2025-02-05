# jobs

## Jobs Module

### Functional Description

- This module is a pipeline; used to search for jobs in the healthcare industry. 
- It uses the JSearch API to search for jobs and then formats the results into a table.

### Technical Design

1. **Client**  `jobs/client/rapid_api_client.py`
    - This is the client for the JSearch API. It is the entry point for multi-source postings.
    - Additional clients could be defined here.
2. **Intake**  `jobsintake_postings.py` - The responsibility of this file is:
    - Abstract and wrap 1+ API clients (JSearch, etc.)
    - Specify key search parameters (modality, location, etc.)
    - Bucket results by modality (CT, MR, etc.) and location (Denver, Phoenix, etc.)
    - Coarsely filter client responses
    - Output both a raw and a filtered result set as csv files in the job_results subdirectory (mode: overwrite) `jobs/jobs_results/`
    - Maintain a list of employers in `employer/employers.json`
3. **Transform**  `jobs/format_postings.py` - The responsibility of this file is:
    - Load posting data from filtered csv files 
    - Output the table as an html file in the jobs subdirectory (mode: overwrite)
4. **View**  `jobs/jobs.html` - The responsibility of this file is:
    - This is the end user view of the enhanced (filtered and formated) posting data.
    - This html file is not directly altered by the pipeline, rather it expects a consolidated json file (`jobs/job_data.json`)
5. **Control** - runner.py - The responsibility of this file is:
    - Execution & pipeline management logic
    - Abstract surface for overarching orchestration

### TODO

1. ?

### Roadmap

- ?

