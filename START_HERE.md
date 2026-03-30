# 🚀 START HERE - AstraMark Quick Launch

## ⚡ Super Quick Start (Copy & Paste)

### Terminal 1 (Backend):
```bash
cd D:\AstraMark\backend
uvicorn server_enhanced:app --reload --port 8001
```

### Terminal 2 (Frontend):
```bash
cd D:\AstraMark\frontend
npm start
```

### Browser:
```
http://localhost:3000
```

---

## 🔐 Login Info

### First Time?
1. Click "Sign Up"
2. Use any email/password:
   - Email: `test@example.com`
   - Password: `Test123456`

### Already Registered?
Use your existing credentials!

---

## 🧪 Test Apify Integration

### Quick Test Values:
```
Business Type: SaaS Marketing Platform
Target Market: United States
Monthly Budget: 5000
Primary Goal: Lead Generation
```

Click "Analyze" and wait 30-60 seconds!

---

## ✅ How to Know It's Working

Look for **real company names** in competitor section:
- ✅ "HubSpot", "Salesforce" (GOOD - Apify working!)
- ❌ "Competitor A", "Competitor B" (BAD - using fallback)

Check the **source** field:
- ✅ `source: "apify_google_search"` (GOOD!)
- ❌ `source: "fallback"` (BAD!)

---

## 📚 Detailed Guides

- **QUICK_START_COMMANDS.md** - All commands in one place
- **FRONTEND_STARTUP_GUIDE.md** - Complete setup guide
- **TESTING_GUIDE.md** - Step-by-step testing instructions
- **APIFY_INTEGRATION_STATUS.md** - Technical documentation

---

## 🐛 Quick Fixes

### Backend won't start?
```bash
cd backend
pip install -r requirements.txt
```

### Frontend won't start?
```bash
cd frontend
npm install
```

### Port already in use?
```bash
# Backend on different port
uvicorn server_enhanced:app --reload --port 8002

# Update frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8002
```

---

## 🎯 Success Checklist

- [ ] Backend running (Terminal 1)
- [ ] Frontend running (Terminal 2)
- [ ] Can access http://localhost:3000
- [ ] Can register/login
- [ ] Can submit analysis
- [ ] See real competitor names
- [ ] Source shows "apify_google_search"

---

## 📞 Need Help?

1. Check terminals for errors
2. Run: `cd backend && python verify_apify_setup.py`
3. Check browser console (F12)
4. Read **TESTING_GUIDE.md** for detailed help

---

## 🎉 You're Ready!

Everything is configured and tested. Just start both servers and test!

**Apify API Key:** ✅ Working  
**Backend:** ✅ Configured  
**Frontend:** ✅ Ready  
**Integration:** ✅ Tested  

Let's go! 🚀
