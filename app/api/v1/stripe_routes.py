"""
Stripe Payment Routes for GeoSpark
"""

import logging
import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import stripe
from dotenv import load_dotenv

from app.core.security import get_current_user

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Stripe with your secret key
# Get from environment variable for security
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
logger.info(f"Stripe API key loaded: {'Yes' if stripe.api_key else 'No'}")

# Create router
router = APIRouter(prefix="/stripe", tags=["stripe"])

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "weekly": {
        "amount": 499,  # $4.99/week
        "interval": "week",
        "description": "Weekly Premium Access"
    },
    "monthly": {
        "amount": 1499,  # $14.99/month
        "interval": "month",
        "description": "Monthly Premium Access"
    },
    "yearly": {
        "amount": 9999,  # $99.99/year (save ~44%)
        "interval": "year",
        "description": "Yearly Premium Access"
    }
}

# Pydantic models
class CreatePaymentIntentRequest(BaseModel):
    plan: str = Field(..., description="Subscription plan: 'weekly', 'monthly', or 'yearly'")
    currency: str = Field(default="usd", description="Currency code")

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str

@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: CreatePaymentIntentRequest
):
    """
    Create a Stripe Payment Intent for processing payments
    Supports weekly, monthly, and yearly subscription plans
    """
    try:
        # Validate plan
        if request.plan not in SUBSCRIPTION_PLANS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid plan. Choose from: {', '.join(SUBSCRIPTION_PLANS.keys())}"
            )
        
        plan = SUBSCRIPTION_PLANS[request.plan]
        
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=plan["amount"],
            currency=request.currency,
            description=plan["description"],
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={
                'product': 'ai_agent_access',
                'type': 'premium_subscription',
                'plan': request.plan,
                'interval': plan["interval"]
            }
        )
        
        logger.info(f"Payment Intent created: {intent.id}")
        
        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            payment_intent_id=intent.id
        )
        
    except stripe._error.CardError as e:
        # Since it's a decline, stripe._error.CardError will be caught
        logger.error(f"Card error: {e}")
        raise HTTPException(status_code=402, detail=str(e))
    except stripe._error.RateLimitError as e:
        # Too many requests made to the API too quickly
        logger.error(f"Rate limit error: {e}")
        raise HTTPException(status_code=429, detail="Too many requests")
    except stripe._error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        logger.error(f"Invalid request error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except stripe._error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Stripe authentication failed")
    except stripe._error.APIConnectionError as e:
        # Network communication with Stripe failed
        logger.error(f"API connection error: {e}")
        raise HTTPException(status_code=503, detail="Network error")
    except stripe._error.StripeError as e:
        # Generic Stripe error
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Payment processing error")
    except Exception as e:
        # Something else happened
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-payment")
async def verify_payment(
    payment_intent_id: str
):
    """
    Verify a payment was successful
    """
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if intent.status == 'succeeded':
            return {
                "success": True,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
                "payment_intent_id": intent.id
            }
        else:
            return {
                "success": False,
                "status": intent.status,
                "payment_intent_id": intent.id
            }
            
    except stripe._error.StripeError as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error verifying payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_stripe_config():
    """
    Get Stripe publishable key and subscription plans for frontend
    """
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    
    if not publishable_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    return {
        "publishable_key": publishable_key,
        "plans": SUBSCRIPTION_PLANS
    }
