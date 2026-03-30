@echo off
echo Starting AstraMark Backend Server...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start server using venv's Python directly
python -m uvicorn server_enhanced:app --reload --port 8001

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Server failed to start. Check the error above.
    pause
)
