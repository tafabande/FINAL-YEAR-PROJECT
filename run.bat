@echo off
echo Starting TrackerPro via Docker Compose...
docker-compose up --build -d
echo.
echo TrackerPro Services Started!
echo Open http://localhost:5000 in your browser to view the dashboard.
pause
