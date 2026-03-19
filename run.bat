@echo off
echo Starting Asset Tracker Pro...
start cmd /k "python backend\app.py"
timeout /t 3
echo Starting Mock Telemetry Generator...
start cmd /k "python backend\mock_telemetry.py"
echo Done! Open http://127.0.0.1:5000 in your browser to view the dashboard.
