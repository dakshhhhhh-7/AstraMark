# Quick Start Commands - AstraMark

## 🚀 Start Everything (2 Terminals)

### Terminal 1: Backend
```bash
cd backend
uvicorn server_enhanced:app --reload --port 8001
```

### Terminal 2: Frontend
```bash
cd frontend
npm start
```

---

## 🔐 Test Login Credentials

### Create New Account
1. Go to: `http://localhost:3000`
2. Click "Sign Up"
3. Use any email/password:
   - Email: `test@example.com`
   - Password: `Test123456`
   - Name: `Test User`

### Login
Use the credentials you just created!

---

## 🧪 Test Apify Integration

### Quick Test
```bash
cd backend
python test_apify_integration.py
```

### Verify Setup
```bash
cd backend
python verify_apify_setup.py
```

---

## 🔍 Check if Everything is Running

### Backend Health Check
```bash
curl http://localhost:8001/api/health
```

### Frontend
Open browser: `http://localhost:3000`

---

## 🛑 Stop Everything

Press `Ctrl+C` in both terminals

---

## 📝 Test Analysis

Once logged in, use these test values:

```
Business Type: SaaS Marketing Platform
Target Market: United States  
Monthly Budget: 5000
Primary Goal: Lead Generation
Additional Info: B2B focus
```

Click "Analyze" and wait 30-60 seconds!

---

## ⚡ One-Line Installers

### Install Backend Dependencies
```bash
cd backend && pip install -r requirements.txt
```

### Install Frontend Dependencies
```bash
cd frontend && npm install
```

---

## 🐛 Quick Fixes

### Backend Port Already in Use
```bash
uvicorn server_enhanced:app --reload --port 8002
```
Then update `frontend/.env`:
```
REACT_APP_BACKEND_URL=http://localhost:8002
```

### Frontend Port Already in Use
```bash
PORT=3001 npm start
```

### Reset Everything
```bash
# Kill all node processes (Windows)
taskkill /F /IM node.exe

# Kill all Python processes (Windows)
taskkill /F /IM python.exe

# Then restart both servers
```

---

## 📊 Expected Results

### Backend Terminal Should Show:
```
INFO: Starting AstraMark Enhanced Server...
INFO: Connected to MongoDB
INFO: Gemini AI Client configured
INFO: Groq service available as fallback
INFO: Application startup complete.
```

### Frontend Terminal Should Show:
```
Compiled successfully!
webpack compiled with 0 warnings
```

### Browser Should Show:
- Login/Register page
- After login: Dashboard with analysis form

---

## ✅ Success Indicators

When you submit an analysis, look for:

1. **Loading state** (30-60 seconds)
2. **Real competitor names** (not "Competitor A")
3. **Actual domains** (not "competitor-a.com")
4. **Source: "apify_google_search"**
5. **Confidence: 0.9**

---

## 🎯 URLs to Remember

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs
- **Health Check:** http://localhost:8001/api/health

---

## 📞 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect to backend | Check if backend is running on port 8001 |
| Login fails | Register a new account first |
| Analysis stuck | Wait 60 seconds, check backend logs |
| Mock data instead of real | Run `python verify_apify_setup.py` |
| Port in use | Use different port (see Quick Fixes) |

---

## 🎉 That's It!

You're ready to test the full platform with real Apify data!
