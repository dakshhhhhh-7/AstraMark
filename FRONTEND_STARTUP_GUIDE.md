# Frontend Startup Guide - AstraMark

## 🚀 Quick Start

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend
uvicorn server_enhanced:app --reload --port 8001
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Keep this terminal running!

---

### Step 2: Start the Frontend

Open a **NEW terminal** and run:

```bash
cd frontend
npm start
```

**Or if you prefer yarn:**
```bash
cd frontend
yarn start
```

**Expected Output:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

The browser should automatically open to `http://localhost:3000`

---

## 🔐 Login Credentials

### Option 1: Create a New Account

1. Go to `http://localhost:3000`
2. Click "Sign Up" or "Register"
3. Fill in:
   - **Email:** your-email@example.com
   - **Password:** YourPassword123
   - **Full Name:** Your Name
4. Click "Register"
5. You'll be automatically logged in

### Option 2: Use Test Account (If you already created one)

If you've already registered, use those credentials:
- **Email:** The email you registered with
- **Password:** The password you set

---

## 📝 Testing the Apify Integration

Once logged in:

### 1. Navigate to the Analysis Page
- Look for "New Analysis" or "Analyze Business" button
- Or go directly to the dashboard

### 2. Fill in the Business Form
```
Business Type: SaaS Marketing Platform
Target Market: United States
Monthly Budget: $5000
Primary Goal: Lead Generation
Additional Info: Focus on B2B companies
```

### 3. Submit and Wait
- Click "Analyze" or "Generate Analysis"
- **Wait 30-60 seconds** (Apify actors need time to run)
- You'll see a loading indicator

### 4. View Results
You should see:
- ✅ Real competitor names (from Apify Google Search)
- ✅ Market analysis with actual data
- ✅ Marketing strategies
- ✅ Revenue projections
- ✅ Competitor insights section

---

## 🔍 How to Verify Apify is Working

### Check the Browser Console
1. Open Developer Tools (F12)
2. Go to "Network" tab
3. Submit an analysis
4. Look for the `/api/analyze` request
5. Check the response - you should see:
   ```json
   {
     "competitor_insights": [
       {
         "name": "Real Company Name",
         "domain": "realcompany.com",
         "source": "apify_google_search"
       }
     ]
   }
   ```

### Check Backend Logs
In your backend terminal, you should see:
```
INFO: Searching competitors for SaaS Marketing Platform using Apify
INFO: Analysis generated successfully with Groq
```

---

## 🛠️ Troubleshooting

### Frontend Won't Start

**Error: `npm: command not found`**
```bash
# Install Node.js first
# Download from: https://nodejs.org/
```

**Error: `Module not found`**
```bash
cd frontend
npm install
# or
yarn install
```

**Error: Port 3000 already in use**
```bash
# Kill the process using port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port:
PORT=3001 npm start
```

### Backend Won't Start

**Error: `ModuleNotFoundError`**
```bash
cd backend
pip install -r requirements.txt
```

**Error: `Address already in use`**
```bash
# Use a different port
uvicorn server_enhanced:app --reload --port 8002

# Then update frontend/.env:
REACT_APP_BACKEND_URL=http://localhost:8002
```

### Login Issues

**Error: "Network Error" or "Cannot connect"**
- Check if backend is running on port 8001
- Check `frontend/.env` has correct `REACT_APP_BACKEND_URL`
- Try: `http://localhost:8001/api/health` in browser

**Error: "Invalid credentials"**
- Make sure you registered first
- Check email/password are correct
- Try registering a new account

### Analysis Not Working

**Stuck on "Loading..."**
- Check backend terminal for errors
- First analysis takes 30-60 seconds (Apify actors)
- Check browser console for errors

**Getting Mock/Fallback Data**
- Check `backend/.env` has `APIFY_API_TOKEN`
- Run: `cd backend && python verify_apify_setup.py`
- Check backend logs for Apify errors

---

## 📊 Expected User Flow

```
1. Open http://localhost:3000
   ↓
2. Register/Login
   ↓
3. Navigate to Dashboard/Analysis
   ↓
4. Fill in business details
   ↓
5. Click "Analyze"
   ↓
6. Wait 30-60 seconds
   ↓
7. View results with real competitor data
   ↓
8. Explore insights, strategies, projections
```

---

## 🎯 What to Look For

### Signs Apify is Working:
- ✅ Real company names in competitor section
- ✅ Actual domains (not "competitor-a.com")
- ✅ Confidence score: 0.9
- ✅ Source: "apify_google_search"
- ✅ Takes 30-60 seconds for first analysis

### Signs Using Fallback Data:
- ⚠️ Generic names like "SaaS Leader A"
- ⚠️ Fake domains like "competitor-a.com"
- ⚠️ Confidence score: 0.3
- ⚠️ Source: "fallback"
- ⚠️ Instant results (<5 seconds)

---

## 🔧 Configuration Files

### Backend Configuration
**File:** `backend/.env`
```env
APIFY_API_TOKEN=apify_api_yj1cEQCBUZcqYHOBhoINfkes4a3e8K1jliim
MONGO_URL=mongodb+srv://...
GROQ_API_KEY=your_groq_key_here
```

### Frontend Configuration
**File:** `frontend/.env`
```env
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_ENVIRONMENT=development
```

---

## 📱 Accessing from Mobile/Other Devices

### Find Your Local IP
```bash
# Windows
ipconfig
# Look for "IPv4 Address"

# Mac/Linux
ifconfig
# Look for "inet"
```

### Update Frontend .env
```env
REACT_APP_BACKEND_URL=http://YOUR_LOCAL_IP:8001
```

### Access from Mobile
```
http://YOUR_LOCAL_IP:3000
```

**Example:**
```
http://192.168.1.100:3000
```

---

## 🎨 Features to Test

### 1. Authentication
- ✅ Register new account
- ✅ Login with credentials
- ✅ Logout
- ✅ Protected routes

### 2. Business Analysis
- ✅ Submit business details
- ✅ View loading state
- ✅ See analysis results
- ✅ Real competitor data

### 3. Dashboard Features
- ✅ View past analyses
- ✅ Market signals
- ✅ AI insights
- ✅ Revenue projections

### 4. Premium Features (if implemented)
- ✅ PDF export
- ✅ Content calendar
- ✅ Pitch deck generation

---

## 📞 Need Help?

### Check Status
```bash
# Backend health check
curl http://localhost:8001/api/health

# Should return:
{
  "status": "healthy",
  "ai_services": {...},
  "market_intelligence": {
    "apify_enabled": true,
    ...
  }
}
```

### View Logs
- **Backend:** Check the terminal running uvicorn
- **Frontend:** Check browser console (F12)

### Run Tests
```bash
# Backend Apify test
cd backend
python test_apify_integration.py

# Backend verification
python verify_apify_setup.py
```

---

## 🚀 Production Deployment

When ready to deploy:

### Backend
1. Set environment variables on your hosting platform
2. Update `ENVIRONMENT=production` in `.env`
3. Deploy to Railway/Heroku/AWS

### Frontend
1. Update `frontend/.env.production`:
   ```env
   REACT_APP_BACKEND_URL=https://your-api-domain.com
   REACT_APP_ENVIRONMENT=production
   ```
2. Build: `npm run build`
3. Deploy `build/` folder to Netlify/Vercel/AWS

---

## ✅ Success Checklist

- [ ] Backend running on port 8001
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:3000
- [ ] Can register a new account
- [ ] Can login successfully
- [ ] Can submit business analysis
- [ ] Analysis completes in 30-60 seconds
- [ ] See real competitor names (not mock data)
- [ ] Competitor source shows "apify_google_search"
- [ ] Can view full analysis results

---

## 🎉 You're Ready!

Your AstraMark platform is now running with:
- ✅ Real-time competitor data from Apify
- ✅ AI-powered analysis
- ✅ User authentication
- ✅ Full-featured dashboard

Start analyzing businesses and see real market intelligence in action! 🚀
