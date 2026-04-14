"""
Enhanced AstraMark Server - Production Ready
"""
from fastapi import (
    FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends, Request, 
    status, Header, Body
)
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import ssl
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
import os
import logging
import ssl
import certifi
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import json
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import jwt
from jwt.exceptions import InvalidTokenError as JWTError
from passlib.context import CryptContext

import google.generativeai as genai
from google.generativeai import types

# Import our services
from config import settings, validate_required_settings
from auth_service import AuthService, AuthTokens, UserInDB, create_auth_tokens, create_access_token as create_proper_access_token
from unified_payment_service import UnifiedPaymentService
from monitoring import MetricsMiddleware, HealthCheck, UsageTracker, monitor_performance
from serp_service import serp_service
from free_market_service import free_market_service
from real_market_service import real_market_service
from apify_market_service import apify_market_service
from blockchain_service import blockchain_service
from pdf_service import pdf_generator
from content_service import ContentGenerationService
from scanner_service import BackgroundScanner
from groq_service import groq_service
from growth_engine import GrowthEngine
from campaign_launcher import CampaignLauncher
from autonomous_mode import AutonomousMarketingEngine
from learning_engine import LearningEngine
from predictive_revenue_system import PredictiveRevenueSystem
from conversion_optimization_ai import ConversionOptimizationAI
from lead_funnel_automator import LeadFunnelAutomator
from competitor_hijacking_engine import CompetitorHijackingEngine

# Import models
from models import (
    BusinessInput, BusinessProfile, MarketAnalysis, UserPersona, AIInsight,
    ChannelStrategy, RevenueProjection, MarketSignal, BlockchainProof,
    AILearningUpdate, ExecutionAction, CompetitorInsight, AnalysisResult
)

from logging_config import configure_logging
from middleware.error_handler import add_exception_handlers

# ==================== INITIALIZATION ====================
configure_logging()
logger = logging.getLogger(__name__)

# Validate configuration on startup
try:
    validate_required_settings()
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    if settings.is_production:
        raise

# Global Services
client = None
db = None
client_ai = None
content_service = None
auth_service = None
payment_service = None
health_check = None
usage_tracker = None
background_scanner = BackgroundScanner(apify_market_service, None)
growth_engine = None
campaign_launcher = None
autonomous_engine = None
learning_engine = None
predictive_revenue_system = None
conversion_optimization_ai = None
lead_funnel_automator = None
competitor_hijacking_engine = None

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address)

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

import hashlib

# Password hashing - Simple SHA256 (for development only)
def hash_password_simple(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password_simple(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password_simple(plain_password) == hashed_password

# JWT Configuration
SECRET_KEY = settings.jwt_secret_key
REFRESH_SECRET_KEY = settings.jwt_refresh_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# ==================== DEPENDENCY FUNCTIONS ====================
async def get_current_user_dep(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Dependency to get current authenticated user"""
    if not auth_service:
        raise HTTPException(status_code=503, detail="Authentication service not available")
    return await auth_service.get_current_user(token)

async def get_payment_service_dep():
    """Dependency to get payment service"""
    if not payment_service:
        raise HTTPException(status_code=503, detail="Payment service not available")
    return payment_service

async def get_content_service_dep():
    """Dependency to get content service"""
    if not content_service:
        raise HTTPException(status_code=503, detail="Content service not available")
    return content_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AstraMark Enhanced Server...")
    global client, db, client_ai, content_service, auth_service, payment_service, health_check, usage_tracker, growth_engine, campaign_launcher, autonomous_engine, conversion_optimization_ai, lead_funnel_automator, competitor_hijacking_engine
    
    # 1. Database Connection
    try:
        # MongoDB connection - Use tlsInsecure in connection string
        logger.info("Configuring MongoDB connection with tlsInsecure...")
        
        # Add tlsInsecure to connection string
        mongo_url = settings.mongo_url
        if "?" in mongo_url:
            mongo_url = f"{mongo_url}&tlsInsecure=true"
        else:
            mongo_url = f"{mongo_url}?tlsInsecure=true&retryWrites=true&w=majority"
        
        # Minimal connection params

        connection_params = {
            "serverSelectionTimeoutMS": 30000,
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000
        }
        
        client = AsyncIOMotorClient(mongo_url, **connection_params)
        await client.admin.command('ping')
        db = client[settings.db_name]
        logger.info(f"Connected to MongoDB successfully")
        
        # Initialize services
        auth_service = AuthService(db)
        payment_service = UnifiedPaymentService(db)
        health_check = HealthCheck(db)
        usage_tracker = UsageTracker(db)
        
        # Initialize Growth OS services
        growth_engine = GrowthEngine(db, client_ai)
        campaign_launcher = CampaignLauncher(db, growth_engine)
        learning_engine = LearningEngine(db, campaign_launcher)
        predictive_revenue_system = PredictiveRevenueSystem(db, growth_engine)
        autonomous_engine = AutonomousMarketingEngine(db, growth_engine, campaign_launcher)
        conversion_optimization_ai = ConversionOptimizationAI(db, client_ai)
        lead_funnel_automator = LeadFunnelAutomator(db, client_ai)
        competitor_hijacking_engine = CompetitorHijackingEngine(db, growth_engine)
        
        # Update Scanner with DB
        background_scanner.db = db
        background_scanner.start()
        
        # Start autonomous engine
        autonomous_engine.start()
        
        logger.info("Growth Operating System initialized successfully")
    except Exception as e:
        logger.critical(f"MongoDB connection failed: {e}")
        raise e

    # 2. AI Client Initialization
    if settings.google_api_key:
        try:
            genai.configure(api_key=settings.google_api_key)
            client_ai = genai  # Store the configured module
            content_service = ContentGenerationService(client_ai)
            logger.info("Gemini AI Client configured")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {e}")
            client_ai = None
            content_service = None
    else:
        logger.warning("GOOGLE_API_KEY not found")
        client_ai = None
        content_service = None
    
    # Initialize Groq as fallback
    if groq_service.is_available():
        logger.info("Groq service available as fallback")
    else:
        logger.warning("Groq service not available")

    yield
    
    # Shutdown
    logger.info("Shutting down...")
    background_scanner.stop()
    if autonomous_engine:
        autonomous_engine.stop()
    if client:
        client.close()
    logger.info("Server shutdown complete")

app = FastAPI(title="AstraMark AI Marketing API - Enhanced", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
add_exception_handlers(app)

# Custom validation error handler for better error messages
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to return user-friendly messages"""
    errors = []
    for error in exc.errors():
        field = error['loc'][-1] if error['loc'] else 'field'
        msg = error['msg']
        
        # Customize messages for better UX
        if 'min_length' in msg.lower():
            if field == 'primary_goal':
                msg = 'Primary goal must be at least 10 characters. Please provide more details about your goal.'
            else:
                msg = f'{field} is too short'
        elif 'required' in msg.lower():
            msg = f'{field} is required'
        
        errors.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": " | ".join(errors)}
    )

api_router = APIRouter(prefix="/api")

# ==================== AUTH MODELS & HELPERS ====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    # bcrypt has a 72-byte limit; enforce a safe length here
    password: str = Field(..., min_length=8, max_length=64)  # Reduced from 72 to be safe

class UserInDB(UserBase):
    id: str
    hashed_password: str
    is_active: bool = True
    is_premium: bool = False
    subscription_plan: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return verify_password_simple(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return hash_password_simple(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    # Add required fields for proper token validation
    if "type" not in to_encode:
        to_encode["type"] = "access"  # Default to access token
    
    # Add issued at timestamp and unique token ID
    to_encode["iat"] = datetime.now(timezone.utc)
    to_encode["jti"] = str(uuid.uuid4())
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Fetch a user document by email and map to UserInDB."""
    if db is None:
        return None
    user_doc = await db.users.find_one({"email": email})
    if not user_doc:
        return None
    
    # Handle created_at field - convert string to datetime if needed
    created_at = user_doc.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    elif created_at is None:
        created_at = datetime.now(timezone.utc)
    
    return UserInDB(
        id=str(user_doc.get("id") or user_doc.get("_id")),
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
        hashed_password=user_doc["hashed_password"],
        created_at=created_at
    )

async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Validating token: {token[:20]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        logger.info(f"Token decoded successfully for email: {email}")
        if email is None:
            logger.error("No email in token payload")
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    user = await get_user_by_email(token_data.email)  # type: ignore[arg-type]
    if user is None:
        logger.error(f"User not found for email: {token_data.email}")
        raise credentials_exception
    logger.info(f"User authenticated successfully: {user.email}")
    return user

# ==================== HELPER FUNCTIONS ====================
async def generate_market_analysis_with_live_data(business: BusinessInput) -> Dict[str, Any]:
    """Generate comprehensive market analysis using AI + live market data"""
    
    if not settings.google_api_key and not settings.groq_api_key:
        raise HTTPException(status_code=500, detail="Server Configuration Error: No AI API keys configured.")

    # Fetch live competitor data using APIFY web scraping (REAL DATA!)
    competitor_data = await apify_market_service.search_competitors(
        business.business_type,
        business.target_market
    )
    
    # Fetch market trends using APIFY actors (REAL MARKET DATA!)
    market_trends = await apify_market_service.get_market_trends(business.business_type)
    
    system_profile = """You are AstraMark, a production-grade AI Marketing & Business Intelligence Platform.

    Your role is to act as:
    - A senior digital marketing strategist
    - A data analyst
    - A market research expert
    - A business consultant
    - A financial planner
    - A startup advisor

    You DO NOT behave like a chatbot.
    You behave like a professional SaaS intelligence engine.

    CORE OBJECTIVES:
    1. Generate actionable, data-backed marketing strategies
    2. Perform market research and competitor analysis
    3. Create revenue projections and business models
    4. Design go-to-market strategies
    5. Build reports, dashboards, and growth plans
    6. Provide automation-ready outputs for execution

    OUTPUT RULES:
    - Always structured JSON
    - Always actionable (no generic advice)
    - Always business-ready
    - Assume the user wants results they can implement or present

    LIMITATIONS:
    - Never hallucinate exact numbers without stating "Estimated" or "Projected".
    - Prefer clarity over hype.
    """
    
    user_prompt = f"""
    Analyze this business and provide a comprehensive marketing strategy:
    
    Business Type: {business.business_type}
    Target Market: {business.target_market}
    Monthly Budget: {business.monthly_budget}
    Primary Goal: {business.primary_goal}
    Additional Info: {business.additional_info or 'None'}
    
    LIVE MARKET DATA:
    - Competitor Count: {len(competitor_data.get('competitors', []))}
    - Top Competitors: {[c.get('name', '') for c in competitor_data.get('competitors', [])[:3]]}
    - Market Trends: {market_trends}
    
    Provide a detailed analysis in the following JSON structure (AND ONLY JSON):
    {{
        "overview": "Brief business snapshot and goal alignment",
        "market_analysis": {{
            "market_size": "Estimated market size as a single string",
            "growth_rate": "Annual growth rate as a single string (e.g., '15% CAGR')",
            "entry_barriers": "Key barriers to entry as a single descriptive string",
            "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
            "risks": ["risk1", "risk2", "risk3"],
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"]
        }},
        "user_personas": [
            {{
                "name": "Persona Name",
                "demographics": "Age, location, income details",
                "psychographics": "Interests, values, lifestyle",
                "pain_points": ["pain1", "pain2", "pain3"],
                "buying_triggers": ["trigger1", "trigger2"],
                "objections": ["objection1", "objection2"]
            }}
        ],
        "ai_insights": [
            {{
                "insight_type": "Pattern Recognition / Market Gap / Growth Opportunity",
                "description": "Detailed insight",
                "confidence": 85
            }}
        ],
        "strategies": [
            {{
                "channel": "SEO",
                "strategy": "Detailed SEO strategy",
                "content_ideas": ["idea1", "idea2", "idea3"],
                "posting_schedule": "Frequency and timing",
                "kpi_benchmarks": {{
                    "organic_traffic": "Target number",
                    "conversion_rate": "Target percentage"
                }}
            }},
            {{
                "channel": "Content Marketing",
                "strategy": "Content strategy details",
                "content_ideas": ["idea1", "idea2", "idea3"],
                "posting_schedule": "Content calendar",
                "kpi_benchmarks": {{
                    "engagement_rate": "Target",
                    "lead_generation": "Target"
                }}
            }},
            {{
                "channel": "Paid Ads",
                "strategy": "Paid advertising strategy",
                "content_ideas": ["ad_concept1", "ad_concept2"],
                "posting_schedule": "Campaign frequency",
                "kpi_benchmarks": {{
                    "cpc": "Target cost",
                    "roas": "Target return"
                }}
            }},
            {{
                "channel": "Social Media",
                "strategy": "Social media strategy",
                "content_ideas": ["post_idea1", "post_idea2", "post_idea3"],
                "posting_schedule": "Daily/Weekly schedule",
                "kpi_benchmarks": {{
                    "followers_growth": "Monthly target",
                    "engagement_rate": "Target percentage"
                }}
            }}
        ],
        "revenue_projection": {{
            "min_monthly": "Currency Amount",
            "max_monthly": "Currency Amount",
            "growth_timeline": "Timeline to reach targets"
        }},
        "virality_score": 75,
        "retention_score": 80,
        "ai_verdict": "High / Medium / Low Growth Potential",
        "confidence_score": 85,
        "biggest_opportunity": "The single biggest opportunity",
        "biggest_risk": "The single biggest risk",
        "next_action": "The immediate next step to take"
    }}
    
    Return strict JSON ONLY. No markdown formatting like ```json ... ```.
    """
    
    # Try Groq first (primary), then fallback to Gemini
    analysis_data = None
    ai_service_used = None
    
    # Try Groq first as primary service
    if groq_service.is_available():
        try:
            logger.info("Attempting analysis with Groq (Primary)")
            analysis_data = await groq_service.generate_analysis(system_profile, user_prompt)
            ai_service_used = "groq"
            logger.info("Analysis generated successfully with Groq")
        except Exception as e:
            logger.error(f"Groq analysis failed: {e}")
            analysis_data = None
    
    # Fallback to Gemini if Groq failed
    if not analysis_data and client_ai and settings.google_api_key:
        try:
            logger.info("Falling back to Gemini for analysis")
            
            @retry(
                stop=stop_after_attempt(2),
                wait=wait_exponential(multiplier=1, min=4, max=10),
                reraise=True
            )
            async def call_gemini():
                PRIMARY_MODEL = "gemini-2.0-flash-exp"
                FALLBACK_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro"]
                models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
                
                for model_name in models_to_try:
                    try:
                        model = client_ai.GenerativeModel(
                            model_name=model_name,
                            generation_config={
                                "temperature": 0.7,
                                "response_mime_type": "application/json"
                            },
                            system_instruction=system_profile
                        )
                        
                        response = await model.generate_content_async(user_prompt)
                        
                        response_text = response.text.strip()
                        
                        # Cleanup potential markdown
                        if response_text.startswith("```json"):
                            response_text = response_text[7:]
                        if response_text.startswith("```"):
                            response_text = response_text[3:]
                        if response_text.endswith("```"):
                            response_text = response_text[:-3]
                        response_text = response_text.strip()
                        
                        return json.loads(response_text)
                    except Exception as e:
                        logger.warning(f"Gemini model {model_name} failed: {e}")
                        continue
                
                raise Exception("All Gemini models failed")
            
            analysis_data = await call_gemini()
            ai_service_used = "gemini"
            logger.info("Analysis generated successfully with Gemini")
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            analysis_data = None
    
    # If both AI services fail, return mock data
    if not analysis_data:
        logger.error("All AI services failed. Using fallback mock data.")
        analysis_data = {
            "overview": f"Analysis generated in offline mode due to AI service unavailability. Business: {business.business_type}",
            "market_analysis": {
                "market_size": "Estimated $10B+ (Offline Estimate)",
                "growth_rate": "15% CAGR",
                "entry_barriers": "Moderate competition and regulatory requirements",
                "opportunities": ["Digital Transformation", "AI Integration", "Niche Targeting"],
                "risks": ["Competition", "Market Saturation", "Tech Changes"],
                "strengths": ["Agility", "Cost Structure"],
                "weaknesses": ["Brand Awareness", "Resources"]
            },
            "user_personas": [
                {
                    "name": "Tech Savvy Founder",
                    "demographics": "25-40, Urban",
                    "psychographics": "Early adopter, ambitious",
                    "pain_points": ["Efficiency", "Scaling"],
                    "buying_triggers": ["Automation", "ROI"],
                    "objections": ["Cost", "Complexity"]
                }
            ],
            "ai_insights": [
                {
                    "insight_type": "Market Gap",
                    "description": "High demand for specialized solutions in this vertical.",
                    "confidence": 70
                }
            ],
            "strategies": [
                {
                    "channel": "Content Marketing",
                    "strategy": "Focus on educational content and thought leadership.",
                    "content_ideas": ["How-to Guides", "Case Studies", "Industry Trends"],
                    "posting_schedule": "2x Weekly",
                    "kpi_benchmarks": {"traffic": "1000/mo", "leads": "50/mo"}
                }
            ],
            "revenue_projection": {
                "min_monthly": "$2,000",
                "max_monthly": "$15,000",
                "growth_timeline": "6-12 Months"
            },
            "virality_score": 65,
            "retention_score": 75,
            "ai_verdict": "Medium Growth Potential",
            "confidence_score": 60,
            "biggest_opportunity": "Niche dominance",
            "biggest_risk": "Competitor speed",
            "next_action": "Launch MVP marketing campaign"
        }
        ai_service_used = "fallback"
    
    # Validate and fix data format issues
    if analysis_data and 'market_analysis' in analysis_data:
        market_analysis = analysis_data['market_analysis']
        
        # Fix entry_barriers if it's a list (convert to string)
        if isinstance(market_analysis.get('entry_barriers'), list):
            market_analysis['entry_barriers'] = ', '.join(market_analysis['entry_barriers'])
        
        # Ensure all required string fields are strings
        string_fields = ['market_size', 'growth_rate', 'entry_barriers']
        for field in string_fields:
            if isinstance(market_analysis.get(field), list):
                market_analysis[field] = ', '.join(str(x) for x in market_analysis[field])
            elif not isinstance(market_analysis.get(field), str):
                market_analysis[field] = str(market_analysis.get(field, 'Not specified'))
        
        # Ensure array fields are arrays
        array_fields = ['opportunities', 'risks', 'strengths', 'weaknesses']
        for field in array_fields:
            if not isinstance(market_analysis.get(field), list):
                market_analysis[field] = [str(market_analysis.get(field, ''))] if market_analysis.get(field) else []
    
    # Fix user personas
    if analysis_data and 'user_personas' in analysis_data:
        for persona in analysis_data['user_personas']:
            # Ensure array fields are arrays
            for field in ['pain_points', 'buying_triggers', 'objections']:
                if not isinstance(persona.get(field), list):
                    persona[field] = [str(persona.get(field, ''))] if persona.get(field) else []
    
    # Fix strategies
    if analysis_data and 'strategies' in analysis_data:
        for strategy in analysis_data['strategies']:
            # Ensure content_ideas is an array of strings
            if not isinstance(strategy.get('content_ideas'), list):
                strategy['content_ideas'] = [str(strategy.get('content_ideas', ''))] if strategy.get('content_ideas') else []
            else:
                # Ensure all items in content_ideas are strings
                strategy['content_ideas'] = [
                    str(item) if not isinstance(item, str) else item 
                    for item in strategy.get('content_ideas', [])
                ]
            
            # Ensure kpi_benchmarks is a dict with string/number values
            if not isinstance(strategy.get('kpi_benchmarks'), dict):
                strategy['kpi_benchmarks'] = {}
            else:
                # Ensure all values in kpi_benchmarks are strings or numbers
                sanitized_kpis = {}
                for key, value in strategy.get('kpi_benchmarks', {}).items():
                    if isinstance(value, (str, int, float)):
                        sanitized_kpis[key] = value
                    else:
                        sanitized_kpis[key] = str(value)
                strategy['kpi_benchmarks'] = sanitized_kpis
    
    # Add metadata about which service was used
    analysis_data['ai_service_used'] = ai_service_used
    analysis_data['competitor_data'] = competitor_data
    analysis_data['market_trends'] = market_trends
    
    return analysis_data

def generate_agent_features(business_type: str, goal: str) -> Dict[str, Any]:
    """Generate mock agent intelligence features"""
    return {
        "market_signals": [
            {
                "type": "Competitive",
                "severity": "critical",
                "message": f"Major competitor in {business_type} increased ad spend by 40%",
                "detected_at": "2 mins ago"
            },
            {
                "type": "Consumer",
                "severity": "info",
                "message": "Shift in search patterns detected for target audience",
                "detected_at": "15 mins ago"
            }
        ],
        "ai_learning_updates": [
            {
                "update_type": "Pattern Recognition",
                "learning_description": f"Model refined for {goal} optimization",
                "improvement_metric": "+14.2% Efficiency",
                "timestamp": "Just now"
            }
        ],
        "execution_actions": [
            {
                "action_id": "auto-content",
                "action_type": "content",
                "action_name": "Generate Social Content",
                "description": "AI-written posts based on this strategy",
                "is_premium": False,
                "status": "active"
            },
            {
                "action_id": "competitor-track",
                "action_type": "monitoring",
                "action_name": "Live Competitor Tracking",
                "description": "Monitor landing page changes in real-time",
                "is_premium": True,
                "status": "locked"
            },
            {
                "action_id": "ad-optimize",
                "action_type": "execution",
                "action_name": "Auto-Optimize Ad Spend",
                "description": "Dynamic budget allocation based on performance",
                "is_premium": True,
                "status": "locked"
            }
        ],
        "last_market_scan": "Recently",
        "monitoring_status": "active"
    }

# ==================== API ROUTES ====================
@api_router.get("/")
async def root():
    return {"message": "AstraMark AI Marketing Platform API - Enhanced Edition"}


# ---------- Auth Endpoints ----------

@api_router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate):
    """
    Register a new user.

    Expected JSON body (from frontend):
    {
      "email": "...",
      "password": "...",
      "full_name": "..."
    }
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    existing = await db.users.find_one({"email": user_in.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "id": str(uuid.uuid4()),
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": get_password_hash(user_in.password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user_doc)

    return {
        "id": user_doc["id"],
        "email": user_doc["email"],
        "full_name": user_doc["full_name"],
    }


@api_router.post("/auth/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 password flow endpoint with refresh token support.
    
    Frontend sends:
      username=<email>&password=<password>
    as x-www-form-urlencoded.
    
    Returns both access_token and refresh_token for silent token refresh.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token (short-lived: 15 minutes)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_proper_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires,
    )
    
    # Create refresh token (long-lived: 7 days)
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_proper_access_token(
        data={"sub": user.email, "user_id": user.id, "type": "refresh"},
        expires_delta=refresh_token_expires,
    )
    
    # Update last login
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }


@api_router.post("/auth/refresh")
async def refresh_access_token(refresh_token: str = Body(..., embed=True)):
    """
    Refresh access token using refresh token (PRODUCTION-GRADE)
    
    This endpoint enables silent token refresh so users never get logged out
    during critical flows like payments.
    """
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = await get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_proper_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires,
        )
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except JWTError as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@api_router.get("/auth/me")
async def read_current_user(current_user: UserInDB = Depends(get_current_user)):
    """Return the currently authenticated user's public profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
    }

@api_router.post("/analyze", response_model=AnalysisResult)
@limiter.limit("5/minute")
async def analyze_business(request: Request, business_input: BusinessInput, premium: bool = False, background_tasks: BackgroundTasks = None):
    """Main AI analysis endpoint with live market data"""
    try:
        # Save business profile
        business_profile = BusinessProfile(**business_input.model_dump())
        business_doc = business_profile.model_dump()
        business_doc['created_at'] = business_doc['created_at'].isoformat()
        await db.businesses.insert_one(business_doc)
        
        # Generate AI analysis with live data
        analysis_data = await generate_market_analysis_with_live_data(business_input)
        
        # Generate agent features
        agent_features = generate_agent_features(business_input.business_type, business_input.primary_goal)
        
        # Create analysis result
        analysis_result = AnalysisResult(
            business_id=business_profile.id,
            overview=analysis_data['overview'],
            market_analysis=MarketAnalysis(**analysis_data['market_analysis']),
            user_personas=[UserPersona(**p) for p in analysis_data['user_personas']],
            ai_insights=[AIInsight(**i) for i in analysis_data['ai_insights']],
            strategies=[ChannelStrategy(**s) for s in analysis_data['strategies']],
            revenue_projection=RevenueProjection(**analysis_data['revenue_projection']),
            virality_score=analysis_data['virality_score'],
            retention_score=analysis_data['retention_score'],
            ai_verdict=analysis_data['ai_verdict'],
            confidence_score=analysis_data['confidence_score'],
            biggest_opportunity=analysis_data['biggest_opportunity'],
            biggest_risk=analysis_data['biggest_risk'],
            next_action=analysis_data['next_action'],
            is_premium=premium,
            market_signals=[MarketSignal(**s) for s in agent_features['market_signals']],
            ai_learning_updates=[AILearningUpdate(**u) for u in agent_features['ai_learning_updates']],
            execution_actions=[ExecutionAction(**a) for a in agent_features['execution_actions']],
            competitor_insights=[CompetitorInsight(**c) for c in analysis_data.get('competitor_data', {}).get('competitors', [])],
            last_market_scan=agent_features['last_market_scan'],
            monitoring_status=agent_features['monitoring_status']
        )
        
        # Generate blockchain proof
        blockchain_proof = await blockchain_service.timestamp_analysis(
            analysis_result.model_dump(),
            db.blockchain_proofs if hasattr(db, 'blockchain_proofs') else None
        )
        analysis_result.blockchain_proof = BlockchainProof(**blockchain_proof)
        
        # Save analysis
        analysis_doc = analysis_result.model_dump()
        analysis_doc['created_at'] = analysis_doc['created_at'].isoformat()
        await db.analyses.insert_one(analysis_doc)
        
        # Schedule background market monitoring if enabled
        if background_tasks and background_scanner.enabled:
            background_tasks.add_task(
                background_scanner.scan_markets
            )
        
        return analysis_result
        
    except Exception as e:
        logging.error(f"Analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analyses", response_model=List[AnalysisResult])
async def get_analyses(limit: int = 10):
    """Get recent analyses"""
    try:
        analyses = await db.analyses.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        for analysis in analyses:
            if isinstance(analysis['created_at'], str):
                analysis['created_at'] = datetime.fromisoformat(analysis['created_at'])
        
        return analyses
    except Exception as e:
        logging.error(f"Get analyses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analyses/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    """Get specific analysis"""
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        if isinstance(analysis['created_at'], str):
            analysis['created_at'] = datetime.fromisoformat(analysis['created_at'])
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/businesses", response_model=List[BusinessProfile])
async def get_businesses(limit: int = 10):
    """Get recent business profiles"""
    try:
        businesses = await db.businesses.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        for business in businesses:
            if isinstance(business['created_at'], str):
                business['created_at'] = datetime.fromisoformat(business['created_at'])
        
        return businesses
    except Exception as e:
        logging.error(f"Get businesses error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_services": {
            "groq_enabled": groq_service.is_available(),
            "groq_primary": True,
            "gemini_enabled": bool(settings.google_api_key),
            "gemini_fallback": bool(settings.google_api_key)
        },
        "market_intelligence": {
            "apify_enabled": apify_market_service.enabled,
            "web_scraping_actors": ["google-search-results-scraper", "website-content-crawler"],
            "real_apis_enabled": real_market_service.enabled,
            "live_data_sources": ["apify_google_search", "apify_website_crawler", "duckduckgo", "github", "reddit"],
            "data_source": "apify_web_scraping"
        },
        "db_connected": client is not None,
        "blockchain_enabled": blockchain_service.enabled,
        "scanner_enabled": background_scanner.enabled
    }

# ==================== CONTENT GENERATION ENDPOINTS ====================
@api_router.post("/generate/pitch-deck")
async def generate_pitch_deck(analysis_id: str, content_svc = Depends(get_content_service_dep)):
    """Generate a pitch deck from analysis"""
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        pitch_deck = await content_svc.generate_pitch_deck(analysis)
        return pitch_deck
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pitch deck generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate/content-calendar")
async def generate_content_calendar(analysis_id: str, weeks: int = 4, content_svc = Depends(get_content_service_dep)):
    """Generate a content calendar from analysis"""
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        calendar = await content_svc.generate_content_calendar(analysis, weeks)
        return calendar
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content calendar generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate/email-sequence")
async def generate_email_sequence(analysis_id: str, sequence_type: str = "onboarding", content_svc = Depends(get_content_service_dep)):
    """Generate an email sequence from analysis"""
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        sequence = await content_svc.generate_email_sequence(analysis, sequence_type)
        return sequence
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email sequence generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/export/pdf/{analysis_id}")
async def export_pdf_report(analysis_id: str):
    """Export analysis as PDF report"""
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Convert datetime if needed
        if isinstance(analysis.get('created_at'), str):
            analysis['created_at'] = datetime.fromisoformat(analysis['created_at'])
        
        pdf_buffer = await pdf_generator.generate_analysis_report(analysis)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=astramark_report_{analysis_id[:8]}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== MARKET INTELLIGENCE ENDPOINTS ====================
@api_router.get("/market/signals")
async def get_market_signals(business_type: Optional[str] = None, limit: int = 10):
    """Get latest market signals"""
    try:
        signals = await background_scanner.get_latest_signals(business_type, limit)
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        logger.error(f"Get market signals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/market/competitors/{business_id}")
async def get_competitor_updates(business_id: str):
    """Get competitor updates for a business"""
    try:
        updates = await background_scanner.get_competitor_updates(business_id)
        return {"updates": updates, "count": len(updates)}
    except Exception as e:
        logger.error(f"Get competitor updates error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return [
        {
            "id": "starter",
            "name": "Starter",
            "price": 19,
            "period": "month",
            "features": [
                "Basic marketing strategies",
                "Limited reports",
                "5 analyses/month"
            ],
            "color": "green"
        },
        {
            "id": "pro",
            "name": "Pro",
            "price": 49,
            "period": "month",
            "features": [
                "Full marketing + data analysis",
                "Business plans",
                "Competitor research",
                "30 analyses/month",
                "Live market data",
                "PDF exports"
            ],
            "color": "blue",
            "popular": True
        },
        {
            "id": "growth",
            "name": "Growth",
            "price": 99,
            "period": "month",
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
            "color": "purple"
        },
        {
            "id": "enterprise",
            "name": "Enterprise",
            "price": "Custom",
            "period": "",
            "features": [
                "API access",
                "Team accounts",
                "Custom AI tuning",
                "White-label reports",
                "Blockchain verification",
                "24/7 support"
            ],
            "color": "slate"
        }
    ]

# ==================== PAYMENT ENDPOINTS ====================
@api_router.get("/payments/gateways")
async def get_payment_gateways(payment_svc = Depends(get_payment_service_dep)):
    """Get available payment gateways"""
    return {
        "gateways": payment_svc.get_available_gateways(),
        "default": settings.default_payment_gateway
    }

@api_router.get("/payments/plans")
async def get_payment_plans(gateway: Optional[str] = None, payment_svc = Depends(get_payment_service_dep)):
    """Get subscription plans for specific gateway or all gateways"""
    if gateway:
        return {
            "gateway": gateway,
            "plans": payment_svc.get_plans_for_gateway(gateway)
        }
    else:
        return payment_svc.get_all_plans()

@api_router.post("/payments/checkout")
async def create_checkout_session(
    plan_id: str = Body(...),
    gateway: str = Body(...),
    success_url: str = Body(...),
    cancel_url: str = Body(...),
    current_user: UserInDB = Depends(get_current_user_dep)
):
    """Create checkout session for subscription"""
    try:
        logger.info(f"Checkout request: user={current_user.id}, plan={plan_id}, gateway={gateway}")
        
        session = await payment_service.create_checkout_session(
            current_user.id, plan_id, gateway, success_url, cancel_url
        )
        
        logger.info(f"Checkout session created successfully for user {current_user.id}")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout session creation failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")

@api_router.post("/payments/razorpay/create-order")
async def create_razorpay_order(
    plan_id: str = Body(...),
    current_user: UserInDB = Depends(get_current_user_dep)
):
    """
    Create Razorpay order for checkout (PRODUCTION-GRADE)
    This endpoint MUST succeed before opening Razorpay checkout
    """
    try:
        logger.info(f"Creating Razorpay order: user={current_user.id}, plan={plan_id}")
        
        # Validate payment service
        if not payment_service or not payment_service.razorpay_service:
            logger.error("Razorpay service not available")
            raise HTTPException(
                status_code=503,
                detail="Payment service unavailable. Please contact support."
            )
        
        # Create order
        order = await payment_service.razorpay_service.create_razorpay_order(
            current_user.id,
            plan_id
        )
        
        # Validate order response
        if not order or "order_id" not in order:
            logger.error(f"Invalid order response: {order}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create payment order"
            )
        
        logger.info(f"Razorpay order created: {order['order_id']}")
        
        return {
            "success": True,
            "order": order
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment order: {str(e)}"
        )

@api_router.post("/payments/razorpay/verify")
async def verify_razorpay_payment(
    order_id: str = Body(...),
    payment_id: str = Body(...),
    signature: str = Body(...),
    current_user: UserInDB = Depends(get_current_user_dep)
):
    """
    Verify Razorpay payment signature and activate subscription (SECURITY CRITICAL)
    """
    try:
        logger.info(f"Verifying payment: user={current_user.id}, order={order_id}, payment={payment_id}")
        
        if not payment_service or not payment_service.razorpay_service:
            raise HTTPException(status_code=503, detail="Payment service unavailable")
        
        # Handle payment success with signature verification
        result = await payment_service.razorpay_service.handle_payment_success(
            current_user.id,
            order_id,
            payment_id,
            signature
        )
        
        logger.info(f"Payment verified successfully for user {current_user.id}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment verification failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Payment verification failed: {str(e)}"
        )

@api_router.post("/payments/subscription")
async def create_subscription(
    plan_id: str,
    gateway: str,
    return_url: str,
    current_user: UserInDB = Depends(get_current_user_dep)
):
    """Create recurring subscription"""
    try:
        subscription = await payment_service.create_subscription(
            current_user.id, plan_id, gateway, return_url
        )
        return subscription
    except Exception as e:
        logger.error(f"Subscription creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/payments/portal")
async def create_customer_portal(
    return_url: str,
    current_user: UserInDB = Depends(get_current_user_dep)
):
    """Create customer portal session"""
    try:
        portal = await payment_service.create_customer_portal_session(
            current_user.id, return_url
        )
        return portal
    except Exception as e:
        logger.error(f"Portal session creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/payments/subscription")
async def get_user_subscription(
    current_user: UserInDB = Depends(get_current_user_dep)
):
    """Get current user's subscription details"""
    subscription = await payment_service.get_user_subscription(current_user.id)
    return subscription or {"is_premium": False, "plan": None}

@api_router.post("/payments/webhook/{gateway}")
async def handle_payment_webhook(
    gateway: str,
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
    razorpay_signature: Optional[str] = Header(None, alias="x-razorpay-signature"),
    payment_svc = Depends(get_payment_service_dep)
):
    """Handle payment webhooks from different gateways"""
    try:
        payload = await request.body()
        
        if gateway == "stripe":
            signature = stripe_signature
        elif gateway == "razorpay":
            signature = razorpay_signature
        else:
            raise HTTPException(status_code=400, detail="Invalid gateway")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        result = await payment_svc.handle_webhook(gateway, payload, signature)
        return result
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/payments/config/{gateway}")
async def get_payment_config(gateway: str, payment_svc = Depends(get_payment_service_dep)):
    """Get public payment gateway configuration"""
    return payment_svc.get_gateway_config(gateway)

# ==================== GROWTH OS ENDPOINTS ====================
@api_router.get("/growth/daily-actions/{business_id}")
async def get_daily_actions(business_id: str):
    """Get AI-generated daily actionable recommendations"""
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        actions = await growth_engine.generate_daily_actions(business_id)
        return {"actions": actions, "count": len(actions)}
    except Exception as e:
        logger.error(f"Daily actions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/predict-revenue")
async def predict_revenue(request: Request):
    """Predict revenue based on budget and channel mix"""
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        budget = data.get('budget')
        channels = data.get('channels', [])
        
        prediction = await growth_engine.predict_revenue(business_id, budget, channels)
        return prediction
    except Exception as e:
        logger.error(f"Revenue prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/launch-campaign")
async def launch_campaign(request: Request):
    """One-click campaign launch"""
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        goal = data.get('goal')
        channels = data.get('channels', [])
        budget = data.get('budget', 0)
        
        result = await campaign_launcher.launch_campaign(business_id, goal, channels, budget)
        return result
    except Exception as e:
        logger.error(f"Campaign launch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/growth/campaigns/{campaign_id}")
async def get_campaign_status(campaign_id: str):
    """Get campaign status and performance"""
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        campaign = await campaign_launcher.get_campaign_status(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get campaign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pause an active campaign"""
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        success = await campaign_launcher.pause_campaign(campaign_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Pause campaign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/campaigns/{campaign_id}/resume")
async def resume_campaign(campaign_id: str):
    """Resume a paused campaign"""
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        success = await campaign_launcher.resume_campaign(campaign_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Resume campaign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/campaigns/{campaign_id}/performance")
async def update_campaign_performance(campaign_id: str, request: Request):
    """Update campaign performance metrics"""
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        data = await request.json()
        performance_data = data.get('performance', {})
        
        success = await campaign_launcher.update_campaign_performance(campaign_id, performance_data)
        return {"success": success}
    except Exception as e:
        logger.error(f"Update campaign performance error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/analyze-competitors")
async def analyze_competitors(request: Request):
    """Analyze competitors and get hijack strategies"""
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        competitors = data.get('competitors', [])
        
        analysis = await growth_engine.analyze_competitors(business_id, competitors)
        return analysis
    except Exception as e:
        logger.error(f"Competitor analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/viral-content")
async def generate_viral_content(request: Request):
    """Generate viral-optimized content"""
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        topic = data.get('topic')
        platform = data.get('platform', 'Instagram')
        
        content = await growth_engine.generate_viral_content(business_id, topic, platform)
        return {"content": content, "count": len(content)}
    except Exception as e:
        logger.error(f"Viral content generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/optimize-conversion")
async def optimize_conversion(request: Request):
    """Analyze and optimize conversion rates"""
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        page_data = await request.json()
        
        optimization = await growth_engine.optimize_conversion(page_data)
        return optimization
    except Exception as e:
        logger.error(f"Conversion optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/create-funnel")
async def create_lead_funnel(request: Request):
    """Create automated lead funnel"""
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        goal = data.get('goal')
        
        funnel = await growth_engine.create_lead_funnel(business_id, goal)
        return funnel
    except Exception as e:
        logger.error(f"Funnel creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/autonomous/enable")
async def enable_autonomous_mode(request: Request):
    """Enable autonomous marketing mode"""
    try:
        if not autonomous_engine:
            raise HTTPException(status_code=503, detail="Autonomous engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        budget_limit = data.get('budget_limit', 10000)
        channels = data.get('channels', ['SEO', 'Social', 'Email'])
        
        config = {
            'budget_limit': budget_limit,
            'channels': channels
        }
        success = await autonomous_engine.enable_autonomous_mode(business_id, config)
        return {"success": success, "message": "Autonomous mode enabled"}
    except Exception as e:
        logger.error(f"Enable autonomous mode error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/autonomous/disable")
async def disable_autonomous_mode(request: Request):
    """Disable autonomous marketing mode"""
    try:
        if not autonomous_engine:
            raise HTTPException(status_code=503, detail="Autonomous engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        
        success = await autonomous_engine.disable_autonomous_mode(business_id)
        return {"success": success, "message": "Autonomous mode disabled"}
    except Exception as e:
        logger.error(f"Disable autonomous mode error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/growth/autonomous/status/{business_id}")
async def get_autonomous_status(business_id: str):
    """Get autonomous mode status for a business"""
    try:
        config = await db.autonomous_configs.find_one({'business_id': business_id})
        if not config:
            return {"enabled": False}
        
        if '_id' in config:
            config['_id'] = str(config['_id'])
        
        return config
    except Exception as e:
        logger.error(f"Get autonomous status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/growth/forecast/{business_id}")
async def forecast_revenue_growth(business_id: str, months: int = 6):
    """
    Forecast monthly revenue growth for a business
    
    **Validates: Requirements 5.5, 5.6, 5.7**
    """
    try:
        if not predictive_revenue_system:
            raise HTTPException(status_code=503, detail="Predictive revenue system not available")
        
        if months < 1 or months > 24:
            raise HTTPException(status_code=400, detail="Months must be between 1 and 24")
        
        forecast = await predictive_revenue_system.forecast_growth(business_id, months)
        return {"business_id": business_id, "months": months, "forecast": forecast}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revenue forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/timeline")
async def calculate_revenue_timeline(request: Request):
    """
    Calculate timeline to reach revenue goal
    
    **Validates: Requirements 5.8**
    """
    try:
        if not predictive_revenue_system:
            raise HTTPException(status_code=503, detail="Predictive revenue system not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        target_revenue = data.get('target_revenue')
        
        if not business_id or not target_revenue:
            raise HTTPException(status_code=400, detail="business_id and target_revenue are required")
        
        if target_revenue <= 0:
            raise HTTPException(status_code=400, detail="target_revenue must be positive")
        
        timeline = await predictive_revenue_system.calculate_timeline(business_id, target_revenue)
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Timeline calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/growth/revenue-projection")
async def project_campaign_revenue(request: Request):
    """
    Project revenue for a specific campaign configuration
    
    **Validates: Requirements 5.2, 5.3**
    """
    try:
        if not predictive_revenue_system:
            raise HTTPException(status_code=503, detail="Predictive revenue system not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        campaign_config = data.get('campaign_config', {})
        
        if not business_id:
            raise HTTPException(status_code=400, detail="business_id is required")
        
        projection = await predictive_revenue_system.project_revenue(business_id, campaign_config)
        return projection
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revenue projection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ADDITIONAL GROWTH OS ENDPOINTS ====================

@api_router.post("/campaigns/launch")
async def launch_campaign_v2(request: Request):
    """
    Launch a complete marketing campaign with one click
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**
    """
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        goal = data.get('goal')
        channels = data.get('channels', [])
        budget = data.get('budget', 0)
        
        if not business_id or not goal:
            raise HTTPException(status_code=400, detail="business_id and goal are required")
        
        if not channels:
            raise HTTPException(status_code=400, detail="At least one channel is required")
        
        result = await campaign_launcher.launch_campaign(business_id, goal, channels, budget)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Campaign launch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/campaigns/{campaign_id}")
async def get_campaign_details(campaign_id: str):
    """
    Get campaign status and performance details
    
    **Validates: Requirements 2.8**
    """
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        campaign = await campaign_launcher.get_campaign_status(campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return campaign
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get campaign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign_v2(campaign_id: str):
    """
    Pause an active campaign
    
    **Validates: Requirements 2.9**
    """
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        success = await campaign_launcher.pause_campaign(campaign_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found or not active")
        
        return {"success": True, "message": f"Campaign {campaign_id} paused"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pause campaign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign_v2(campaign_id: str):
    """
    Resume a paused campaign
    
    **Validates: Requirements 2.9**
    """
    try:
        if not campaign_launcher:
            raise HTTPException(status_code=503, detail="Campaign launcher not available")
        
        success = await campaign_launcher.resume_campaign(campaign_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found or not paused")
        
        return {"success": True, "message": f"Campaign {campaign_id} resumed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume campaign error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/autonomous/enable")
async def enable_autonomous_mode_v2(request: Request):
    """
    Enable autonomous marketing mode for a business
    
    **Validates: Requirements 10.1, 10.2, 10.8**
    """
    try:
        if not autonomous_engine:
            raise HTTPException(status_code=503, detail="Autonomous engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        config = data.get('config', {})
        
        if not business_id:
            raise HTTPException(status_code=400, detail="business_id is required")
        
        # Validate config
        if 'budget_limit' not in config:
            raise HTTPException(status_code=400, detail="budget_limit is required in config")
        
        success = await autonomous_engine.enable_autonomous_mode(business_id, config)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to enable autonomous mode")
        
        return {"success": True, "message": "Autonomous mode enabled", "business_id": business_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enable autonomous mode error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/autonomous/disable")
async def disable_autonomous_mode_v2(request: Request):
    """
    Disable autonomous marketing mode for a business
    
    **Validates: Requirements 10.9**
    """
    try:
        if not autonomous_engine:
            raise HTTPException(status_code=503, detail="Autonomous engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        reason = data.get('reason', 'user_requested')
        
        if not business_id:
            raise HTTPException(status_code=400, detail="business_id is required")
        
        success = await autonomous_engine.disable_autonomous_mode(business_id, reason)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to disable autonomous mode")
        
        return {"success": True, "message": "Autonomous mode disabled", "business_id": business_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disable autonomous mode error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/autonomous/status/{business_id}")
async def get_autonomous_status_v2(business_id: str):
    """
    Get autonomous mode status and recent actions
    
    **Validates: Requirements 10.7**
    """
    try:
        if not autonomous_engine:
            raise HTTPException(status_code=503, detail="Autonomous engine not available")
        
        status = await autonomous_engine.get_autonomous_status(business_id)
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get autonomous status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/competitors/add")
async def add_competitor(request: Request):
    """
    Add a competitor to monitor
    
    **Validates: Requirements 6.1, 6.2, 6.9**
    """
    try:
        if not competitor_hijacking_engine:
            raise HTTPException(status_code=503, detail="Competitor hijacking engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        competitor_url = data.get('competitor_url')
        
        if not business_id or not competitor_url:
            raise HTTPException(status_code=400, detail="business_id and competitor_url are required")
        
        competitor_id = await competitor_hijacking_engine.add_competitor(business_id, competitor_url)
        
        return {"success": True, "competitor_id": competitor_id, "message": "Competitor added for monitoring"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add competitor error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/competitors/{business_id}")
async def get_competitors(business_id: str):
    """
    Get all monitored competitors for a business
    
    **Validates: Requirements 6.9**
    """
    try:
        if not competitor_hijacking_engine:
            raise HTTPException(status_code=503, detail="Competitor hijacking engine not available")
        
        competitors = await competitor_hijacking_engine.monitor_competitors(business_id)
        return {"competitors": competitors, "count": len(competitors)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get competitors error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/competitors/{competitor_id}/strategies")
async def get_competitor_strategies(competitor_id: str):
    """
    Get counter-strategies to beat a competitor
    
    **Validates: Requirements 6.5, 6.8**
    """
    try:
        if not competitor_hijacking_engine:
            raise HTTPException(status_code=503, detail="Competitor hijacking engine not available")
        
        # Get competitor from database
        competitor = await db.competitors.find_one({'id': competitor_id})
        if not competitor:
            raise HTTPException(status_code=404, detail="Competitor not found")
        
        business_id = competitor.get('business_id')
        strategies = await competitor_hijacking_engine.suggest_counter_strategies(business_id, competitor_id)
        
        return {"competitor_id": competitor_id, "strategies": strategies, "count": len(strategies)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get competitor strategies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/content/viral")
async def generate_viral_content_v2(request: Request):
    """
    Generate viral-optimized content
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7**
    """
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        topic = data.get('topic')
        platform = data.get('platform', 'social')
        
        if not business_id or not topic:
            raise HTTPException(status_code=400, detail="business_id and topic are required")
        
        content = await growth_engine.generate_viral_content(business_id, topic, platform)
        
        return {"content": content, "count": len(content)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate viral content error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/content/campaign-assets")
async def generate_campaign_assets(request: Request):
    """
    Generate complete campaign assets for 1-click launch
    
    **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8**
    """
    try:
        if not growth_engine:
            raise HTTPException(status_code=503, detail="Growth engine not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        goal = data.get('goal')
        
        if not business_id or not goal:
            raise HTTPException(status_code=400, detail="business_id and goal are required")
        
        assets = await growth_engine.generate_campaign_assets(goal, business_id)
        
        if not assets:
            raise HTTPException(status_code=500, detail="Failed to generate campaign assets")
        
        return assets
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate campaign assets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/conversion/analyze")
async def analyze_conversion(request: Request):
    """
    Analyze landing page and identify conversion bottlenecks
    
    **Validates: Requirements 8.1, 8.2, 8.7**
    """
    try:
        if not conversion_optimization_ai:
            raise HTTPException(status_code=503, detail="Conversion optimization AI not available")
        
        data = await request.json()
        page_url = data.get('page_url')
        business_id = data.get('business_id')
        
        if not page_url or not business_id:
            raise HTTPException(status_code=400, detail="page_url and business_id are required")
        
        analysis = await conversion_optimization_ai.analyze_page(page_url, business_id)
        
        if not analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze page")
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/conversion/ab-test")
async def create_ab_test(request: Request):
    """
    Create A/B test with variations
    
    **Validates: Requirements 8.3, 8.4**
    """
    try:
        if not conversion_optimization_ai:
            raise HTTPException(status_code=503, detail="Conversion optimization AI not available")
        
        data = await request.json()
        page_id = data.get('page_id')
        variations = data.get('variations', [])
        
        if not page_id or not variations:
            raise HTTPException(status_code=400, detail="page_id and variations are required")
        
        test_id = await conversion_optimization_ai.run_ab_test(page_id, variations)
        
        return {"success": True, "test_id": test_id, "message": "A/B test started"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create A/B test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/funnels/create")
async def create_funnel(request: Request):
    """
    Create automated lead funnel
    
    **Validates: Requirements 9.1, 9.2, 9.4, 9.9**
    """
    try:
        if not lead_funnel_automator:
            raise HTTPException(status_code=503, detail="Lead funnel automator not available")
        
        data = await request.json()
        business_id = data.get('business_id')
        goal = data.get('goal')
        
        if not business_id or not goal:
            raise HTTPException(status_code=400, detail="business_id and goal are required")
        
        funnel = await lead_funnel_automator.create_funnel(business_id, goal)
        
        if not funnel:
            raise HTTPException(status_code=500, detail="Failed to create funnel")
        
        return funnel
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create funnel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/funnels/{funnel_id}/leads")
async def add_lead_to_funnel(funnel_id: str, request: Request):
    """
    Add lead to funnel
    
    **Validates: Requirements 9.3, 9.5**
    """
    try:
        if not lead_funnel_automator:
            raise HTTPException(status_code=503, detail="Lead funnel automator not available")
        
        data = await request.json()
        lead_data = {
            'email': data.get('email'),
            'name': data.get('name'),
            'company': data.get('company')
        }
        
        if not lead_data['email']:
            raise HTTPException(status_code=400, detail="email is required")
        
        lead_id = await lead_funnel_automator.add_lead(funnel_id, lead_data)
        
        return {"success": True, "lead_id": lead_id, "funnel_id": funnel_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add lead error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/funnels/{funnel_id}/analytics")
async def get_funnel_analytics(funnel_id: str):
    """
    Get funnel analytics and conversion rates
    
    **Validates: Requirements 9.9**
    """
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Get funnel
        funnel = await db.lead_funnels.find_one({'id': funnel_id})
        if not funnel:
            raise HTTPException(status_code=404, detail="Funnel not found")
        
        # Get leads in funnel
        leads = await db.leads.find({'funnel_id': funnel_id}).to_list(length=10000)
        
        # Calculate analytics
        total_leads = len(leads)
        active_leads = len([l for l in leads if l.get('status') == 'active'])
        converted_leads = len([l for l in leads if l.get('converted')])
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Stage breakdown
        stage_breakdown = {}
        for stage in ['Awareness', 'Interest', 'Decision', 'Action']:
            stage_leads = len([l for l in leads if l.get('current_stage') == stage])
            stage_breakdown[stage] = {
                'count': stage_leads,
                'percentage': (stage_leads / total_leads * 100) if total_leads > 0 else 0
            }
        
        analytics = {
            'funnel_id': funnel_id,
            'funnel_name': funnel.get('funnel_name'),
            'total_leads': total_leads,
            'active_leads': active_leads,
            'converted_leads': converted_leads,
            'conversion_rate': round(conversion_rate, 2),
            'stage_breakdown': stage_breakdown,
            'created_at': funnel.get('created_at')
        }
        
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get funnel analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== APP SETUP ====================
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Allow all origins in development
    allow_methods=["*"],
    allow_headers=["*"],
)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
