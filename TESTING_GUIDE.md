# 🧪 AstraMark Enhanced - Complete Testing Guide

## ✅ Expected Server Output

When you start the enhanced backend, you should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:server_enhanced:Connected to MongoDB: mongodb://localhost:27017
INFO:server_enhanced:Gemini AI configured
INFO:server_enhanced:Starting AstraMark Enhanced Server...
INFO:apscheduler.scheduler:Added job "Market Signal Scanner" to job store "default"
INFO:apscheduler.scheduler:Added job "Competitor Monitor" to job store "default"
INFO:apscheduler.scheduler:Scheduler started
INFO:scanner_service:Background scanner started (interval: 30 minutes)
INFO:server_enhanced:Background scanner started
INFO:     Application startup complete.
```

✅ **What this means**:
- ✅ Server running on port 8001
- ✅ MongoDB connected
- ✅ Gemini AI ready
- ✅ Background scanner active (will scan every 30 min)
- ✅ All services initialized

---

## 🧪 Test 1: Health Check

### Command:
```bash
curl http://localhost:8001/api/health
```

### Expected Output:
```json
{
  "status": "healthy",
  "ai_enabled": true,
  "db_connected": true,
  "serp_enabled": false,
  "blockchain_enabled": false,
  "scanner_enabled": true
}
```

✅ **What to verify**:
- `status`: "healthy"
- `ai_enabled`: true (Gemini API key configured)
- `db_connected`: true (MongoDB connected)
- `serp_enabled`: false (no SERP API key yet - using mock data)
- `blockchain_enabled`: false (no RPC URL yet - using DB fallback)
- `scanner_enabled`: true (background scanner running)

---

## 🧪 Test 2: Create Analysis (Main Feature)

### Command:
```bash
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"business_type\":\"AI SaaS Platform\",\"target_market\":\"Tech startups in USA\",\"monthly_budget\":\"$10,000\",\"primary_goal\":\"Acquire 1000 users in 3 months\",\"additional_info\":\"B2B focus with freemium model\"}"
```

### Expected Output (Partial - it's large):
```json
{
  "id": "abc123-def456-...",
  "business_id": "xyz789-...",
  "overview": "This AI SaaS platform targets tech startups...",
  
  "market_analysis": {
    "market_size": "Estimated $50-100 billion globally",
    "growth_rate": "25-30% annually",
    "entry_barriers": "High - requires AI expertise, data infrastructure",
    "opportunities": [
      "Growing demand for AI automation",
      "Underserved SMB market",
      "Integration opportunities"
    ],
    "risks": [
      "Intense competition",
      "Rapid technology changes",
      "Customer acquisition costs"
    ],
    "strengths": ["AI-powered", "Freemium model"],
    "weaknesses": ["New entrant", "Limited brand"]
  },
  
  "user_personas": [
    {
      "name": "Tech-Savvy Founder",
      "demographics": "25-40 years old, USA-based, $50K-150K income",
      "psychographics": "Innovation-focused, data-driven, efficiency-oriented",
      "pain_points": [
        "Manual processes consuming time",
        "Lack of marketing expertise",
        "Limited budget for agencies"
      ],
      "buying_triggers": [
        "Free trial availability",
        "ROI demonstration",
        "Peer recommendations"
      ],
      "objections": ["Price concerns", "Integration complexity"]
    }
  ],
  
  "strategies": [
    {
      "channel": "SEO",
      "strategy": "Focus on long-tail keywords targeting startup pain points...",
      "content_ideas": [
        "How AI automates marketing for startups",
        "SaaS marketing guide for founders",
        "Free tools for startup growth"
      ],
      "posting_schedule": "2-3 blog posts per week",
      "kpi_benchmarks": {
        "organic_traffic": "5,000-10,000 monthly visitors",
        "conversion_rate": "2-3%"
      }
    }
    // ... 3 more channels (Content Marketing, Paid Ads, Social Media)
  ],
  
  "revenue_projection": {
    "min_monthly": "$15,000",
    "max_monthly": "$50,000",
    "growth_timeline": "6-12 months to reach targets"
  },
  
  "virality_score": 75,
  "retention_score": 80,
  "ai_verdict": "High Growth Potential",
  "confidence_score": 85,
  
  "biggest_opportunity": "Leverage AI differentiation in underserved SMB market",
  "biggest_risk": "High customer acquisition costs in competitive landscape",
  "next_action": "Launch content marketing campaign targeting startup founders",
  
  // ✨ NEW ENHANCED FEATURES:
  
  "competitor_insights": [
    {
      "name": "AI SaaS Platform Leader A",
      "domain": "competitor-a.com",
      "description": "Leading AI SaaS Platform platform in Tech startups in USA",
      "position": 1,
      "estimated_traffic": "8,000-12,000",
      "ad_spend_monthly": "$15,000-$25,000",
      "active_campaigns": 24,
      "top_keywords": ["saas platform", "business software", "automation tool"]
    },
    {
      "name": "AI SaaS Platform Challenger B",
      "domain": "competitor-b.com",
      "estimated_traffic": "5,000-8,000",
      "ad_spend_monthly": "$8,000-$15,000",
      "active_campaigns": 18
    }
  ],
  
  "blockchain_proof": {
    "hash": "a3f5b2c1d4e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
    "timestamp": "2026-01-08 22:15:30 UTC",
    "network": "AstraMark Intelligence Ledger (Database)",
    "verified": false
  },
  
  "market_signals": [
    {
      "id": "signal-123",
      "type": "Competitive",
      "severity": "critical",
      "message": "Major competitor in AI SaaS Platform increased ad spend by 40%",
      "detected_at": "2 mins ago"
    },
    {
      "type": "Consumer",
      "severity": "info",
      "message": "Shift in search patterns detected for target audience",
      "detected_at": "15 mins ago"
    }
  ],
  
  "execution_actions": [
    {
      "action_id": "auto-content",
      "action_type": "content",
      "action_name": "Generate Social Content",
      "description": "AI-written posts based on this strategy",
      "is_premium": false,
      "status": "active"
    },
    {
      "action_id": "competitor-track",
      "action_type": "monitoring",
      "action_name": "Live Competitor Tracking",
      "description": "Monitor landing page changes in real-time",
      "is_premium": true,
      "status": "locked"
    }
  ],
  
  "created_at": "2026-01-08T16:45:30.123456+00:00"
}
```

✅ **What to verify**:
- ✅ `id` and `business_id` are UUIDs
- ✅ `market_analysis` has all fields (market_size, growth_rate, etc.)
- ✅ `user_personas` array with detailed personas
- ✅ `strategies` array with 4 channels (SEO, Content, Paid Ads, Social)
- ✅ **NEW**: `competitor_insights` with 3 competitors (mock data)
- ✅ **NEW**: `blockchain_proof` with hash and timestamp
- ✅ **NEW**: `market_signals` array with alerts
- ✅ **NEW**: `execution_actions` with actionable items
- ✅ Response time: 20-30 seconds (AI generation)

---

## 🧪 Test 3: Export PDF Report

### Step 1: Copy the analysis ID from Test 2
```bash
# From the response above, copy the "id" field
# Example: "abc123-def456-ghi789"
```

### Step 2: Export PDF
```bash
curl http://localhost:8001/api/export/pdf/abc123-def456-ghi789 --output report.pdf
```

### Expected Output:
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 45678    0 45678    0     0  15226      0 --:--:--  0:00:03 --:--:-- 15226
```

✅ **What to verify**:
- ✅ File `report.pdf` created in current directory
- ✅ File size: ~40-50 KB
- ✅ Open the PDF and check:
  - Title page: "AstraMark Intelligence Report"
  - Executive Summary section
  - Key Performance Indicators table
  - Market Analysis section
  - SWOT Analysis table (color-coded)
  - User Personas section
  - Marketing Strategies section
  - Revenue Projections table
  - Action Items section
  - Blockchain Verification section (with hash)

---

## 🧪 Test 4: Generate Pitch Deck

### Command:
```bash
curl -X POST "http://localhost:8001/api/generate/pitch-deck?analysis_id=abc123-def456-ghi789"
```

### Expected Output:
```json
{
  "pitch_deck": {
    "slides": [
      {
        "slide_number": 1,
        "title": "Problem",
        "content": [
          "Tech startups struggle with manual marketing processes",
          "Limited budget for marketing agencies",
          "Lack of in-house marketing expertise"
        ],
        "speaker_notes": "Start by highlighting the pain points that resonate with investors"
      },
      {
        "slide_number": 2,
        "title": "Solution",
        "content": [
          "AI-powered marketing automation platform",
          "Freemium model for easy adoption",
          "10x faster than traditional methods"
        ],
        "speaker_notes": "Emphasize the AI differentiation and business model"
      },
      {
        "slide_number": 3,
        "title": "Market Opportunity",
        "content": [
          "$50-100 billion global market",
          "25-30% annual growth rate",
          "Underserved SMB segment"
        ],
        "speaker_notes": "Show the massive market potential"
      }
      // ... 6 more slides (Business Model, Traction, Competition, Team, Financials, Ask)
    ]
  },
  "total_slides": 9,
  "generated_at": "2026-01-08T16:50:00.123456"
}
```

✅ **What to verify**:
- ✅ `total_slides`: 9
- ✅ Each slide has: `slide_number`, `title`, `content`, `speaker_notes`
- ✅ Slides cover: Problem, Solution, Market, Business Model, Traction, Competition, Team, Financials, Ask
- ✅ Response time: 15-20 seconds

---

## 🧪 Test 5: Generate Content Calendar

### Command:
```bash
curl -X POST "http://localhost:8001/api/generate/content-calendar?analysis_id=abc123-def456-ghi789&weeks=4"
```

### Expected Output:
```json
{
  "content_calendar": {
    "weeks": [
      {
        "week_number": 1,
        "days": [
          {
            "day": "Monday",
            "date": "2026-01-13",
            "posts": [
              {
                "channel": "LinkedIn",
                "content_type": "Article",
                "topic": "AI Marketing Automation for Startups",
                "caption": "🚀 How AI is transforming marketing for tech startups...",
                "hashtags": ["#AIMarketing", "#StartupGrowth", "#MarketingAutomation"],
                "time": "09:00 AM"
              },
              {
                "channel": "Twitter",
                "content_type": "Thread",
                "topic": "Marketing tips for founders",
                "caption": "Thread: 10 marketing hacks every founder should know 🧵",
                "hashtags": ["#StartupTips", "#Marketing"],
                "time": "02:00 PM"
              }
            ]
          },
          {
            "day": "Tuesday",
            "date": "2026-01-14",
            "posts": [ /* ... */ ]
          }
          // ... 5 more days
        ]
      },
      {
        "week_number": 2,
        "days": [ /* ... */ ]
      }
      // ... 2 more weeks
    ]
  },
  "duration_weeks": 4,
  "total_posts": 56,
  "generated_at": "2026-01-08T16:55:00.123456"
}
```

✅ **What to verify**:
- ✅ `duration_weeks`: 4
- ✅ `total_posts`: 40-60 posts
- ✅ Each post has: channel, content_type, topic, caption, hashtags, time
- ✅ Multiple channels: LinkedIn, Twitter, Instagram, Facebook
- ✅ Response time: 20-30 seconds

---

## 🧪 Test 6: Generate Email Sequence

### Command:
```bash
curl -X POST "http://localhost:8001/api/generate/email-sequence?analysis_id=abc123-def456-ghi789&sequence_type=onboarding"
```

### Expected Output:
```json
{
  "email_sequence": {
    "sequence_name": "Onboarding Sequence",
    "emails": [
      {
        "email_number": 1,
        "send_delay_days": 0,
        "subject_line": "Welcome to AstraMark! 🚀",
        "preview_text": "Get started with AI-powered marketing in 3 easy steps",
        "body": "Hi {{first_name}},\n\nWelcome to AstraMark! We're excited to help you...",
        "cta": "Get Started Now",
        "cta_link": "https://astramark.com/onboarding"
      },
      {
        "email_number": 2,
        "send_delay_days": 2,
        "subject_line": "Your first AI marketing strategy is ready",
        "preview_text": "See how AI analyzed your business",
        "body": "Hi {{first_name}},\n\nYour personalized marketing strategy...",
        "cta": "View Strategy",
        "cta_link": "https://astramark.com/dashboard"
      }
      // ... 3 more emails
    ]
  },
  "total_emails": 5,
  "sequence_type": "onboarding",
  "generated_at": "2026-01-08T17:00:00.123456"
}
```

✅ **What to verify**:
- ✅ `total_emails`: 5
- ✅ Each email has: email_number, send_delay_days, subject_line, preview_text, body, cta, cta_link
- ✅ Delay progression: 0, 2, 5, 7, 14 days
- ✅ Personalization tags: {{first_name}}, {{company_name}}
- ✅ Response time: 10-15 seconds

---

## 🧪 Test 7: Market Signals (Background Scanner)

### Wait 30 minutes after server start, then:

```bash
curl http://localhost:8001/api/market/signals?limit=10
```

### Expected Output:
```json
{
  "signals": [
    {
      "_id": "...",
      "business_type": "AI SaaS Platform",
      "target_market": "Tech startups in USA",
      "signal_type": "Market",
      "severity": "warning",
      "message": "Google Ads CPC increased +18% for AI SaaS Platform - consider adjusting budget",
      "detected_at": "2026-01-08T17:30:00+00:00",
      "created_at": "2026-01-08T17:30:00+00:00"
    },
    {
      "signal_type": "Market",
      "severity": "info",
      "message": "Meta Ads CPM decreased -12% - good opportunity for paid social campaigns",
      "detected_at": "2026-01-08T17:30:00+00:00"
    },
    {
      "signal_type": "Competitive",
      "severity": "info",
      "message": "Top competitor \"AI SaaS Platform Leader A\" detected in Tech startups in USA",
      "detected_at": "2026-01-08T17:30:00+00:00"
    }
  ],
  "count": 3
}
```

✅ **What to verify**:
- ✅ Signals appear after 30 minutes
- ✅ Signal types: "Competitive", "Consumer", "Market"
- ✅ Severity levels: "info", "warning", "critical"
- ✅ Messages are actionable

---

## 🧪 Test 8: Frontend Testing

### Start Frontend:
```bash
cd frontend
npm start
```

### Expected Browser Output:

1. **Navigate to**: http://localhost:3000

2. **Fill in the form**:
   - Business Type: "AI SaaS Platform"
   - Target Market: "Tech startups in USA"
   - Monthly Budget: "$10,000"
   - Primary Goal: "Acquire 1000 users in 3 months"
   - Additional Info: "B2B focus with freemium model"

3. **Click**: "Generate AI Marketing Strategy"

4. **Wait**: 20-30 seconds (loading spinner)

5. **Expected Dashboard**:
   - ✅ Header with confidence, virality, retention scores
   - ✅ Live Agent Panel (market signals)
   - ✅ Blockchain Proof Card (with hash)
   - ✅ Execution Actions panel
   - ✅ **NEW**: Content Generation & Export panel with 4 cards:
     - 📄 Export PDF Report (Free)
     - 🎤 Generate Pitch Deck (Pro - locked)
     - 📅 Content Calendar (Pro - locked)
     - ✉️ Email Sequence (Pro - locked)
   - ✅ Market Analysis card
   - ✅ User Personas card
   - ✅ AI Insights card
   - ✅ Multi-Channel Strategies (tabs)
   - ✅ Revenue Projection card
   - ✅ Competitor Analysis card (locked)
   - ✅ Action Items cards

6. **Click**: "Export PDF Report"
   - ✅ Loading spinner appears
   - ✅ Success toast: "PDF report downloaded successfully!"
   - ✅ PDF file downloads to your Downloads folder

---

## 📊 Performance Benchmarks

| Operation | Expected Time | Status |
|-----------|--------------|--------|
| Server Startup | 2-3 seconds | ✅ |
| Health Check | <100ms | ✅ |
| Create Analysis | 20-30 seconds | ✅ (AI processing) |
| Export PDF | 2-5 seconds | ✅ |
| Generate Pitch Deck | 15-20 seconds | ✅ (AI processing) |
| Generate Calendar | 20-30 seconds | ✅ (AI processing) |
| Generate Email Seq | 10-15 seconds | ✅ (AI processing) |
| Market Signals | <200ms | ✅ |
| Background Scan | Runs every 30 min | ✅ |

---

## 🐛 Common Issues & Solutions

### Issue 1: Server won't start
```
ModuleNotFoundError: No module named 'web3'
```
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### Issue 2: PDF export fails
```
ImportError: cannot import name 'PDFGenerator'
```
**Solution**:
```bash
pip install reportlab pillow
```

### Issue 3: Analysis takes too long
```
Timeout after 60 seconds
```
**Solution**: This is normal for AI processing. Wait up to 30 seconds.

### Issue 4: Background scanner not running
**Check server logs for**:
```
INFO:scanner_service:Background scanner started
```
If missing, check `.env`:
```bash
ENABLE_BACKGROUND_SCANNER=true
```

---

## ✅ Success Checklist

After testing, you should have:

- [x] Server running on port 8001
- [x] Health check returns all services
- [x] Created at least 1 analysis
- [x] Analysis includes competitor_insights
- [x] Analysis includes blockchain_proof
- [x] Downloaded a PDF report
- [x] Generated a pitch deck (or saw the response)
- [x] Background scanner logs appear
- [x] Frontend loads and displays analysis
- [x] Content Actions Panel visible in dashboard

---

## 🎉 You're Ready!

If all tests pass, your AstraMark Enhanced platform is **fully functional** and ready for:
- ✅ Production deployment
- ✅ Adding real API keys (SERP, Alchemy)
- ✅ User authentication
- ✅ Payment integration
- ✅ Scaling to production

**Need help?** Check the documentation files:
- `QUICK_START.md`
- `ENHANCED_FEATURES.md`
- `ARCHITECTURE.md`

---

**Happy Testing! 🚀**
