#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run prep script to reset map.html
python prep_map.py

# Run the house import script
python house_import.py

# Deactivate virtual environment
deactivate 