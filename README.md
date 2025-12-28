# 🚀 AstraMark - AI Marketing Intelligence Platform

AstraMark is an autonomous AI-powered marketing platform that acts as your Chief Marketing Officer, Market Research Analyst, Growth Hacker, and Revenue Architect combined.

## ✨ Features

### Core Features (MVP)
- 🤖 **AI-Powered Analysis** - Powered by Gemini 2.0 Flash for intelligent insights
- 📊 **Market Analysis** - Comprehensive market size, growth rate, and opportunity analysis
- 👥 **User Personas** - Detailed target audience profiles with pain points and buying triggers
- 🎯 **Multi-Channel Strategies** - Actionable strategies for SEO, Content Marketing, Paid Ads, and Social Media
- 💰 **Revenue Projections** - Data-driven financial forecasts
- 📈 **Scoring System** - Virality and retention scores for your business
- 💎 **Freemium Model** - Basic features free, advanced insights with Pro

### Premium Features 🔒
- Deep competitor analysis
- Advanced market intelligence
- Unlimited strategy generation
- Priority AI processing

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **MongoDB** - NoSQL database for flexible data storage
- **Gemini 2.0 Flash** - Google's latest AI model via Emergent LLM Key
- **Motor** - Async MongoDB driver

### Frontend
- **React 19** - Modern UI library
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - Beautiful, accessible component library
- **Axios** - HTTP client
- **Sonner** - Toast notifications

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Emergent LLM Key (included)

### Installation

1. **Backend Setup**
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Frontend Setup**
```bash
cd /app/frontend
yarn install
```

3. **Environment Variables**

Backend (`.env`):
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=*
EMERGENT_LLM_KEY=sk-emergent-65c2d5d8f865cF9E79
```

Frontend (`.env`):
```
REACT_APP_BACKEND_URL=https://astramark.preview.emergentagent.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

### Running the Application

**Using Supervisor (Production)**:
```bash
sudo supervisorctl restart all
```

**Manual (Development)**:

Backend:
```bash
cd /app/backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

Frontend:
```bash
cd /app/frontend
yarn start
```

## 📡 API Endpoints

### Health Check
```
GET /api/health
```

### Generate Analysis
```
POST /api/analyze
Content-Type: application/json

{
  "business_type": "SaaS Platform",
  "target_market": "Small businesses in USA",
  "monthly_budget": "$5,000",
  "primary_goal": "Increase user signups by 100%",
  "additional_info": "B2B focus with freemium model"
}
```

### Get Analyses
```
GET /api/analyses?limit=10
```

### Get Specific Analysis
```
GET /api/analyses/{analysis_id}
```

### Get Business Profiles
```
GET /api/businesses?limit=10
```

## 🎨 UI Components

The dashboard includes:
- **Business Input Form** - Clean, intuitive form for business details
- **Market Opportunity Card** - Market size, growth, opportunities, and risks
- **User Personas Card** - Detailed target audience profiles
- **AI Insights Card** - Pattern recognition and strategic insights
- **Strategy Cards** - Channel-specific marketing strategies with tabs
- **Revenue Projection Card** - Min/max monthly revenue forecasts
- **Action Items** - Biggest opportunity, risk, and next steps
- **Premium Locks** - Upgrade prompts for locked features

## 🔐 Freemium Model

### Free Tier
- Basic market analysis
- 1-2 user personas
- Core channel strategies
- Revenue projections

### Pro Tier 💎
- Advanced AI insights
- Unlimited analyses
- Competitor deep-dive
- Priority processing
- Advanced metrics

## 📊 Data Models

### Business Profile
```python
{
  "id": "uuid",
  "business_type": "string",
  "target_market": "string",
  "monthly_budget": "string",
  "primary_goal": "string",
  "additional_info": "string",
  "created_at": "datetime"
}
```

### Analysis Result
```python
{
  "id": "uuid",
  "business_id": "uuid",
  "overview": "string",
  "market_analysis": { ... },
  "user_personas": [ ... ],
  "ai_insights": [ ... ],
  "strategies": [ ... ],
  "revenue_projection": { ... },
  "virality_score": "int",
  "retention_score": "int",
  "ai_verdict": "string",
  "confidence_score": "int",
  "biggest_opportunity": "string",
  "biggest_risk": "string",
  "next_action": "string",
  "is_premium": "boolean",
  "created_at": "datetime"
}
```

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8001/api/health

# Test analysis
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "E-commerce",
    "target_market": "Young professionals",
    "monthly_budget": "₹50,000",
    "primary_goal": "Increase sales"
  }'
```

### Test Frontend
1. Navigate to http://localhost:3000
2. Fill in the business form
3. Click "Generate AI Marketing Strategy"
4. View the comprehensive analysis dashboard

## 🎯 Key Features Explained

### AI Analysis Engine
- Uses Gemini 2.0 Flash for intelligent analysis
- Generates comprehensive strategies based on business context
- Provides confidence scoring for all insights
- Real-time processing with async architecture

### Multi-Channel Strategies
Each channel includes:
- **Strategy** - Detailed approach and tactics
- **Content Ideas** - Specific content suggestions
- **Posting Schedule** - Frequency and timing
- **KPI Benchmarks** - Measurable success metrics

### Scoring System
- **Virality Score** (0-100) - Potential for rapid growth
- **Retention Score** (0-100) - Long-term user retention potential
- **Confidence Score** (0-100) - AI's confidence in the analysis

## 🔄 Architecture

```
┌─────────────────┐
│   React UI      │
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   FastAPI       │
│  (Port 8001)    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────────┐
│MongoDB │  │ Gemini API │
└────────┘  └────────────┘
```

## 🚧 Future Enhancements

- [ ] User authentication and accounts
- [ ] Payment integration (Stripe)
- [ ] Web search integration for real-time data
- [ ] Competitor tracking dashboard
- [ ] Email marketing automation
- [ ] Social media scheduler
- [ ] Analytics and reporting
- [ ] Team collaboration features
- [ ] Export reports to PDF
- [ ] API for third-party integrations

## 📝 Notes

- All backend API routes must be prefixed with `/api` for proper routing
- Frontend uses environment variable `REACT_APP_BACKEND_URL` for API calls
- MongoDB connection uses `MONGO_URL` from backend environment
- AI responses are parsed and structured into consistent data models
- Premium features are UI-locked but can be enabled via `premium=true` flag

## 🤝 Contributing

This is an MVP built for demonstration. For production use:
1. Add proper error handling and validation
2. Implement user authentication
3. Add rate limiting
4. Set up monitoring and logging
5. Add comprehensive testing
6. Implement caching layer
7. Add security headers and CORS restrictions

## 📄 License

Built on the Emergent Platform

## 🙏 Acknowledgments

- Powered by Google's Gemini 2.0 Flash
- UI components from Shadcn/UI
- Icons from Lucide React
- Built with FastAPI and React

---

**Made with ⚡ by Emergent AI**
