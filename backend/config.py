"""
Configuration management for AstraMark
Handles environment variables and settings validation
"""
import os
import secrets
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    mongo_url: str = "mongodb://127.0.0.1:27017"
    db_name: str = "astramark_dev"
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # AI Services
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    serp_api_key: Optional[str] = None
    apify_api_token: Optional[str] = None
    
    # Authentication
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_refresh_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Payment Gateways
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    razorpay_webhook_secret: Optional[str] = None
    default_payment_gateway: str = "stripe"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    
    # App Settings
    environment: str = "development"
    debug: bool = True
    
    @field_validator('cors_origins')
    @classmethod
    def parse_cors_origins(cls, v):
        return [origin.strip() for origin in v.split(',')]
    
    @field_validator('jwt_secret_key', 'jwt_refresh_secret_key')
    @classmethod
    def validate_secret_keys(cls, v):
        if len(v) < 32:
            raise ValueError('Secret keys must be at least 32 characters long')
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Validation on startup
def validate_required_settings():
    """Validate that required settings are present"""
    errors = []
    
    if not settings.google_api_key and not settings.groq_api_key:
        errors.append("At least one AI API key (GOOGLE_API_KEY or GROQ_API_KEY) is required")
    
    if settings.is_production:
        if not settings.stripe_secret_key and not settings.razorpay_key_id:
            errors.append("At least one payment gateway (STRIPE_SECRET_KEY or RAZORPAY_KEY_ID) is required in production")
        
        if settings.jwt_secret_key == settings.jwt_refresh_secret_key:
            errors.append("JWT_SECRET_KEY and JWT_REFRESH_SECRET_KEY must be different")
        
        # Webhook secrets are recommended but not required
        if settings.stripe_secret_key and not settings.stripe_webhook_secret:
            errors.append("STRIPE_WEBHOOK_SECRET is recommended for production")
        
        if settings.razorpay_key_id and not settings.razorpay_webhook_secret:
            errors.append("RAZORPAY_WEBHOOK_SECRET is recommended for production")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Generate secure keys helper
def generate_secret_key() -> str:
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    print("Generated JWT Secret Key:", generate_secret_key())
    print("Generated JWT Refresh Secret Key:", generate_secret_key())