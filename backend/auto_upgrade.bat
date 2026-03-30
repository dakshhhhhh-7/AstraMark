@echo off
echo ========================================
echo AstraMark - Automated Python 3.12 Upgrade
echo ========================================
echo.

REM Check if Python 3.12 is installed
echo Checking for Python 3.12...
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python 3.12 not found!
    echo.
    echo Please install Python 3.12 first:
    echo 1. Go to: https://www.python.org/downloads/
    echo 2. Download Python 3.12.x
    echo 3. Run installer and CHECK "Add to PATH"
    echo 4. Close this window and run this script again
    echo.
    pause
    exit /b 1
)

py -3.12 --version
echo Python 3.12 found!
echo.

REM Deactivate current venv if active
echo Deactivating current virtual environment...
call deactivate 2>nul

REM Backup old venv
echo.
echo Backing up old virtual environment...
if exist venv_python310_backup (
    echo Removing old backup...
    rmdir /s /q venv_python310_backup
)
if exist venv (
    echo Moving venv to venv_python310_backup...
    move venv venv_python310_backup >nul
)

REM Create new venv with Python 3.12
echo.
echo Creating new virtual environment with Python 3.12...
py -3.12 -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate new venv
echo.
echo Activating new virtual environment...
call venv\Scripts\activate.bat

REM Verify Python version
echo.
echo Verifying Python version in venv...
python --version

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo.
echo Installing dependencies (this may take 2-3 minutes)...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Trying again with verbose output...
    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Test MongoDB connection
echo.
echo ========================================
echo Testing MongoDB Connection...
echo ========================================
python test_connection.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Upgrade Complete!
    echo ========================================
    echo.
    echo Python 3.12 is now active in your venv
    echo MongoDB connection is working
    echo.
    echo To start the server, run:
    echo   python run_server.py
    echo.
    echo Old venv backed up to: venv_python310_backup
    echo You can delete it after confirming everything works.
    echo.
) else (
    echo.
    echo ========================================
    echo Upgrade completed but MongoDB test failed
    echo ========================================
    echo.
    echo Please check:
    echo 1. Internet connection
    echo 2. MongoDB Atlas cluster is running
    echo 3. Firewall settings
    echo.
)

pause
