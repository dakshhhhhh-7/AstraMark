"""
Unified Payment Service - Supports both Stripe and Razorpay
"""
from typing import Dict, Any, Optional, List, Literal
from fastapi import HTTPException
import logging

from config import settings
from payment_service import PaymentService
from razorpay_service import RazorpayService

logger = logging.getLogger(__name__)

PaymentGateway = Literal["stripe", "razorpay"]

class UnifiedPaymentService:
    """Unified payment service supporting multiple gateways"""
    
    def __init__(self, db):
        self.db = db
        self.stripe_service = PaymentService(db) if settings.stripe_secret_key else None
        self.razorpay_service = RazorpayService(db) if settings.razorpay_key_id else None
        self.default_gateway = settings.default_payment_gateway
        
        logger.info(f"Payment services initialized - Stripe: {bool(self.stripe_service)}, Razorpay: {bool(self.razorpay_service)}")
    
    def get_available_gateways(self) -> List[Dict[str, Any]]:
        """Get list of available payment gateways"""
        gateways = []
        
        if self.stripe_service and self.stripe_service.is_enabled():
            gateways.append({
                "id": "stripe",
                "name": "Stripe",
                "description": "International payments via credit/debit cards",
                "currencies": ["USD", "EUR", "GBP", "INR"],
                "methods": ["card", "apple_pay", "google_pay"],
                "regions": ["Global"],
                "logo": "https://stripe.com/img/v3/home/social.png"
            })
        
        if self.razorpay_service and self.razorpay_service.is_enabled():
            gateways.append({
                "id": "razorpay", 
                "name": "Razorpay",
                "description": "Indian payments via UPI, cards, wallets & banking",
                "currencies": ["INR"],
                "methods": ["card", "upi", "netbanking", "wallet"],
                "regions": ["India", "Malaysia", "Singapore"],
                "logo": "https://razorpay.com/assets/razorpay-logo.svg"
            })
        
        return gateways
    
    def get_service(self, gateway: PaymentGateway):
        """Get payment service instance for specific gateway"""
        if gateway == "stripe":
            if not self.stripe_service or not self.stripe_service.is_enabled():
                raise HTTPException(status_code=503, detail="Stripe not available")
            return self.stripe_service
        elif gateway == "razorpay":
            if not self.razorpay_service or not self.razorpay_service.is_enabled():
                raise HTTPException(status_code=503, detail="Razorpay not available")
            return self.razorpay_service
        else:
            raise HTTPException(status_code=400, detail="Invalid payment gateway")
    
    async def create_checkout_session(
        self,
        user_id: str,
        plan_id: str,
        gateway: PaymentGateway,
        success_url: str,
        cancel_url: str,
        currency: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create checkout session for specified gateway"""
        service = self.get_service(gateway)
        
        if gateway == "stripe":
            return await service.create_checkout_session(user_id, plan_id, success_url, cancel_url)
        elif gateway == "razorpay":
            # For Razorpay, we can use either subscription or payment link
            # Let's use payment link for simplicity
            return await service.create_payment_link(user_id, plan_id, success_url)
    
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        gateway: PaymentGateway,
        return_url: str
    ) -> Dict[str, Any]:
        """Create recurring subscription"""
        service = self.get_service(gateway)
        
        if gateway == "stripe":
            return await service.create_checkout_session(user_id, plan_id, return_url, return_url)
        elif gateway == "razorpay":
            return await service.create_subscription(user_id, plan_id, return_url)
    
    async def handle_webhook(
        self,
        gateway: PaymentGateway,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """Handle webhook from specified gateway"""
        service = self.get_service(gateway)
        return await service.handle_webhook(payload, signature)
    
    async def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user subscription from any gateway"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return None
        
        # Check which gateway the user is using
        if user.get("stripe_customer_id") and self.stripe_service:
            return await self.stripe_service.get_user_subscription(user_id)
        elif user.get("razorpay_customer_id") and self.razorpay_service:
            return await self.razorpay_service.get_user_subscription(user_id)
        
        # Return basic subscription info if no gateway data
        return {
            "is_premium": user.get("is_premium", False),
            "plan": user.get("subscription_plan"),
            "status": user.get("subscription_status"),
            "updated_at": user.get("subscription_updated_at"),
            "gateway": None
        }
    
    def get_plans_for_gateway(self, gateway: PaymentGateway) -> List[Dict[str, Any]]:
        """Get subscription plans for specific gateway"""
        service = self.get_service(gateway)
        return service.get_plans()
    
    def get_all_plans(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get plans from all available gateways"""
        plans = {}
        
        if self.stripe_service and self.stripe_service.is_enabled():
            plans["stripe"] = self.stripe_service.get_plans()
        
        if self.razorpay_service and self.razorpay_service.is_enabled():
            plans["razorpay"] = self.razorpay_service.get_plans()
        
        return plans
    
    def recommend_gateway(self, user_country: Optional[str] = None, currency: Optional[str] = None) -> PaymentGateway:
        """Recommend best gateway based on user location/currency"""
        # If user is from India or wants INR, recommend Razorpay
        if (user_country == "IN" or currency == "INR") and self.razorpay_service and self.razorpay_service.is_enabled():
            return "razorpay"
        
        # For international users, prefer Stripe
        if self.stripe_service and self.stripe_service.is_enabled():
            return "stripe"
        
        # Fallback to any available gateway
        if self.razorpay_service and self.razorpay_service.is_enabled():
            return "razorpay"
        
        raise HTTPException(status_code=503, detail="No payment gateways available")
    
    async def create_customer_portal_session(
        self,
        user_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Create customer portal session (Stripe only for now)"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check which gateway the user is using
        if user.get("stripe_customer_id") and self.stripe_service:
            return await self.stripe_service.create_portal_session(user_id, return_url)
        elif user.get("razorpay_customer_id"):
            # Razorpay doesn't have a customer portal, redirect to dashboard
            return {
                "portal_url": "https://dashboard.razorpay.com/",
                "message": "Please manage your subscription through Razorpay dashboard"
            }
        else:
            raise HTTPException(status_code=400, detail="No active subscription found")
    
    def get_gateway_config(self, gateway: PaymentGateway) -> Dict[str, Any]:
        """Get public configuration for frontend"""
        if gateway == "stripe" and self.stripe_service:
            return {
                "gateway": "stripe",
                "public_key": None,  # Stripe uses secret key only
                "enabled": self.stripe_service.is_enabled()
            }
        elif gateway == "razorpay" and self.razorpay_service:
            return {
                "gateway": "razorpay",
                "key_id": settings.razorpay_key_id,  # This is safe to expose
                "enabled": self.razorpay_service.is_enabled()
            }
        else:
            return {"gateway": gateway, "enabled": False}