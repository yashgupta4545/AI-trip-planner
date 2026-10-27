@echo off
title TripGenie AI - Automated Setup and Launch
echo ========================================================
echo Setting up TripGenie AI on a new environment...
echo ========================================================

echo Step 1: Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt

echo.
echo Step 2: Validating datasets...
python scripts/validate_dataset.py

echo.
echo Step 3: Launching application...
python -m streamlit run app.py

pause
