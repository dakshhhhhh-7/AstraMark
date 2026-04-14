"""
Razorpay Payment Integration Service
"""
import razorpay
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import HTTPException
import logging
import hmac
import hashlib

from config import settings

logger = logging.getLogger(__name__)

class RazorpayService:
    """Razorpay payment service"""
    
    def __init__(self, db):
        self.db = db
        self.client = None
        
        if settings.razorpay_key_id and settings.razorpay_key_secret:
            self.client = razorpay.Client(
                auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
            )
            logger.info("Razorpay client initialized")
        else:
            logger.warning("Razorpay not configured - payments disabled")
    
    def is_enabled(self) -> bool:
        """Check if Razorpay is properly configured"""
        return bool(self.client)
    
    async def create_customer(self, user_id: str, email: str, name: Optional[str] = None, phone: Optional[str] = None) -> str:
        """Create Razorpay customer"""
        if not self.is_enabled():
            raise HTTPException(status_code=503, detail="Payment service not available")
        
        try:
            customer_data = {
                "name": name or email.split('@')[0],
                "email": email,
                "notes": {"user_id": user_id}
            }
            
            if phone:
                customer_data["contact"] = phone
            
            customer = self.client.customer.create(customer_data)
            
            # Save customer ID to database
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"razorpay_customer_id": customer["id"]}}
            )
            
            return customer["id"]
        except Exception as e:
            logger.error(f"Razorpay customer creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_subscription(
        self, 
        user_id: str, 
        plan_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Create Razorpay subscription"""
        if not self.is_enabled():
            raise HTTPException(status_code=503, detail="Payment service not available")
        
        # Plan mapping (amounts in paise - 1 INR = 100 paise)
        plans = {
            "starter": {"amount": 149900, "period": "monthly", "interval": 1},  # ₹1499/month
            "pro": {"amount": 399900, "period": "monthly", "interval": 1},     # ₹3999/month  
            "growth": {"amount": 799900, "period": "monthly", "interval": 1}   # ₹7999/month
        }
        
        if plan_id not in plans:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        plan_data = plans[plan_id]
        
        try:
            # Get or create customer
            user = await self.db.users.find_one({"id": user_id})
            customer_id = user.get("razorpay_customer_id")
            
            if not customer_id:
                customer_id = await self.create_customer(
                    user_id, user["email"], user.get("full_name")
                )
            
            # Create Razorpay plan if not exists
            razorpay_plan_id = f"plan_{plan_id}_monthly"
            try:
                plan = self.client.plan.fetch(razorpay_plan_id)
            except:
                # Create plan
                plan = self.client.plan.create({
                    "period": plan_data["period"],
                    "interval": plan_data["interval"],
                    "item": {
                        "name": f"AstraMark {plan_id.title()} Plan",
                        "amount": plan_data["amount"],
                        "currency": "INR"
                    },
                    "notes": {"plan_id": plan_id}
                })
                razorpay_plan_id = plan["id"]
            
            # Create subscription
            subscription = self.client.subscription.create({
                "plan_id": razorpay_plan_id,
                "customer_notify": 1,
                "quantity": 1,
                "total_count": 12,  # 12 months
                "notes": {
                    "user_id": user_id,
                    "plan_id": plan_id
                }
            })
            
            return {
                "subscription_id": subscription["id"],
                "short_url": subscription.get("short_url"),
                "status": subscription["status"]
            }
            
        except Exception as e:
            logger.error(f"Razorpay subscription creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def create_razorpay_order(
        self, 
        user_id: str, 
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Create Razorpay order for checkout (PRODUCTION-GRADE)
        Returns order object with id, amount, currency for frontend
        """
        if not self.is_enabled():
            logger.error("Razorpay service not enabled")
            raise HTTPException(
                status_code=503, 
                detail="Payment service unavailable. Please contact support."
            )
        
        # Plan amounts in paise (1 INR = 100 paise)
        amounts = {
            "starter": 149900,  # ₹1499
            "pro": 399900,      # ₹3999
            "growth": 799900    # ₹7999
        }
        
        if plan_id not in amounts:
            logger.error(f"Invalid plan_id: {plan_id}")
            raise HTTPException(status_code=400, detail="Invalid subscription plan")
        
        try:
            # Fetch user details
            user = await self.db.users.find_one({"id": user_id})
            if not user:
                logger.error(f"User not found: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Generate unique receipt ID
            import uuid
            receipt_id = f"rcpt_{plan_id}_{user_id[:8]}_{uuid.uuid4().hex[:8]}"
            
            # Create Razorpay order
            order_data = {
                "amount": amounts[plan_id],
                "currency": "INR",
                "receipt": receipt_id,
                "notes": {
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "email": user["email"],
                    "type": "subscription"
                }
            }
            
            logger.info(f"Creating Razorpay order for user {user_id}, plan {plan_id}")
            order = self.client.order.create(data=order_data)
            
            # Validate order response
            if not order or "id" not in order:
                logger.error(f"Invalid order response from Razorpay: {order}")
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to create payment order. Please try again."
                )
            
            logger.info(f"Razorpay order created successfully: {order['id']}")
            
            # Store order in database for verification later
            await self.db.payment_orders.insert_one({
                "order_id": order["id"],
                "user_id": user_id,
                "plan_id": plan_id,
                "amount": amounts[plan_id],
                "currency": "INR",
                "status": "created",
                "receipt": receipt_id,
                "created_at": datetime.now(timezone.utc)
            })
            
            # Return complete order object for frontend
            return {
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "key_id": settings.razorpay_key_id,  # Public key for frontend
                "plan_id": plan_id,
                "user_email": user["email"],
                "user_name": user.get("full_name", user["email"].split('@')[0])
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Payment system error: {str(e)}"
            )
    
    async def verify_payment_signature(
        self,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature (SECURITY CRITICAL)
        """
        if not self.is_enabled():
            return False
        
        try:
            # Generate expected signature
            message = f"{order_id}|{payment_id}"
            expected_signature = hmac.new(
                settings.razorpay_key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if is_valid:
                logger.info(f"Payment signature verified for order {order_id}")
            else:
                logger.error(f"Invalid payment signature for order {order_id}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def handle_payment_success(
        self,
        user_id: str,
        order_id: str,
        payment_id: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Handle successful payment after signature verification
        """
        try:
            # Verify signature first
            if not await self.verify_payment_signature(order_id, payment_id, signature):
                raise HTTPException(status_code=400, detail="Invalid payment signature")
            
            # Get order details from database
            order = await self.db.payment_orders.find_one({"order_id": order_id})
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Update user subscription
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "is_premium": True,
                        "subscription_plan": order["plan_id"],
                        "subscription_status": "active",
                        "razorpay_order_id": order_id,
                        "razorpay_payment_id": payment_id,
                        "subscription_updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Update order status
            await self.db.payment_orders.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": "paid",
                        "payment_id": payment_id,
                        "paid_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Log successful payment
            await self.db.payments.insert_one({
                "user_id": user_id,
                "order_id": order_id,
                "payment_id": payment_id,
                "amount": order["amount"],
                "currency": order["currency"],
                "plan_id": order["plan_id"],
                "status": "success",
                "gateway": "razorpay",
                "created_at": datetime.now(timezone.utc)
            })
            
            logger.info(f"Payment successful for user {user_id}, order {order_id}")
            
            return {
                "success": True,
                "message": "Payment successful",
                "plan": order["plan_id"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Payment success handling failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def create_payment_link(
        self, 
        user_id: str, 
        plan_id: str, 
        return_url: str
    ) -> Dict[str, Any]:
        """Create Razorpay payment link for one-time payment"""
        if not self.is_enabled():
            raise HTTPException(status_code=503, detail="Payment service not available")
        
        # Plan amounts in paise
        amounts = {
            "starter": 149900,  # ₹1499
            "pro": 399900,     # ₹3999
            "growth": 799900   # ₹7999
        }
        
        if plan_id not in amounts:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        try:
            user = await self.db.users.find_one({"id": user_id})
            
            payment_link = self.client.payment_link.create({
                "amount": amounts[plan_id],
                "currency": "INR",
                "description": f"AstraMark {plan_id.title()} Plan Subscription",
                "customer": {
                    "name": user.get("full_name", user["email"].split('@')[0]),
                    "email": user["email"]
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "callback_url": return_url,
                "callback_method": "get",
                "notes": {
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "type": "subscription"
                }
            })
            
            return {
                "payment_link_id": payment_link["id"],
                "payment_url": payment_link["short_url"],
                "status": payment_link["status"]
            }
            
        except Exception as e:
            logger.error(f"Razorpay payment link creation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Razorpay webhook signature"""
        if not settings.razorpay_webhook_secret:
            logger.warning("Razorpay webhook secret not configured - skipping signature verification")
            return True  # Allow webhooks in development without secret
        
        try:
            expected_signature = hmac.new(
                settings.razorpay_webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Razorpay webhook events"""
        if not self.verify_webhook_signature(payload, signature):
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        try:
            import json
            event = json.loads(payload.decode())
            event_type = event.get("event")
            
            if event_type == "payment.captured":
                await self._handle_payment_captured(event["payload"]["payment"]["entity"])
            elif event_type == "subscription.activated":
                await self._handle_subscription_activated(event["payload"]["subscription"]["entity"])
            elif event_type == "subscription.cancelled":
                await self._handle_subscription_cancelled(event["payload"]["subscription"]["entity"])
            elif event_type == "payment_link.paid":
                await self._handle_payment_link_paid(event["payload"]["payment_link"]["entity"])
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def _handle_payment_captured(self, payment):
        """Handle successful payment"""
        user_id = payment.get("notes", {}).get("user_id")
        plan_id = payment.get("notes", {}).get("plan_id")
        
        if user_id and plan_id:
            # Update user subscription
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "is_premium": True,
                        "subscription_plan": plan_id,
                        "subscription_status": "active",
                        "razorpay_payment_id": payment["id"],
                        "subscription_updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Log payment
            await self.db.payments.insert_one({
                "user_id": user_id,
                "razorpay_payment_id": payment["id"],
                "amount": payment["amount"],
                "currency": payment["currency"],
                "status": "captured",
                "gateway": "razorpay",
                "created_at": datetime.now(timezone.utc)
            })
            
            logger.info(f"User {user_id} payment captured for {plan_id}")
    
    async def _handle_subscription_activated(self, subscription):
        """Handle subscription activation"""
        user_id = subscription.get("notes", {}).get("user_id")
        plan_id = subscription.get("notes", {}).get("plan_id")
        
        if user_id and plan_id:
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "is_premium": True,
                        "subscription_plan": plan_id,
                        "subscription_status": "active",
                        "razorpay_subscription_id": subscription["id"],
                        "subscription_updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"User {user_id} subscription activated for {plan_id}")
    
    async def _handle_subscription_cancelled(self, subscription):
        """Handle subscription cancellation"""
        user_id = subscription.get("notes", {}).get("user_id")
        
        if user_id:
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "is_premium": False,
                        "subscription_plan": None,
                        "subscription_status": "cancelled",
                        "subscription_updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"User {user_id} subscription cancelled")
    
    async def _handle_payment_link_paid(self, payment_link):
        """Handle payment link completion"""
        user_id = payment_link.get("notes", {}).get("user_id")
        plan_id = payment_link.get("notes", {}).get("plan_id")
        
        if user_id and plan_id:
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "is_premium": True,
                        "subscription_plan": plan_id,
                        "subscription_status": "active",
                        "subscription_updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"User {user_id} payment link completed for {plan_id}")
    
    async def get_user_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current subscription details"""
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            return None
        
        subscription_data = {
            "is_premium": user.get("is_premium", False),
            "plan": user.get("subscription_plan"),
            "status": user.get("subscription_status"),
            "updated_at": user.get("subscription_updated_at"),
            "gateway": "razorpay"
        }
        
        if user.get("razorpay_subscription_id") and self.is_enabled():
            try:
                subscription = self.client.subscription.fetch(user["razorpay_subscription_id"])
                subscription_data.update({
                    "current_period_end": subscription.get("current_end"),
                    "next_billing": subscription.get("charge_at")
                })
            except Exception:
                pass
        
        return subscription_data
    
    def get_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans for Razorpay (Indian pricing)"""
        return [
            {
                "id": "starter",
                "name": "Starter",
                "price": 1499,  # ₹1499
                "currency": "INR",
                "interval": "month",
                "features": [
                    "Basic marketing strategies",
                    "Limited reports",
                    "5 analyses/month"
                ],
                "popular": False
            },
            {
                "id": "pro", 
                "name": "Pro",
                "price": 3999,  # ₹3999
                "currency": "INR",
                "interval": "month",
                "features": [
                    "Full marketing + data analysis",
                    "Business plans",
                    "Competitor research",
                    "30 analyses/month",
                    "Live market data",
                    "PDF exports"
                ],
                "popular": True
            },
            {
                "id": "growth",
                "name": "Growth", 
                "price": 7999,  # ₹7999
                "currency": "INR",
                "interval": "month",
                "features": [
                    "Advanced analytics",
                    "Revenue forecasting",
                    "Automation planning",
                    "Export reports (PDF/Excel)",
                    "100 analyses/month",
                    "Pitch deck generator",
                    "Content calendar",
                    "Email sequences"
                ],
                "popular": False
            }
        ]