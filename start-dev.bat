@echo off
echo ======================================
echo    Splitwise Development Server
echo ======================================
echo.
echo Starting Backend and Frontend...
echo.
echo 1. Backend will start on http://localhost:5000
echo 2. Frontend will start on http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start backend in new window
start "Splitwise Backend" cmd /k ".venv\Scripts\activate && flask run"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
start "Splitwise Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting in separate windows...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
pause