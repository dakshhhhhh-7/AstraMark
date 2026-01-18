# 🚀 Quick Start Guide - AstraMark Enhanced

## ⚡ Get Started in 3 Minutes

### Step 1: Start the Enhanced Backend
```bash
cd backend
python -m uvicorn server_enhanced:app --reload --host 0.0.0.0 --port 8001
```

**Expected Output**:
```
INFO:     Starting AstraMark Enhanced Server...
INFO:     Background scanner started (interval: 30 minutes)
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Step 2: Start the Frontend
```bash
cd frontend
npm start
```

**Expected Output**:
```
Compiled successfully!
You can now view astramark in the browser.
  Local:            http://localhost:3000
```

### Step 3: Test the System

#### Option A: Via Browser
1. Open http://localhost:3000
2. Fill in the business form:
   - Business Type: "AI SaaS Platform"
   - Target Market: "Tech startups in USA"
   - Monthly Budget: "$10,000"
   - Primary Goal: "Acquire 1000 users in 3 months"
3. Click "Generate AI Marketing Strategy"
4. Wait 20-30 seconds for AI analysis
5. **NEW**: Scroll down to see "Content Generation & Export" panel
6. Click "Export PDF Report" to download

#### Option B: Via API
```bash
# Create an analysis
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "AI SaaS Platform",
    "target_market": "Tech startups",
    "monthly_budget": "$10,000",
    "primary_goal": "Acquire 1000 users"
  }' | jq '.id'

# Copy the analysis ID, then export PDF
curl http://localhost:8001/api/export/pdf/{ANALYSIS_ID} --output report.pdf

# Generate pitch deck
curl -X POST "http://localhost:8001/api/generate/pitch-deck?analysis_id={ANALYSIS_ID}" | jq

# Generate content calendar
curl -X POST "http://localhost:8001/api/generate/content-calendar?analysis_id={ANALYSIS_ID}&weeks=4" | jq
```

---

## 🎯 What You'll See

### 1. Enhanced Analysis Response
```json
{
  "id": "abc123...",
  "overview": "Your business snapshot...",
  "market_analysis": { ... },
  "user_personas": [ ... ],
  "strategies": [ ... ],
  
  // NEW FEATURES:
  "competitor_insights": [
    {
      "name": "AI SaaS Leader A",
      "domain": "competitor-a.com",
      "estimated_traffic": "8,000-12,000",
      "ad_spend_monthly": "$15,000-$25,000",
      "active_campaigns": 24
    }
  ],
  "blockchain_proof": {
    "hash": "a3f5b2c1...",
    "timestamp": "2026-01-08 21:30:00 UTC",
    "network": "AstraMark Intelligence Ledger (Database)",
    "verified": false
  },
  "market_signals": [
    {
      "type": "Competitive",
      "severity": "critical",
      "message": "Major competitor increased ad spend by 40%"
    }
  ]
}
```

### 2. Content Actions Panel (Frontend)
You'll see 4 new action cards:
- 📄 **Export PDF Report** (Free) - Download professional report
- 🎤 **Generate Pitch Deck** (Pro) - 9-slide investor presentation
- 📅 **Content Calendar** (Pro) - 4-week posting schedule
- ✉️ **Email Sequence** (Pro) - 5-email drip campaign

### 3. Background Scanner Logs
Every 30 minutes, you'll see:
```
INFO:     Starting market scan...
INFO:     Market scan completed. Generated 4 signals
INFO:     Starting competitor monitoring...
INFO:     Competitor monitoring completed. 2 snapshots created
```

---

## 🔧 Configuration Options

### Enable Live Market Data (Optional)
1. Get SERP API key from https://serpapi.com
2. Edit `backend/.env`:
   ```bash
   SERP_API_KEY="your_actual_key_here"
   ENABLE_LIVE_MARKET_DATA=true
   ```
3. Restart backend server

**Result**: Real competitor data instead of mock data

### Enable Blockchain (Optional)
1. Get Alchemy key from https://www.alchemy.com
2. Edit `backend/.env`:
   ```bash
   POLYGON_RPC_URL="https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY"
   ENABLE_BLOCKCHAIN=true
   ```
3. Restart backend server

**Result**: On-chain proofs on Polygon Amoy testnet

---

## 🧪 Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3000
- [ ] Can create a new analysis
- [ ] Analysis includes `competitor_insights`
- [ ] Analysis includes `blockchain_proof`
- [ ] Can export PDF report
- [ ] PDF downloads successfully
- [ ] Background scanner logs appear (wait 30 min)
- [ ] Health check shows all services: http://localhost:8001/api/health

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.10+)
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Try original server if enhanced fails
python -m uvicorn server:app --reload --port 8001
```

### PDF export fails
```bash
# Install missing dependencies
pip install reportlab pillow

# On Windows:
pip install pywin32
```

### Frontend errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

### Background scanner not running
```bash
# Check .env file:
ENABLE_BACKGROUND_SCANNER=true

# Check server logs for:
# "Background scanner started"
```

---

## 📊 Expected Performance

- **Analysis Generation**: 20-30 seconds
- **PDF Export**: 2-5 seconds
- **Pitch Deck Generation**: 15-20 seconds
- **Content Calendar**: 20-30 seconds
- **Email Sequence**: 10-15 seconds
- **Background Scan**: Runs every 30 minutes

---

## 🎉 Success Indicators

✅ You're ready when you see:
1. Backend running on port 8001
2. Frontend running on port 3000
3. "Background scanner started" in logs
4. Can generate analysis with competitor data
5. Can download PDF report
6. Health check returns all services enabled

---

## 📞 Need Help?

Check these files:
- `ENHANCED_FEATURES.md` - Full feature documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `README.md` - Original project documentation

---

**Happy Building! 🚀**
