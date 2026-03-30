"""
Monitoring and Error Tracking Setup
"""
import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings

# Initialize Sentry only if DSN is provided
if settings.sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.pymongo import PyMongoIntegration
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                PyMongoIntegration(),
            ],
            traces_sample_rate=0.1 if settings.is_production else 1.0,
            environment=settings.environment,
            release="1.0.0"  # Update this with your app version
        )
        logging.info("Sentry initialized for error tracking")
    except ImportError:
        logging.warning("Sentry SDK not installed - error tracking disabled")
    except Exception as e:
        logging.error(f"Failed to initialize Sentry: {e}")
else:
    logging.info("Sentry DSN not configured - error tracking disabled")

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        process_time = time.time() - start_time
        
        # Log metrics
        logger = logging.getLogger("metrics")
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Duration: {process_time:.3f}s"
        )
        
        # Add headers
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class HealthCheck:
    """Health check utilities"""
    
    def __init__(self, db=None):
        self.db = db
    
    async def check_database(self) -> dict:
        """Check database connectivity"""
        try:
            if self.db:
                await self.db.admin.command('ping')
                return {"status": "healthy", "message": "Database connected"}
            else:
                return {"status": "unhealthy", "message": "Database not initialized"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Database error: {str(e)}"}
    
    async def check_ai_service(self) -> dict:
        """Check AI service availability"""
        try:
            if settings.google_api_key:
                return {"status": "healthy", "message": "AI service configured"}
            else:
                return {"status": "unhealthy", "message": "AI service not configured"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"AI service error: {str(e)}"}
    
    async def check_payment_service(self) -> dict:
        """Check payment service availability"""
        try:
            if settings.stripe_secret_key:
                return {"status": "healthy", "message": "Payment service configured"}
            else:
                return {"status": "warning", "message": "Payment service not configured"}
        except Exception as e:
            return {"status": "unhealthy", "message": f"Payment service error: {str(e)}"}
    
    async def get_system_health(self) -> dict:
        """Get overall system health"""
        checks = {
            "database": await self.check_database(),
            "ai_service": await self.check_ai_service(),
            "payment_service": await self.check_payment_service()
        }
        
        # Determine overall status
        statuses = [check["status"] for check in checks.values()]
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "environment": settings.environment,
            "checks": checks
        }

# Usage tracking
class UsageTracker:
    """Track API usage for billing and analytics"""
    
    def __init__(self, db):
        self.db = db
    
    async def track_analysis_request(self, user_id: str, plan: str = "free"):
        """Track analysis request for usage billing"""
        try:
            await self.db.usage_logs.insert_one({
                "user_id": user_id,
                "action": "analysis_request",
                "plan": plan,
                "timestamp": time.time(),
                "created_at": time.time()
            })
        except Exception as e:
            logging.error(f"Failed to track usage: {e}")
    
    async def get_user_usage(self, user_id: str, period_start: float) -> dict:
        """Get user usage statistics"""
        try:
            usage = await self.db.usage_logs.aggregate([
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": period_start}
                    }
                },
                {
                    "$group": {
                        "_id": "$action",
                        "count": {"$sum": 1}
                    }
                }
            ]).to_list(length=None)
            
            return {item["_id"]: item["count"] for item in usage}
        except Exception as e:
            logging.error(f"Failed to get usage: {e}")
            return {}

# Performance monitoring
def monitor_performance(func_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log performance
                logger = logging.getLogger("performance")
                logger.info(f"{func_name} completed in {duration:.3f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger = logging.getLogger("performance")
                logger.error(f"{func_name} failed after {duration:.3f}s: {str(e)}")
                raise
        return wrapper
    return decorator