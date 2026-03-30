# 🚀 EASY START GUIDE - AstraMark

## ✅ Setup Complete!

Your backend dependencies are installed and ready to go!

---

## 🎯 SUPER EASY START (Just Double-Click!)

### Option 1: Use the Batch Files (Easiest!)

1. **Start Backend:**
   - Double-click `START_BACKEND.bat`
   - Wait for "Application startup complete"

2. **Start Frontend:**
   - Double-click `START_FRONTEND.bat`
   - Browser will open automatically

---

## 📝 Manual Start (If batch files don't work)

### Terminal 1 - Backend:
```bash
cd D:\AstraMark\backend
venv\Scripts\activate
python -m uvicorn server_enhanced:app --reload --port 8001
```

### Terminal 2 - Frontend:
```bash
cd D:\AstraMark\frontend
npm start
```

---

## 🔐 First Time Setup

### 1. Open Browser
Go to: `http://localhost:3000`

### 2. Create Account
Click "Sign Up" and fill in:
```
Email: test@example.com
Password: Test123456
Name: Test User
```

### 3. Test Analysis
Fill in the form:
```
Business Type: SaaS Marketing Platform
Target Market: United States
Monthly Budget: 5000
Primary Goal: Lead Generation
Additional Info: B2B focus
```

Click "Analyze" and wait 30-60 seconds!

---

## ✅ How to Know It's Working

### Backend Terminal Should Show:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### Frontend Terminal Should Show:
```
Compiled successfully!
webpack compiled with 0 warnings
```

### In the Results, Look For:
- ✅ Real company names (HubSpot, Salesforce, etc.)
- ✅ Actual domains (hubspot.com, salesforce.com)
- ✅ Source: "apify_google_search"
- ✅ Confidence: 0.9

### NOT These (Fallback Data):
- ❌ Generic names (Competitor A, SaaS Leader B)
- ❌ Fake domains (competitor-a.com)
- ❌ Source: "fallback"
- ❌ Confidence: 0.3

---

## 🐛 Troubleshooting

### Backend Won't Start?

**Error: "ModuleNotFoundError"**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements-minimal.txt
```

**Error: "Port 8001 already in use"**
```bash
# Use different port
python -m uvicorn server_enhanced:app --reload --port 8002

# Update frontend/.env:
REACT_APP_BACKEND_URL=http://localhost:8002
```

### Frontend Won't Start?

**Error: "npm: command not found"**
- Install Node.js from: https://nodejs.org/

**Error: "Module not found"**
```bash
cd frontend
npm install
```

**Error: "Port 3000 already in use"**
```bash
# Windows: Kill the process
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different port
set PORT=3001 && npm start
```

### Can't Login?

1. Make sure backend is running
2. Check `http://localhost:8001/api/health` in browser
3. Register a new account first
4. Use correct email/password

### Getting Mock Data Instead of Real Data?

```bash
cd backend
python verify_apify_setup.py
```

Should show all ✅ checks passing.

---

## 📊 What You Should See

### 1. Login Page
- Clean form with email/password
- Sign Up and Login buttons

### 2. Dashboard
- Welcome message
- "New Analysis" button
- Recent analyses (if any)

### 3. Analysis Form
- Business Type field
- Target Market field
- Monthly Budget field
- Primary Goal dropdown
- Additional Info textarea

### 4. Loading State (30-60 seconds)
- Spinner or progress bar
- "Analyzing..." message
- "Fetching competitor data..."

### 5. Results Page
- Overview section
- Market Analysis
- **Competitor Insights** (with REAL companies!)
- Marketing Strategies
- Revenue Projections
- AI Insights

---

## 🎉 Success Checklist

- [ ] Backend started (Terminal 1)
- [ ] Frontend started (Terminal 2)
- [ ] Can access http://localhost:3000
- [ ] Can register account
- [ ] Can login
- [ ] Can submit analysis
- [ ] Analysis completes (30-60 seconds)
- [ ] See real competitor names
- [ ] Source shows "apify_google_search"
- [ ] Confidence is 0.9

---

## 📞 Quick Help

### Check Backend Status
Open browser: `http://localhost:8001/api/health`

Should return:
```json
{
  "status": "healthy",
  "apify_enabled": true,
  "db_connected": true
}
```

### Test Apify Integration
```bash
cd backend
venv\Scripts\activate
python test_apify_integration.py
```

Should show: `✅ ALL TESTS PASSED`

### Verify Setup
```bash
cd backend
venv\Scripts\activate
python verify_apify_setup.py
```

Should show all ✅ checks.

---

## 🚀 You're All Set!

Everything is configured and ready:
- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ Apify API key configured
- ✅ Startup scripts created
- ✅ Frontend ready

Just double-click the batch files and start testing!

---

## 📚 More Help

- **COMMAND_CARD.txt** - Quick reference
- **TESTING_GUIDE.md** - Detailed testing steps
- **FRONTEND_STARTUP_GUIDE.md** - Complete frontend guide
- **APIFY_INTEGRATION_STATUS.md** - Technical docs

---

**Happy Testing! 🎉**
