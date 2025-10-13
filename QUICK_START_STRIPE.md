# 🔑 Quick Start: Add Your Stripe Keys

## Step 1: Get Stripe Keys
Visit: https://dashboard.stripe.com/test/apikeys

You'll see:
- **Publishable key**: pk_test_xxxxx... (safe to expose)
- **Secret key**: sk_test_xxxxx... (keep private!)

## Step 2: Update Backend .env

Open: `.env` (root directory)

Find these lines:
```
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
```

Replace with your actual keys:
```
STRIPE_SECRET_KEY=sk_test_51xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxx
```

## Step 3: Update Frontend .env

Open: `frontend/.env`

Find this line:
```
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
```

Replace with your publishable key:
```
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxx
```

## Step 4: Restart Servers

**Backend:**
```bash
# Press Ctrl+C to stop
py main.py
```

**Frontend:**
```bash
# Press Ctrl+C to stop
cd frontend
npm run dev
```

## Step 5: Test Payment

Use Stripe test card:
- Card: `4242 4242 4242 4242`
- Expiry: `12/34`
- CVC: `123`

✅ Done! Your real Stripe integration is live!
