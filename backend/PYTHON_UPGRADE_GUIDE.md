# Python 3.11+ Upgrade Guide for AstraMark

## Current Status
- **Current Python**: 3.10.11
- **Issue**: SSL/TLS handshake errors with MongoDB Atlas on Windows
- **Temporary Fix**: SSL workaround added (development only)
- **Recommended**: Upgrade to Python 3.11 or 3.12

## Quick Start (Try Current Setup First)

The SSL workaround has been added. Try starting the server:

```bash
cd backend
.\venv\Scripts\activate.bat
uvicorn server_enhanced:app --reload --port 8001
```

If it works, you're good to go! If you still see SSL errors, proceed with the upgrade below.

## Option 1: Upgrade to Python 3.11+ (Recommended)

### Step 1: Install Python 3.11 or 3.12

1. Download from: https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Install for all users (recommended)

### Step 2: Recreate Virtual Environment

Run the automated script:

```bash
cd backend
upgrade_venv.bat
```

This will:
- Backup your current venv to `venv_backup`
- Create a new venv with Python 3.11+
- Install all dependencies
- Verify the installation

### Step 3: Start the Server

```bash
.\venv\Scripts\activate.bat
uvicorn server_enhanced:app --reload --port 8001
```

## Option 2: Manual Upgrade

If the automated script doesn't work:

```bash
# 1. Deactivate current venv
deactivate

# 2. Backup and remove old venv
move venv venv_backup

# 3. Create new venv with Python 3.11+
py -3.11 -m venv venv
# or
py -3.12 -m venv venv

# 4. Activate new venv
.\venv\Scripts\activate.bat

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install dependencies
pip install -r requirements.txt

# 7. Verify Python version
python --version
```

## What Changed?

### SSL Workaround Added (Development Only)

In `server_enhanced.py`, added:
- Proper SSL context configuration
- Development mode relaxed SSL settings
- Uses `certifi` for certificate verification
- Falls back to `CERT_NONE` in development if needed

### Groq Client Fix

In `groq_service.py`, fixed:
- Removed unsupported `proxies` parameter
- Added graceful fallback for version compatibility

## Troubleshooting

### "Python 3.11 not found"
- Make sure you installed Python 3.11+ and checked "Add to PATH"
- Restart your terminal/PowerShell after installation
- Verify with: `py -0` (should list all Python versions)

### "pip install fails"
- Make sure you're in the activated venv
- Try: `python -m pip install --upgrade pip`
- Then retry: `pip install -r requirements.txt`

### "Server still won't start"
- Check MongoDB connection string in `.env`
- Verify your MongoDB Atlas cluster is running
- Check firewall/network settings
- Try the SSL workaround by ensuring `ENVIRONMENT=development` in `.env`

## Benefits of Python 3.11+

- Better SSL/TLS support on Windows
- 10-60% faster performance
- Better error messages
- Improved async/await performance
- Better type hints support
- Security improvements

## After Upgrade

Once everything works with Python 3.11+:
1. Delete the backup: `rmdir /s /q venv_backup`
2. Update your documentation
3. Consider updating `.gitignore` if needed

## Need Help?

If you encounter issues:
1. Check the error message carefully
2. Verify Python version: `python --version`
3. Verify venv is activated (should see `(venv)` in prompt)
4. Check MongoDB connection string
5. Ensure all environment variables are set in `.env`
