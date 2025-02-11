# job

## Job Module

### Functional Description

- This module is a pipeline; used to search for jobs in the healthcare industry. 
- It uses the JSearch API to search for jobs and then formats the results into a table.

### Technical Design (by layer)

1. *Client*  `job/client/rapid_api_client.py`
    - This is the client for the JSearch API. It is the entry point for multi-source postings.
    - Additional clients could be defined here.
2. *Intake*  `job/intake_postings.py` - The responsibility of this file is:
    - Abstract and wrap 1+ API clients (JSearch, etc.)
    - Specify key search parameters (modality, location, etc.)
    - Bucket results by modality (CT, MR, etc.) and location (Denver, Phoenix, etc.)
    - Coarsely filter client responses
    - Output both a raw and a filtered result set as csv files in the job_results subdirectory (mode: overwrite) `job/job_results/`
    - Maintain a list of employers in `employer/employers.json`
3. *Transform*  `job/format_postings.py` - The responsibility of this file is:
    - Load posting data from filtered csv files
    - Eliminate duplicate postings by comparing key fields (job title, employer, location, and description)
    - Remove redundant job listings that represent the same position
    - For each filtered csv, output similarly named json file  in the job_results subdirectory (mode: overwrite) `job/job_results/`
    - Finally, combine all json files into a single consolidated json file `job/job_data.json` (which is expected by the view layer)
4. *View*  `job/job.html` - The responsibility of this file is:
    - This is the end user view of the enhanced (filtered and formated) posting data.
    - This html file is not directly altered by the pipeline, rather it expects a consolidated json file (`job/job_data.json`)
5. *Control* - `job/runner-job.py` - The responsibility of this file is:
    - Execution & pipeline management logic
    - Abstract surface for overarching orchestration
    - Set the last-refreshed timestamp in `index.html` via `shared/utility.py`

### TODO

1. ?

### Roadmap

- ?

