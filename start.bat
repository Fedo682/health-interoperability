@echo off
echo Starting Health Interoperability Demo...
echo.

cd /d "%~dp0"

if not exist "data\gp_clinic.db" (
    echo Seeding databases...
    python data\seed_data.py
    echo.
)

echo Opening browser...
start "" http://localhost:5000

echo Starting Flask server...
python app\app.py
