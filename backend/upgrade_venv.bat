@echo off
echo ========================================
echo Recreating Virtual Environment with Python 3.11+
echo ========================================
echo.

REM Check if Python 3.11+ is available
py -3.12 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py -3.12
    echo Found Python 3.12
    goto :create_venv
)

py -3.11 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py -3.11
    echo Found Python 3.11
    goto :create_venv
)

echo ERROR: Python 3.11 or 3.12 not found!
echo Please install Python 3.11+ first by running: upgrade_python.bat
pause
exit /b 1

:create_venv
echo.
echo Step 1: Backing up current venv folder...
if exist venv_backup rmdir /s /q venv_backup
if exist venv move venv venv_backup

echo.
echo Step 2: Creating new virtual environment with %PYTHON_CMD%...
%PYTHON_CMD% -m venv venv

echo.
echo Step 3: Activating new virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 4: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 5: Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo SUCCESS! Virtual environment upgraded!
echo ========================================
echo.
echo Python version in new venv:
python --version
echo.
echo You can now start the server with:
echo   venv\Scripts\activate.bat
echo   uvicorn server_enhanced:app --reload --port 8001
echo.
echo Old venv backed up to: venv_backup
echo You can delete it after confirming everything works.
echo.
pause
