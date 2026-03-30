# 🚀 AstraMark - AI Marketing Intelligence Platform

AstraMark is a production-ready, AI-powered marketing platform that acts as your Chief Marketing Officer, Market Research Analyst, Growth Hacker, and Revenue Architect combined.

## ✨ Features

### Core Features
- 🤖 **AI-Powered Analysis** - Powered by Gemini 2.0 Flash for intelligent insights
- 📊 **Market Analysis** - Comprehensive market size, growth rate, and opportunity analysis
- 👥 **User Personas** - Detailed target audience profiles with pain points and buying triggers
- 🎯 **Multi-Channel Strategies** - Actionable strategies for SEO, Content Marketing, Paid Ads, and Social Media
- 💰 **Revenue Projections** - Data-driven financial forecasts
- 📈 **Scoring System** - Virality and retention scores for your business

### Premium Features 🔒
- 🔍 **Live Competitor Analysis** - Real-time competitor monitoring and insights
- 📄 **PDF Report Generation** - Professional, exportable marketing reports
- 🎨 **Content Generation Suite** - Pitch decks, content calendars, email sequences
- ⛓️ **Blockchain Verification** - Timestamp analyses on Polygon blockchain
- 💳 **Multi-Gateway Payments** - Stripe (Global) & Razorpay (India) support
- 📊 **Advanced Analytics** - Usage tracking and performance metrics

### Enterprise Features 🏢
- 🔐 **JWT Authentication** - Secure user management with refresh tokens
- 🚨 **Error Tracking** - Sentry integration for monitoring
- 📈 **Rate Limiting** - Tiered API limits based on subscription
- 🐳 **Docker Support** - Containerized deployment
- 🔄 **CI/CD Pipeline** - Automated testing and deployment

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **MongoDB Atlas** - Cloud NoSQL database
- **Gemini 2.0 Flash** - Google's latest AI model
- **Stripe & Razorpay** - Multi-gateway payment processing
- **JWT** - Secure authentication with refresh tokens
- **Sentry** - Error tracking and monitoring
- **Docker** - Containerization

### Frontend
- **React 19** - Modern UI library
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - Beautiful, accessible component library
- **Axios** - HTTP client with interceptors
- **React Router** - Client-side routing

### Infrastructure
- **Railway** - Backend hosting and deployment
- **Vercel** - Frontend hosting with CDN
- **MongoDB Atlas** - Managed database service
- **GitHub Actions** - CI/CD pipeline
- **Docker** - Containerization and deployment

## 🚀 Quick Start

### Development Setup

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/astramark.git
cd astramark
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python server_enhanced.py
```

3. **Frontend Setup**
```bash
cd frontend
yarn install
yarn start
```

4. **Docker Setup (Alternative)**
```bash
docker-compose up -d
```

### Production Deployment

See [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) for detailed deployment instructions.

## 📡 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/token` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user profile

### Analysis Endpoints
- `POST /api/analyze` - Generate AI marketing analysis
- `GET /api/analyses` - Get user's analyses
- `GET /api/analyses/{id}` - Get specific analysis

### Content Generation
- `POST /api/generate/pitch-deck` - Generate investor pitch deck
- `POST /api/generate/content-calendar` - Generate content calendar
- `POST /api/generate/email-sequence` - Generate email sequences

### Payment Endpoints
- `GET /api/payments/gateways` - Get available payment gateways
- `GET /api/payments/plans` - Get subscription plans by gateway
- `POST /api/payments/checkout` - Create checkout session
- `POST /api/payments/subscription` - Create recurring subscription
- `POST /api/payments/portal` - Access customer portal
- `GET /api/payments/subscription` - Get user subscription details
- `POST /api/payments/webhook/{gateway}` - Payment webhook handlers

### Export & Reports
- `GET /api/export/pdf/{id}` - Export analysis as PDF
- `GET /api/market/signals` - Get market intelligence signals

### System Endpoints
- `GET /api/health` - System health check
- `GET /docs` - Interactive API documentation

## 💳 Subscription Plans

### Global Pricing (Stripe)
| Plan | Price (USD) | Features |
|------|-------------|----------|
| **Starter** | $19/month | Basic analysis, 5 reports/month |
| **Pro** | $49/month | Full features, 30 reports/month, PDF export |
| **Growth** | $99/month | Advanced analytics, 100 reports/month, content generation |
| **Enterprise** | Custom | API access, white-label, unlimited usage |

### India Pricing (Razorpay)
| Plan | Price (INR) | Features |
|------|-------------|----------|
| **Starter** | ₹1,499/month | Basic analysis, 5 reports/month |
| **Pro** | ₹3,999/month | Full features, 30 reports/month, PDF export |
| **Growth** | ₹7,999/month | Advanced analytics, 100 reports/month, content generation |
| **Enterprise** | Custom | API access, white-label, unlimited usage |

**Payment Methods:**
- **Stripe**: Credit/Debit Cards, Apple Pay, Google Pay (Global)
- **Razorpay**: UPI, Net Banking, Wallets, Cards (India + International)

## 🔐 Security Features

- ✅ JWT authentication with refresh tokens
- ✅ Rate limiting per subscription tier
- ✅ Input validation and sanitization
- ✅ CORS protection
- ✅ Environment-based configuration
- ✅ Secure password hashing
- ✅ API key management
- ✅ Error tracking and monitoring

## 📊 Monitoring & Analytics

- **Health Checks** - Real-time system status monitoring
- **Error Tracking** - Sentry integration for error reporting
- **Usage Analytics** - Track API usage per user/plan
- **Performance Metrics** - Request timing and success rates
- **Payment Tracking** - Subscription and billing analytics

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests (if implemented)
cd frontend
yarn test
```

## 🚀 Deployment

### Automated Deployment
- **GitHub Actions** - Automated CI/CD pipeline
- **Railway** - Backend deployment with auto-scaling
- **Vercel** - Frontend deployment with CDN
- **Docker** - Containerized applications

### Manual Deployment
```bash
# Build and deploy backend
docker build -t astramark-backend ./backend
docker run -p 8001:8001 astramark-backend

# Build and deploy frontend
cd frontend && yarn build
# Deploy build/ folder to your hosting service
```

## 📈 Performance

- **Response Time** - < 2s for AI analysis
- **Uptime** - 99.9% availability target
- **Scalability** - Auto-scaling based on demand
- **Caching** - Redis caching for improved performance

## 🔧 Configuration

### Required Environment Variables

**Backend (.env)**:
```bash
# Database
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/db
DB_NAME=astramark_prod

# Authentication
JWT_SECRET_KEY=your-32-char-secret-key
JWT_REFRESH_SECRET_KEY=your-different-32-char-secret

# AI Services
GOOGLE_API_KEY=your-google-api-key

# Payments
STRIPE_SECRET_KEY=sk_live_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Monitoring
SENTRY_DSN=https://your-sentry-dsn

# App Settings
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
```

**Frontend (.env)**:
```bash
REACT_APP_BACKEND_URL=https://your-api-domain.com
REACT_APP_ENVIRONMENT=production
```

## 📞 Support & Documentation

- **API Docs**: `/docs` endpoint with interactive Swagger UI
- **Production Setup**: [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

Commercial License - See LICENSE file for details

## 🙏 Acknowledgments

- Powered by Google's Gemini 2.0 Flash
- UI components from Shadcn/UI
- Icons from Lucide React
- Built with FastAPI and React

---

**Made with ⚡ by the AstraMark Team**

🌟 **Star this repo if you find it useful!**

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
