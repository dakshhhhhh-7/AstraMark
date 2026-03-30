# AstraMark Testing Guide

## ✅ Current Status

**Backend**: Running on http://localhost:8001
**Frontend**: Running on http://localhost:3000
**MongoDB**: Connected successfully to new cluster

## 🧪 What to Test

### 1. Authentication Flow

#### Test User Registration
1. Open http://localhost:3000
2. Click "Sign Up" or "Register"
3. Fill in:
   - Email: test@example.com
   - Password: Test123456
   - Full Name: Test User
4. Click "Register"
5. ✅ Should create account and redirect to login or dashboard

#### Test User Login
1. Go to login page
2. Enter credentials:
   - Email: test@example.com
   - Password: Test123456
3. Click "Login"
4. ✅ Should receive JWT token and redirect to dashboard

### 2. Business Analysis (Main Feature)

#### Test AI Analysis
1. After logging in, go to the main dashboard
2. Fill in the business input form:
   - **Business Type**: "E-commerce Fashion Store"
   - **Target Market**: "Women 25-40, Urban, Middle Income"
   - **Monthly Budget**: "$2000"
   - **Primary Goal**: "Increase Online Sales"
   - **Additional Info**: "Focus on sustainable fashion"
3. Click "Analyze" or "Generate Strategy"
4. ✅ Should see:
   - Loading indicator
   - AI-generated analysis with:
     - Market overview
     - SWOT analysis
     - User personas
     - Marketing strategies (SEO, Content, Paid Ads, Social Media)
     - Revenue projections
     - AI insights
     - Confidence scores

### 3. API Endpoints to Test

#### Health Check
```bash
curl http://localhost:8001/api/
```
Expected: `{"message": "AstraMark AI Marketing Platform API - Enhanced Edition"}`

#### Register User (via API)
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "apitest@example.com",
    "password": "Test123456",
    "full_name": "API Test User"
  }'
```

#### Login (via API)
```bash
curl -X POST http://localhost:8001/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=apitest@example.com&password=Test123456"
```
Expected: JWT access token

#### Test Analysis (via API)
```bash
# First get token from login, then:
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "business_type": "SaaS Startup",
    "target_market": "B2B Tech Companies",
    "monthly_budget": "5000",
    "primary_goal": "Lead Generation",
    "additional_info": "AI-powered analytics platform"
  }'
```

### 4. Frontend Components to Test

#### Navigation
- ✅ Logo/brand name visible
- ✅ Navigation menu works
- ✅ Login/Logout buttons functional
- ✅ Protected routes redirect to login if not authenticated

#### Forms
- ✅ Input validation works
- ✅ Error messages display correctly
- ✅ Success messages show
- ✅ Loading states visible during API calls

#### Dashboard
- ✅ Analysis results display properly
- ✅ Charts/graphs render (if any)
- ✅ Data is formatted correctly
- ✅ Responsive design works on mobile

### 5. Error Handling

#### Test Invalid Login
1. Try logging in with wrong password
2. ✅ Should show error message: "Incorrect email or password"

#### Test Duplicate Registration
1. Try registering with existing email
2. ✅ Should show error: "Email already registered"

#### Test Rate Limiting
1. Make 6+ analysis requests quickly
2. ✅ Should get rate limit error (5 requests per minute)

### 6. AI Services

#### Check Which AI Service is Active
Look at backend console logs:
- If you see "Groq service available" → Groq is working
- If you see "Gemini AI Client configured" → Google AI is working
- If both fail → Falls back to mock data

#### Test with Different Business Types
Try analyzing:
- E-commerce store
- SaaS product
- Local restaurant
- Consulting service
- Mobile app
- Physical product

Each should get relevant, customized strategies.

### 7. Database Verification

#### Check MongoDB Collections
1. Open MongoDB Compass or Atlas dashboard
2. Connect to: `mongodb+srv://dakshraj:daksh123@astramark.xnxadjs.mongodb.net/`
3. Check database: `astramark_dev`
4. ✅ Should see collections:
   - `users` - registered users
   - `businesses` - business profiles
   - `analyses` - analysis results (if saved)

### 8. Payment Integration (If Implemented)

#### Test Razorpay
1. Go to pricing/payment page
2. Select a plan
3. Click "Pay Now"
4. ✅ Should open Razorpay checkout
5. Use test card: 4111 1111 1111 1111
6. ✅ Should process payment and update user status

### 9. Performance Testing

#### Check Response Times
- Registration: < 1 second
- Login: < 500ms
- Analysis: 5-15 seconds (AI processing)
- Dashboard load: < 2 seconds

#### Check Memory Usage
- Backend should use < 500MB RAM
- Frontend should load in < 3 seconds

### 10. Browser Compatibility

Test on:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Edge (latest)
- ✅ Safari (if on Mac)
- ✅ Mobile browsers (Chrome/Safari on phone)

## 🐛 Common Issues & Solutions

### Issue: "Network Error" in Frontend
**Solution**: Check backend is running on port 8001

### Issue: "Unauthorized" Error
**Solution**: Token expired, log in again

### Issue: Analysis Takes Too Long
**Solution**: Normal for AI processing, wait 10-15 seconds

### Issue: "CORS Error"
**Solution**: Check CORS_ORIGINS in backend/.env includes http://localhost:3000

### Issue: MongoDB Connection Failed
**Solution**: Check internet connection and MongoDB Atlas cluster is running

## 📊 Expected Results

### Successful Analysis Should Include:
1. **Overview**: Brief business summary
2. **Market Analysis**:
   - Market size estimate
   - Growth rate
   - Entry barriers
   - Opportunities (3+)
   - Risks (3+)
   - Strengths (2+)
   - Weaknesses (2+)
3. **User Personas**: 1-3 detailed personas
4. **AI Insights**: Pattern recognition, market gaps
5. **Strategies**: 4 channels (SEO, Content, Paid Ads, Social)
6. **Revenue Projection**: Min/max monthly estimates
7. **Scores**: Virality, retention, confidence (0-100)
8. **Verdict**: High/Medium/Low growth potential

## 🎯 Key Features to Verify

- [x] User authentication (register/login)
- [x] JWT token management
- [x] Business analysis generation
- [x] AI-powered insights
- [x] Market research data
- [x] Strategy recommendations
- [x] Revenue projections
- [x] MongoDB data persistence
- [x] Error handling
- [x] Rate limiting
- [x] CORS configuration
- [x] Responsive design

## 📝 Test Checklist

### Backend
- [ ] Server starts without errors
- [ ] MongoDB connects successfully
- [ ] API endpoints respond
- [ ] Authentication works
- [ ] Analysis generates results
- [ ] Error handling works
- [ ] Rate limiting active

### Frontend
- [ ] App loads in browser
- [ ] Registration form works
- [ ] Login form works
- [ ] Dashboard displays
- [ ] Analysis form submits
- [ ] Results display correctly
- [ ] Navigation works
- [ ] Responsive on mobile

### Integration
- [ ] Frontend connects to backend
- [ ] JWT tokens work
- [ ] Data persists in MongoDB
- [ ] Real-time updates work
- [ ] Error messages display

## 🚀 Next Steps After Testing

1. **If everything works**:
   - Start building new features
   - Add more AI capabilities
   - Enhance UI/UX
   - Add analytics

2. **If issues found**:
   - Check console logs (F12 in browser)
   - Check backend terminal output
   - Review error messages
   - Check MongoDB connection

3. **Production Deployment**:
   - Set ENVIRONMENT=production in .env
   - Update CORS origins
   - Add proper API keys
   - Enable monitoring
   - Set up CI/CD

## 📞 Support

If you encounter issues:
1. Check backend logs in terminal
2. Check browser console (F12)
3. Verify MongoDB connection
4. Check .env configuration
5. Ensure all dependencies installed

## 🎉 Success Indicators

You'll know it's working when:
- ✅ You can register and login
- ✅ Analysis generates in 5-15 seconds
- ✅ Results are detailed and relevant
- ✅ Data saves to MongoDB
- ✅ No console errors
- ✅ UI is responsive and smooth

Happy testing! 🚀
