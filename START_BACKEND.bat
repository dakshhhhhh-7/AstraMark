@echo off
echo ========================================
echo    STARTING ASTRAMARK BACKEND SERVER
echo ========================================
echo.

cd /d "%~dp0backend"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting server on http://localhost:8001
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn server_enhanced:app --reload --port 8001

pause
