@echo off
echo ========================================
echo    STARTING ASTRAMARK FRONTEND
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Starting React development server...
echo This will open your browser automatically
echo Press Ctrl+C to stop the server
echo.

npm start

pause
