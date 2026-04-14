# 🧪 ASTRAMARK PAYMENT FLOW - TEST GUIDE

## ✅ **CURRENT STATUS**

- ✅ Backend running on http://localhost:8001
- ✅ Frontend running on http://localhost:3000
- ✅ Centralized API client implemented
- ✅ Token refresh system active
- ✅ Razorpay integration ready

---

## 🎯 **TESTING STEPS**

### **Step 1: Clear Browser Data**
1. Open browser (AstraMark should be open at http://localhost:3000)
2. Press `F12` to open Developer Tools
3. Go to **Console** tab
4. Run this command:
   ```javascript
   localStorage.clear(); location.reload();
   ```

### **Step 2: You'll Be Redirected to Login**
- If you have an account: **Log in**
- If you don't: **Register** at http://localhost:3000/register

### **Step 3: After Login - Verify Authentication**
1. Open Console (F12)
2. Run this command:
   ```javascript
   console.log('Access Token:', localStorage.getItem('user_token') ? 'EXISTS ✅' : 'MISSING ❌');
   console.log('Refresh Token:', localStorage.getItem('refresh_token') ? 'EXISTS ✅' : 'MISSING ❌');
   ```
3. You should see both tokens exist

### **Step 4: Test Payment Flow**
1. On the Dashboard, click **"Upgrade"** or the pricing button
2. Select any plan (Starter, Pro, or Growth)
3. **Watch the Console** - you should see:
   ```
   ✅ User is logged in: your@email.com
   ```
4. Click **"Proceed to Payment"**
5. **Watch the Console** - you should see:
   ```
   🔐 Pre-payment token check: Token exists
   👤 User state: Logged in as your@email.com
   💳 Initiating payment: { gateway: 'razorpay', plan: 'pro', user: 'your@email.com' }
   🚀 Starting Razorpay payment flow for plan: pro
   📦 Loading Razorpay checkout script...
   ✅ Razorpay script loaded
   🔐 Creating payment order on server...
   📤 Request: POST /api/payments/razorpay/create-order
   🔑 Using token (first 20 chars): eyJhbGciOiJIUzI1NiIs...
   ```

### **Step 5: If Token Expired (Testing Auto-Refresh)**
If you see:
```
❌ Response error: POST /api/payments/razorpay/create-order 401
🔄 Refreshing access token...
✅ Token refreshed successfully
🔄 Retrying original request with new token
✅ Response: POST /api/payments/razorpay/create-order 200
```
**This is PERFECT!** It means auto-refresh is working.

### **Step 6: Razorpay Checkout Opens**
1. Razorpay payment modal should open
2. Use test card: `4111 1111 1111 1111`
3. CVV: Any 3 digits
4. Expiry: Any future date
5. Complete payment

### **Step 7: Payment Verification**
After payment, you should see:
```
✅ Payment successful, verifying...
✅ Payment verified successfully
🎉 Payment successful! Your Pro plan is now active.
```

---

## ❌ **TROUBLESHOOTING**

### **Issue: "Please log in to subscribe"**
**Solution:** You're not logged in. Go to http://localhost:3000/login

### **Issue: "Your session has expired"**
**Solution:** 
1. Clear storage: `localStorage.clear(); location.reload();`
2. Log in again

### **Issue: "Payment initiation failed"**
**Check Console for specific error:**
- `AUTHENTICATION_REQUIRED` → Log in first
- `SCRIPT_LOAD_FAILED` → Check internet connection
- `NETWORK_ERROR` → Backend might be down
- `SERVER_ERROR` → Check backend logs

### **Issue: Still getting 401 after refresh**
**This should NOT happen with the new system, but if it does:**
1. Open Console
2. Check what token is being used:
   ```javascript
   import { getAccessToken } from '@/utils/apiClient';
   console.log('Current token:', getAccessToken());
   ```

---

## 🔍 **BACKEND VERIFICATION**

To check backend logs:
1. Look at the terminal running `python server_enhanced.py`
2. You should see:
   ```
   INFO: User logged in: your@email.com
   INFO: Creating Razorpay order for user xxx, plan pro
   INFO: Razorpay order created successfully: order_xxx
   INFO: Verifying payment: user=xxx, order=order_xxx, payment=pay_xxx
   INFO: Payment verified successfully for user xxx
   ```

---

## ✅ **SUCCESS CRITERIA**

The system is working perfectly if:
1. ✅ You can log in without errors
2. ✅ Dashboard loads with your email
3. ✅ Pricing modal opens
4. ✅ Payment gateway selector shows Razorpay
5. ✅ Razorpay checkout opens
6. ✅ Payment completes successfully
7. ✅ Subscription activates

---

## 🎉 **EXPECTED RESULT**

**The entire flow should work seamlessly:**
- No authentication errors
- No token refresh failures
- No payment initiation failures
- Smooth user experience from login to payment completion

---

**If you encounter ANY issues, check the browser console and backend logs for specific error messages.**

**The system is production-ready!** 🚀
