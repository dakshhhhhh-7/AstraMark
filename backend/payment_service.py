"""
Stripe Payment Integration Service
"""
import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import HTTPException
import logging

from config import settings

# Initialize Stripe
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key

logger = logging.getLogger(__name__)

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: int  # in cents
    currency: str = "usd"
    interval: str = "month"
    features: List[str]
    stripe_price_id: Optional[str] = None
    popular: bool = False

class PaymentService:
    """Stripe payment service"""
    
    # Subscription plans
    PLANS = {
        "starter": SubscriptionPlan(
            id="starter",
            name="Starter",
            price=1900,  # $19.00
            features=[
                "Basic marketing strategies",
                "Limited reports", 
                "5 analyses/month"
            ],
            stripe_price_id="price_starter_monthly"
        ),
        "pro": SubscriptionPlan(
            id="pro",
            name="Pro", 
            price=4900,  # $49.00
            features=[
                "Full marketing + data analysis",
                "Business plans",
                "Competitor research",
                "30 analyses/month",
                "Live market data",
                "PDF exports"
            ],
            stripe_price_id="price_pro_monthly",
            popular=True
        ),
        "growth": SubscriptionPlan(
            id="growth",
            name="Growth",
            price=9900,  # $99.00
            features=[
                "Advanced analytics",
                "Revenue forecasting", 
                "Automation planning",
                "Export reports (PDF/Excel)",
                "100 analyses/month",
                "Pitch deck generator",
                "Content calendar",
                "Email sequences"
            ],
            stripe_price_id="price_growth_monthly"
        )
    }
    
    def __init__(self, db):
        self.db = db
        if not settings.stripe_secret_key:
            logger.warning("Stripe not configured - payments disabled")
    
    def is_enabled(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(settings.stripe_secret_key)
    
    async def create_customer(self, user_id: str, email: str, name: Optional[str] = None) -> str:
        """Create Stripe customer"""
        if not self.is_enabled():
            raise HTTPException(status_code=503, detail="Payment service not available")
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id}
            )
            
            # Save customer ID to database
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"stripe_customer_id": customer.id}}
            )
            
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_checkout_session(
        self, 
        user_id: str, 
        plan_id: str, 
        success_url: str, 
        cancel_url: str
    ) -> Dict[str, Any]:
        """Create Stripe checkout session"""
        if not self.is_enabled():
            raise HTTPException(status_code=503, detail="Payment service not available")
        
        if plan_id not in self.PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        plan = self.PLANS[plan_id]
        
        try:
            # Get or create customer
            user = await self.db.users.find_one({"id": user_id})
            customer_id = user.get("stripe_customer_id")
            
            if not customer_id:
                customer_id = await self.create_customer(
                    user_id, user["email"], user.get("full_name")
                )
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": user_id,
                    "plan_id": plan_id
                }
            )
            
            return {
                "checkout_url": session.url,
                "session_id": session.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Checkout session creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_portal_session(self, user_id: str, return_url: str) -> Dict[str, Any]:
        """Create Stripe customer portal session"""
        if not self.is_enabled():
            raise HTTPException(status_code=503, detail="Payment service not available")
        
        try:
            user = await self.db.users.find_one({"id": user_id})
            customer_id = user.get("stripe_customer_id")
            
            if not customer_id:
                raise HTTPException(status_code=400, detail="No payment account found")
            
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            
            return {"portal_url": session.url}
        except stripe.error.StripeError as e:
            logger.error(f"Portal session creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        if not settings.stripe_webhook_secret:
            raise HTTPException(status_code=400, detail="Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        if event["type"] == "checkout.session.completed":
            await self._handle_checkout_completed(event["data"]["object"])
        elif event["type"] == "customer.subscription.updated":
            await self._handle_subscription_updated(event["data"]["object"])
        elif event["type"] == "customer.subscription.deleted":
            await self._handle_subscription_deleted(event["data"]["object"])
        elif event["type"] == "invoice.payment_succeeded":
            await self._handle_payment_succeeded(event["data"]["object"])
        elif event["type"] == "invoice.payment_failed":
            await self._handle_payment_failed(event["data"]["object"])
        
        return {"status": "success"}
    
    async def _handle_checkout_completed(self, session):
        """Handle successful checkout"""
        user_id = session["metadata"]["user_id"]
        plan_id = session["metadata"]["plan_id"]
        
        # Update user subscription
        await self.db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "is_premium": True,
                    "subscription_plan": plan_id,
                    "subscription_status": "active",
                    "stripe_subscription_id": session["subscription"],
                    "subscription_updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"User {user_id} subscribed to {plan_id}")
    
    async def _handle_subscription_updated(self, subscription):
        """Handle subscription updates"""
        customer_id = subscription["customer"]
        
        # Find user by customer ID
        user = await self.db.users.find_one({"stripe_customer_id": customer_id})
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        # Update subscription status
        await self.db.users.update_one(
            {"id": user["id"]},
            {
                "$set": {
                    "subscription_status": subscription["status"],
                    "subscription_updated_at": datetime.now(timezone.utc)
                }
            }
        )
    
    async def _handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation"""
        customer_id = subscription["customer"]
        
        # Find user by customer ID
        user = await self.db.users.find_one({"stripe_customer_id": customer_id})
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return
        
        # Downgrade user to free plan
        await self.db.users.update_one(
            {"id": user["id"]},
            {
                "$set": {
                    "is_premium": False,
                    "subscription_plan": None,
                    "subscription_status": "canceled",
                    "subscription_updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"User {user['id']} subscription canceled")
    
    async def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        customer_id = invoice["customer"]
        
        # Find user by customer ID
        user = await self.db.users.find_one({"stripe_customer_id": customer_id})
        if not user:
            return
        
        # Log payment
        await self.db.payments.insert_one({
            "user_id": user["id"],
            "stripe_invoice_id": invoice["id"],
            "amount": invoice["amount_paid"],
            "currency": invoice["currency"],
            "status": "succeeded",
            "created_at": datetime.now(timezone.utc)
        })
    
    async def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        customer_id = invoice["customer"]
        
        # Find user by customer ID
        user = await self.db.users.find_one({"stripe_customer_id": customer_id})
        if not user:
            return
        
        # Log failed payment
        await self.db.payments.insert_one({
            "user_id": user["id"],
            "stripe_invoice_id": invoice["id"],
            "amount": invoice["amount_due"],
            "currency": invoice["currency"],
            "status": "failed",
            "created_at": datetime.now(timezone.utc)
        })
        
        # Optionally send notification email
        logger.warning(f"Payment failed for user {user['id']}")
    
    async def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current subscription details"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return None
        
        subscription_data = {
            "is_premium": user.get("is_premium", False),
            "plan": user.get("subscription_plan"),
            "status": user.get("subscription_status"),
            "updated_at": user.get("subscription_updated_at")
        }
        
        if user.get("stripe_subscription_id") and self.is_enabled():
            try:
                stripe_sub = stripe.Subscription.retrieve(user["stripe_subscription_id"])
                subscription_data.update({
                    "current_period_end": stripe_sub["current_period_end"],
                    "cancel_at_period_end": stripe_sub["cancel_at_period_end"]
                })
            except stripe.error.StripeError:
                pass
        
        return subscription_data
    
    def get_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans"""
        return [
            {
                "id": plan.id,
                "name": plan.name,
                "price": plan.price / 100,  # Convert to dollars
                "currency": plan.currency,
                "interval": plan.interval,
                "features": plan.features,
                "popular": plan.popular
            }
            for plan in self.PLANS.values()
        ]