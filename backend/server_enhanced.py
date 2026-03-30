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
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
import os
import logging
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

from google import genai
from google.genai import types

# Import our services
from config import settings, validate_required_settings
from auth_service import AuthService, AuthTokens, UserInDB, create_auth_tokens
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

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address)

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    global client, db, client_ai, content_service, auth_service, payment_service, health_check, usage_tracker
    
    # 1. Database Connection
    try:
        client = AsyncIOMotorClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        db = client[settings.db_name]
        logger.info(f"Connected to MongoDB: {settings.mongo_url}")
        
        # Initialize services
        auth_service = AuthService(db)
        payment_service = UnifiedPaymentService(db)
        health_check = HealthCheck(db)
        usage_tracker = UsageTracker(db)
        
        # Update Scanner with DB
        background_scanner.db = db
        background_scanner.start()
    except Exception as e:
        logger.critical(f"MongoDB connection failed: {e}")
        raise e

    # 2. AI Client Initialization
    if settings.google_api_key:
        try:
            client_ai = genai.Client(api_key=settings.google_api_key)
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
    if client:
        client.close()
    logger.info("Server shutdown complete")

app = FastAPI(title="AstraMark AI Marketing API - Enhanced", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
add_exception_handlers(app)
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
    # bcrypt has a 72-byte limit, truncate if necessary
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # bcrypt has a 72-byte limit, truncate if necessary
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_email(token_data.email)  # type: ignore[arg-type]
    if user is None:
        raise credentials_exception
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
                PRIMARY_MODEL = "models/gemini-2.5-flash"
                FALLBACK_MODELS = ["models/gemini-2.5-pro", "models/gemini-2.0-flash"]
                models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
                
                for model_name in models_to_try:
                    try:
                        generation_config = types.GenerateContentConfig(
                            temperature=0.7,
                            response_mime_type="application/json",
                            system_instruction=system_profile
                        )
                        
                        response = await client_ai.aio.models.generate_content(
                            model=model_name,
                            contents=user_prompt,
                            config=generation_config
                        )
                        
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
                market_analysis[field] = ', '.join(market_analysis[field])
            elif not isinstance(market_analysis.get(field), str):
                market_analysis[field] = str(market_analysis.get(field, 'Not specified'))
    
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


@api_router.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 password flow endpoint.

    Frontend sends:
      username=<email>&password=<password>
    as x-www-form-urlencoded.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


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
    plan_id: str,
    gateway: str,
    success_url: str,
    cancel_url: str,
    current_user: UserInDB = Depends(get_current_user_dep)
):
    """Create checkout session for subscription"""
    try:
        session = await payment_service.create_checkout_session(
            current_user.id, plan_id, gateway, success_url, cancel_url
        )
        return session
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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

# ==================== APP SETUP ====================
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(','),
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
