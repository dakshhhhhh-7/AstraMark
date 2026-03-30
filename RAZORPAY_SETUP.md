# 🚀 Razorpay Quick Setup Guide

## ✅ What You Need Right Now (Minimum)

Just add these 2 values to your `backend/.env` file:

```bash
RAZORPAY_KEY_ID=rzp_test_your_actual_key_id
RAZORPAY_KEY_SECRET=your_actual_key_secret
DEFAULT_PAYMENT_GATEWAY=razorpay
```

**That's it!** The system will work without the webhook secret for development.

## 🔧 Step-by-Step Setup

### 1. Get Your Razorpay Keys
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Login with your account
3. Go to **Settings** → **API Keys**
4. Copy your **Key ID** (starts with `rzp_test_`)
5. Copy your **Key Secret**

### 2. Update Your .env File
```bash
# Replace with your actual values
RAZORPAY_KEY_ID=rzp_test_1234567890abcdef
RAZORPAY_KEY_SECRET=your_actual_secret_key_here
DEFAULT_PAYMENT_GATEWAY=razorpay
```

### 3. Test the Integration
```bash
# Start your backend
cd backend
python server_enhanced.py

# Test the payment gateways endpoint
curl http://localhost:8001/api/payments/gateways
```

You should see Razorpay listed as an available gateway!

## 🔒 Webhook Secret (Optional - For Production)

### When You Need It:
- **Development**: Not required (payments still work)
- **Production**: Highly recommended for security

### How to Set It Up Later:
1. Go to **Settings** → **Webhooks** in Razorpay Dashboard
2. Click **Create Webhook**
3. Add URL: `https://your-domain.com/api/payments/webhook/razorpay`
4. Select events:
   - `payment.captured`
   - `payment.failed`
   - `subscription.activated`
   - `subscription.cancelled`
5. Copy the **Webhook Secret**
6. Add to `.env`: `RAZORPAY_WEBHOOK_SECRET=your_webhook_secret`

## 🧪 Testing Payments

### Test Card Numbers (Razorpay):
```bash
# Success
Card: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date

# Failure
Card: 4000 0000 0000 0002
```

### Test UPI IDs:
```bash
# Success: success@razorpay
# Failure: failure@razorpay
```

## 💰 Pricing Comparison

| Gateway | Starter | Pro | Growth |
|---------|---------|-----|--------|
| **Stripe** | $19 | $49 | $99 |
| **Razorpay** | ₹1,499 | ₹3,999 | ₹7,999 |

## 🚀 Quick Start Commands

```bash
# 1. Install Razorpay SDK
pip install razorpay

# 2. Update your .env with Razorpay keys
# 3. Start the server
python server_enhanced.py

# 4. Test in browser
# Go to http://localhost:3000
# Click on pricing and select Razorpay
```

## ❓ Troubleshooting

### "Payment service not available"
- Check your `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are set
- Ensure no extra spaces in the .env file

### "Invalid gateway"
- Make sure `DEFAULT_PAYMENT_GATEWAY=razorpay` is set
- Restart your backend server after changing .env

### Webhook errors (can ignore for now)
- Webhooks are optional for development
- You'll see warnings in logs but payments will still work

## 🎉 Success!

Once set up, users will see:
- **Gateway Selection**: Choose between Stripe and Razorpay
- **Indian Pricing**: ₹1,499 instead of $19
- **Local Payment Methods**: UPI, Net Banking, Wallets
- **Seamless Experience**: Same UI for both gateways

**You're ready to accept payments in India! 🇮🇳**