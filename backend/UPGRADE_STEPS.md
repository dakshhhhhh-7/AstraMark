# Python 3.12 Upgrade - Step-by-Step Guide

## Step 1: Download Python 3.12

1. Open your browser
2. Go to: **https://www.python.org/downloads/**
3. Click the big yellow button "Download Python 3.12.x"
4. Wait for download to complete

## Step 2: Install Python 3.12

1. Run the downloaded installer (python-3.12.x-amd64.exe)
2. **CRITICAL**: Check the box "Add python.exe to PATH" at the bottom
3. Click "Install Now"
4. Wait for installation (2-3 minutes)
5. Click "Close" when done

## Step 3: Verify Installation

1. **Close all PowerShell/terminal windows**
2. Open a **NEW** PowerShell window
3. Run this command:

```powershell
py -0
```

You should see something like:
```
 -V:3.12          Python 3.12 (64-bit)
 -V:3.10          Python 3.10 (64-bit)
```

If you see Python 3.12, you're good! Proceed to Step 4.

## Step 4: Recreate Virtual Environment

Copy and paste these commands one by one:

```powershell
# Navigate to backend folder
cd D:\AstraMark\backend

# Deactivate current venv if active
deactivate

# Backup old venv
move venv venv_python310_backup

# Create new venv with Python 3.12
py -3.12 -m venv venv

# Activate new venv
.\venv\Scripts\activate.bat

# Verify Python version (should show 3.12.x)
python --version

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies (this will take 2-3 minutes)
pip install -r requirements.txt
```

## Step 5: Test MongoDB Connection

```powershell
python test_connection.py
```

You should see:
```
✅ MongoDB connection successful!
✅ Database access successful!
```

## Step 6: Start the Server

```powershell
python run_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

## Step 7: Test Endpoints

Open a new PowerShell window and test:

```powershell
# Test health check
curl http://localhost:8001/api/

# Should return: {"message": "AstraMark AI Marketing Platform API - Enhanced Edition"}
```

## Troubleshooting

### "py -3.12 not found"
- Make sure you checked "Add to PATH" during installation
- Restart your computer
- Try: `py -3.11` if you installed 3.11 instead

### "pip install fails"
- Make sure venv is activated (you should see `(venv)` in prompt)
- Try: `python -m pip install --upgrade pip` first
- Then retry: `pip install -r requirements.txt`

### "MongoDB still fails"
- Make sure you're using the NEW venv (check `python --version`)
- Make sure you ran `pip install -r requirements.txt`
- Check internet connection

## After Successful Upgrade

1. Delete old venv:
```powershell
rmdir /s /q venv_python310_backup
```

2. Update your start script to use new Python

3. Continue with endpoint testing!

---

**Current Step**: Please complete Steps 1-3 first, then let me know when Python 3.12 is installed.
