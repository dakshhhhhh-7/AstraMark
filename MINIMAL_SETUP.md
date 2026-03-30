# 🚀 Minimal Setup Guide (No Sentry Required)

## ✅ **What You Have Ready:**
- ✅ MongoDB Atlas URL configured
- ✅ Razorpay payment gateway ready
- ✅ Groq AI service configured
- ✅ All optional services disabled

## 🎯 **Only 2 Things Left to Do:**

### 1. **Generate JWT Keys** (Required)
```bash
cd backend
python config.py
```
Copy the output and paste into your `.env` file:
```bash
JWT_SECRET_KEY=generated_key_1_here
JWT_REFRESH_SECRET_KEY=generated_key_2_here
```

### 2. **Get Google API Key** (Optional but Recommended)
```bash
# Go to: https://console.cloud.google.com
# Enable Generative AI API
# Create API Key
# Add to .env: GOOGLE_API_KEY=AIza_your_key_here
```

## 🚀 **Start the Application:**

```bash
# 1. Create virtual environment
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 2. Install dependencies (no Sentry required!)
pip install -r requirements.txt

# 3. Generate JWT keys
python config.py

# 4. Start backend
python server_enhanced.py

# 5. In another terminal, start frontend
cd frontend
yarn install
yarn start
```

## 🧪 **Test Everything Works:**

```bash
# Test health endpoint
curl http://localhost:8001/api/health

# Should return:
{
  "status": "healthy",
  "ai_services": {
    "gemini_enabled": true/false,
    "groq_enabled": true,
    "fallback_available": true
  },
  "db_connected": true
}
```

## 🎯 **What's Disabled (Intentionally):**
- ❌ **Sentry** - No error tracking (not needed for local dev)
- ❌ **SERP API** - No live competitor data (optional)
- ❌ **Stripe** - Only Razorpay enabled (sufficient for testing)

## ✅ **What Works:**
- ✅ **AI Analysis** - Groq + optional Gemini
- ✅ **Payments** - Razorpay integration
- ✅ **Database** - MongoDB Atlas
- ✅ **Authentication** - JWT tokens
- ✅ **All Core Features** - Full marketing analysis

**Your app will work perfectly without Sentry! 🎉**