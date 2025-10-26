@echo off
REM This script is for local development on Windows

echo Starting Lumera backend in development mode...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Starting server...
python app.py