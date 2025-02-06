import json
from pathlib import Path
from typing import Set

def load_employers() -> Set[str]:
    """Load existing employers from JSON file or create empty set if file doesn't exist."""
    employer_path = Path(__file__).parent / "employers.json"
    try:
        with open(employer_path, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_employers(employers: Set[str]) -> None:
    """Save employers set to JSON file."""
    employer_path = Path(__file__).parent / "employers.json"
    with open(employer_path, 'w') as f:
        json.dump(list(employers), f, indent=2)

def update_employers(jobs: list) -> None:
    """Update employers set with new companies from job results."""
    employers = load_employers()
    for job in jobs:
        if company := job.get('employer_name'):
            employers.add(company)
    save_employers(employers) 