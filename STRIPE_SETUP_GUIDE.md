# Real Stripe Payment Integration Setup Guide

## ✅ What's Been Implemented

### Backend (Python/FastAPI)
1. **Stripe Python SDK** installed (`stripe==13.0.1`)
2. **Payment Routes** created at `app/api/v1/stripe_routes.py`:
   - `POST /api/v1/stripe/create-payment-intent` - Creates payment intent
   - `POST /api/v1/stripe/verify-payment` - Verifies payment status
   - `GET /api/v1/stripe/config` - Returns publishable key
3. **Routes integrated** into main.py
4. **Environment variables** configured in `.env`

### Frontend (React/TypeScript)
1. **Stripe packages** installed:
   - `@stripe/stripe-js`
   - `@stripe/react-stripe-js`
2. **Payment modal** updated with real Stripe Elements
3. **CardElement** integrated for secure card input
4. **Environment variables** configured in `frontend/.env`

## 🔑 Setup Instructions

### Step 1: Get Your Stripe API Keys

1. **Sign up/Login** to Stripe: https://dashboard.stripe.com/register
2. **Activate your account** (for test mode, this is instant)
3. **Get your API keys**:
   - Go to: https://dashboard.stripe.com/test/apikeys
   - You'll see two keys:
     - **Publishable key** (starts with `pk_test_`)
     - **Secret key** (starts with `sk_test_`)

### Step 2: Configure Backend Environment

Edit `.env` file in the root directory:

```bash
# Replace these with your actual Stripe keys
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
```

**⚠️ Important**: 
- Never commit your secret key to version control
- Use test keys for development (they start with `sk_test_` and `pk_test_`)
- For production, use live keys (they start with `sk_live_` and `pk_live_`)

### Step 3: Configure Frontend Environment

Edit `frontend/.env` file:

```bash
# Replace with your actual Stripe publishable key
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here

# API Base URL (already configured)
VITE_API_BASE_URL=http://localhost:8000
```

### Step 4: Restart Both Servers

#### Backend:
```bash
# Stop the current server (Ctrl+C)
# Then restart:
py main.py
```

#### Frontend:
```bash
# Stop the current server (Ctrl+C in the frontend terminal)
# Then restart:
cd frontend
npm run dev
```

## 🧪 Testing the Integration

### Test Mode
Stripe provides test card numbers that you can use:

#### Successful Payments:
- **Card Number**: `4242 4242 4242 4242`
- **Expiry**: Any future date (e.g., `12/34`)
- **CVC**: Any 3 digits (e.g., `123`)
- **ZIP**: Any 5 digits (e.g., `12345`)

#### Test Different Scenarios:
- **Declined Card**: `4000 0000 0000 0002`
- **Insufficient Funds**: `4000 0000 0000 9995`
- **Requires Authentication (3D Secure)**: `4000 0025 0000 3155`

### Testing Steps:

1. **Open Sparks Chat**: http://localhost:5173
2. **Send 3 messages** (free limit)
3. **Payment modal appears** on 4th message
4. **Fill in payment details**:
   - Email: Any valid email
   - Name: Any name
   - Card: Use test card `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
5. **Click "Pay $9.99"**
6. **Payment processes** through real Stripe API
7. **Success!** You get unlimited access

## 📊 Monitoring Payments

### Stripe Dashboard
View all test payments at: https://dashboard.stripe.com/test/payments

You'll see:
- Payment status
- Amount
- Customer email
- Payment method
- Metadata
- Logs

## 🔒 Security Features

### Built-in Security:
✅ **PCI Compliance**: Stripe handles all card data  
✅ **Tokenization**: Card numbers never touch your server  
✅ **3D Secure**: Optional authentication for high-risk payments  
✅ **Encryption**: All data encrypted in transit and at rest  
✅ **Fraud Detection**: Stripe Radar included (even in test mode)

### What You Should Do:
- ✅ Use HTTPS in production
- ✅ Store Stripe keys in environment variables
- ✅ Never log card details
- ✅ Implement webhook handlers for reliability
- ✅ Verify payments on the backend

## 🚀 API Endpoints

### Create Payment Intent
```bash
POST http://localhost:8000/api/v1/stripe/create-payment-intent
Content-Type: application/json

{
  "amount": 999,
  "currency": "usd",
  "description": "AI Agent Premium Access"
}

Response:
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

### Verify Payment
```bash
POST http://localhost:8000/api/v1/stripe/verify-payment?payment_intent_id=pi_xxx

Response:
{
  "success": true,
  "status": "succeeded",
  "amount": 999,
  "currency": "usd",
  "payment_intent_id": "pi_xxx"
}
```

### Get Stripe Config
```bash
GET http://localhost:8000/api/v1/stripe/config

Response:
{
  "publishable_key": "pk_test_xxx"
}
```

## 🎯 How It Works

### Payment Flow:

1. **User triggers payment** (clicks button or reaches message limit)
2. **Frontend requests** payment intent from backend
3. **Backend creates** PaymentIntent via Stripe API
4. **Backend returns** client_secret to frontend
5. **Frontend displays** Stripe CardElement
6. **User enters** card details (securely tokenized by Stripe)
7. **Frontend confirms** payment using client_secret
8. **Stripe processes** payment
9. **Frontend receives** payment result
10. **Success callback** grants user access

### Architecture:
```
User Browser (Frontend)
    ↓ [Create Payment Intent Request]
Your Backend (FastAPI)
    ↓ [Create PaymentIntent]
Stripe API
    ↓ [Return client_secret]
Your Backend
    ↓ [Return client_secret]
User Browser
    ↓ [Enter card details in CardElement]
    ↓ [Confirm payment with client_secret]
Stripe API
    ↓ [Process payment]
    ↓ [Return result]
User Browser
    ↓ [Display success/error]
```

## 🐛 Troubleshooting

### "Stripe not configured" error
- Check that `.env` file has `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY`
- Restart backend server after adding keys

### CardElement not showing
- Check that `frontend/.env` has `VITE_STRIPE_PUBLISHABLE_KEY`
- Restart frontend dev server after adding key
- Check browser console for errors

### Payment fails
- Use test card: `4242 4242 4242 4242`
- Check that backend is running
- Check network tab for API errors
- Verify Stripe keys are test keys (start with `pk_test_` and `sk_test_`)

### CORS errors
- Backend CORS is configured to allow all origins in development
- In production, update CORS to allow only your frontend domain

## 📝 Next Steps for Production

### Before Going Live:

1. **Switch to Live Keys**:
   - Get live keys from https://dashboard.stripe.com/apikeys
   - Update environment variables
   - Test thoroughly

2. **Implement Webhooks**:
   - Create webhook endpoint to handle events
   - Listen for `payment_intent.succeeded`
   - Update user database on successful payment
   - Handle failed payments and refunds

3. **Add User Database**:
   - Store payment status per user
   - Check payment status on app load
   - Implement subscription management if needed

4. **Security Enhancements**:
   - Use HTTPS only
   - Implement rate limiting
   - Add authentication to payment endpoints
   - Log payment attempts for fraud detection

5. **Error Handling**:
   - Better error messages for users
   - Retry logic for network failures
   - Email notifications for failed payments

6. **Compliance**:
   - Add proper Terms of Service
   - Add Privacy Policy
   - Implement refund policy
   - Add billing information page

## 📚 Resources

- **Stripe Documentation**: https://stripe.com/docs
- **Test Cards**: https://stripe.com/docs/testing
- **Stripe Dashboard**: https://dashboard.stripe.com
- **API Reference**: https://stripe.com/docs/api
- **React Integration**: https://stripe.com/docs/stripe-js/react

## 💬 Support

If you encounter issues:
1. Check browser console for errors
2. Check backend logs
3. Check Stripe dashboard for payment attempts
4. Review this guide
5. Check Stripe documentation

---

**Status**: ✅ Real Stripe Integration Complete  
**Environment**: Development (Test Mode)  
**Payment Amount**: $9.99 (999 cents)  
**Last Updated**: October 13, 2025
