# 🚀 AstraMark Production Setup Guide

This guide walks you through setting up AstraMark for production deployment.

## 📋 Prerequisites

Before starting, ensure you have accounts for:
- [MongoDB Atlas](https://www.mongodb.com/atlas) (Database)
- [Google Cloud Console](https://console.cloud.google.com) (AI Services)
- [Stripe](https://dashboard.stripe.com) (Payments)
- [Sentry](https://sentry.io) (Error Tracking)
- [Railway](https://railway.app) or [Render](https://render.com) (Backend Hosting)
- [Vercel](https://vercel.com) (Frontend Hosting)

## 🔧 Step-by-Step Setup

### 1. MongoDB Atlas Setup

1. **Create Account**: Sign up at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Create Cluster**: 
   - Choose M10 cluster (recommended for production)
   - Select your preferred region
   - Name it `astramark-prod`
3. **Database Access**:
   - Create database user with read/write permissions
   - Note down username and password
4. **Network Access**:
   - Add `0.0.0.0/0` for Railway/Render access
   - Or add specific IP ranges for better security
5. **Get Connection String**:
   ```
   mongodb+srv://<username>:<password>@astramark-prod.xxxxx.mongodb.net/astramark_prod
   ```

### 2. Google Cloud Console Setup

1. **Create Project**: Go to [Google Cloud Console](https://console.cloud.google.com)
2. **Enable APIs**:
   - Generative AI API
   - Vertex AI API (if using)
3. **Create API Key**:
   - Go to "Credentials" → "Create Credentials" → "API Key"
   - Restrict key to Generative AI API
   - Note down the API key

### 3. Payment Gateway Setup (Stripe & Razorpay)

#### Stripe Setup (International)
1. **Create Account**: Sign up at [Stripe Dashboard](https://dashboard.stripe.com)
2. **Get API Keys**:
   - Go to "Developers" → "API Keys"
   - Copy "Secret key" (starts with `sk_live_` for production)
3. **Create Products**:
   ```bash
   # Create products for each plan
   Starter Plan: $19/month
   Pro Plan: $49/month  
   Growth Plan: $99/month
   ```
4. **Setup Webhooks**:
   - Go to "Developers" → "Webhooks"
   - Add endpoint: `https://your-api-domain.com/api/payments/webhook/stripe`
   - Select events: `checkout.session.completed`, `customer.subscription.updated`, etc.
   - Note down webhook secret

#### Razorpay Setup (India & International)
1. **Create Account**: Sign up at [Razorpay Dashboard](https://dashboard.razorpay.com)
2. **Get API Keys**:
   - Go to "Settings" → "API Keys"
   - Generate and copy "Key ID" and "Key Secret"
3. **Create Plans** (Optional - auto-created by API):
   ```bash
   # Indian pricing
   Starter Plan: ₹1,499/month
   Pro Plan: ₹3,999/month  
   Growth Plan: ₹7,999/month
   ```
4. **Setup Webhooks**:
   - Go to "Settings" → "Webhooks"
   - Add endpoint: `https://your-api-domain.com/api/payments/webhook/razorpay`
   - Select events: `payment.captured`, `subscription.activated`, etc.
   - Note down webhook secret

### 4. Sentry Setup

1. **Create Account**: Sign up at [Sentry](https://sentry.io)
2. **Create Project**: 
   - Choose "FastAPI" as platform
   - Name it "astramark-backend"
3. **Get DSN**: Copy the DSN from project settings

### 5. Backend Deployment (Railway)

1. **Connect Repository**: 
   - Go to [Railway](https://railway.app)
   - Connect your GitHub repository
   - Select the backend folder

2. **Environment Variables**:
   ```bash
   # Database
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/astramark_prod
   DB_NAME=astramark_prod
   
   # Security
   JWT_SECRET_KEY=<generate-32-char-secret>
   JWT_REFRESH_SECRET_KEY=<generate-different-32-char-secret>
   
   # AI Services
   GOOGLE_API_KEY=<your-google-api-key>
   
   # Payment Gateways (Choose one or both)
   # Stripe (International)
   STRIPE_SECRET_KEY=<your-stripe-secret-key>
   STRIPE_WEBHOOK_SECRET=<your-stripe-webhook-secret>
   
   # Razorpay (India & International)  
   RAZORPAY_KEY_ID=<your-razorpay-key-id>
   RAZORPAY_KEY_SECRET=<your-razorpay-key-secret>
   RAZORPAY_WEBHOOK_SECRET=<your-razorpay-webhook-secret>
   
   # Default payment gateway
   DEFAULT_PAYMENT_GATEWAY=stripe
   
   # Monitoring
   SENTRY_DSN=<your-sentry-dsn>
   
   # App Settings
   ENVIRONMENT=production
   DEBUG=false
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Generate Secret Keys**:
   ```bash
   # Run this in backend directory to generate secure keys
   python config.py
   ```

### 6. Frontend Deployment (Vercel)

1. **Connect Repository**:
   - Go to [Vercel](https://vercel.com)
   - Import your GitHub repository
   - Select the frontend folder

2. **Environment Variables**:
   ```bash
   REACT_APP_BACKEND_URL=https://your-railway-app.railway.app
   ```

3. **Build Settings**:
   - Build Command: `yarn build`
   - Output Directory: `build`
   - Install Command: `yarn install`

### 7. Domain Setup

1. **Custom Domain**: Add your domain in Vercel dashboard
2. **SSL Certificate**: Vercel provides automatic SSL
3. **DNS Configuration**: Point your domain to Vercel

## 🔐 Security Checklist

- [ ] All API keys are in environment variables (not code)
- [ ] JWT secrets are 32+ characters and unique
- [ ] MongoDB has proper access controls
- [ ] CORS is configured for your domain only
- [ ] Stripe webhooks are properly secured
- [ ] Sentry is configured for error tracking

## 📊 Monitoring Setup

### Health Checks
- Backend: `https://your-api-domain.com/api/health`
- Frontend: `https://your-domain.com/health`

### Uptime Monitoring
Set up monitoring with:
- [UptimeRobot](https://uptimerobot.com)
- [Pingdom](https://pingdom.com)
- [StatusPage](https://statuspage.io)

## 💰 Cost Estimation

### Monthly Infrastructure Costs:
- **MongoDB Atlas M10**: ~$57/month
- **Railway Pro**: ~$20/month
- **Vercel Pro**: ~$20/month
- **Sentry**: ~$26/month
- **Domain**: ~$12/year
- **Total**: ~$125/month

### Usage-Based Costs:
- **Google AI API**: ~$0.50 per 1K requests
- **Stripe**: 2.9% + $0.30 per transaction

## 🚀 Deployment Commands

### Local Testing:
```bash
# Start with Docker
docker-compose up -d

# Or start services individually
cd backend && python server_enhanced.py
cd frontend && yarn start
```

### Production Deploy:
```bash
# Backend (Railway auto-deploys on git push)
git push origin main

# Frontend (Vercel auto-deploys on git push)  
git push origin main
```

## 🔧 Post-Deployment

1. **Test All Endpoints**: Use the API documentation at `/docs`
2. **Verify Payments**: Test subscription flow end-to-end
3. **Check Monitoring**: Ensure Sentry is receiving events
4. **Load Testing**: Test with expected traffic volume
5. **Backup Strategy**: Set up MongoDB Atlas backups

## 📞 Support

If you encounter issues:
1. Check the logs in Railway/Vercel dashboards
2. Monitor Sentry for errors
3. Verify all environment variables are set correctly
4. Test API endpoints individually

---

**🎉 Congratulations! Your AstraMark platform is now production-ready!**