#!/bin/bash
set -e

# Load environment variables
source .env

# Set up Python environment
python3 -m venv venv
. venv/bin/activate
python -m pip install --upgrade pip
# pip install pytest
pip install -r requirements.txt

# # Run tests
# pytest ./app/tests/test_analysis_controller.py -v