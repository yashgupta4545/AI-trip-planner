@echo off
title TripGenie AI - Travel Planning Platform
echo ========================================================
echo Launching TripGenie AI Travel Platform...
echo ========================================================

if exist ".venv\Scripts\python.exe" (
    echo Using project virtual environment...
    ".venv\Scripts\python.exe" -m streamlit run app.py
) else (
    echo Using system Python...
    python -m streamlit run app.py
)

pause
