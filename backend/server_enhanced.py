"""
Enhanced AstraMark Server with Live Market Data, Background Scanning, and Content Generation
"""
from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import json
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

from google import genai
from google.genai import types

# Import our new services
from serp_service import serp_service
from blockchain_service import blockchain_service
from pdf_service import pdf_generator
from content_service import ContentGenerationService
from scanner_service import BackgroundScanner

# Import models
from models import (
    BusinessInput, BusinessProfile, MarketAnalysis, UserPersona, AIInsight,
    ChannelStrategy, RevenueProjection, MarketSignal, BlockchainProof,
    AILearningUpdate, ExecutionAction, CompetitorInsight, AnalysisResult
)

from logging_config import configure_logging
from middleware.error_handler import add_exception_handlers
from auth.router import router as auth_router
from auth.dependencies import get_current_active_user
from users.user_models import User

# ==================== DATA MODELS ====================


# ==================== INITIALIZATION ====================
load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)

# Database Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Global Services
client = None
db = None
client_ai = None
content_service = None
background_scanner = BackgroundScanner(serp_service, None) 

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AstraMark Enhanced Server...")
    global client, db, client_ai, content_service
    
    # 1. Database Connection
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        db = client[DB_NAME]
        logger.info(f"Connected to MongoDB: {MONGO_URL}")
        
        # Update Scanner with DB
        background_scanner.db = db
        background_scanner.start() # Assumes non-blocking or managed
    except Exception as e:
        logger.critical(f"MongoDB connection failed: {e}")
        raise e

    # 2. AI Client Initialization
    if GOOGLE_API_KEY:
        try:
            client_ai = genai.Client(api_key=GOOGLE_API_KEY)
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

    yield
    
    # Shutdown
    logger.info("Shutting down...")
    background_scanner.stop()
    if client:
        client.close()
    logger.info("Server shutdown complete")

    logger.info("Server shutdown complete")

app = FastAPI(title="AstraMark AI Marketing API - Enhanced", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
add_exception_handlers(app)
api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)

# ==================== HELPER FUNCTIONS ====================
async def generate_market_analysis_with_live_data(business: BusinessInput) -> Dict[str, Any]:
    """Generate comprehensive market analysis using AI + live market data"""
    
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Server Configuration Error: API Key missing.")

    # Fetch live competitor data
    competitor_data = await serp_service.search_competitors(
        business.business_type,
        business.target_market
    )
    
    # Fetch market trends
    market_trends = await serp_service.get_market_trends(business.business_type)
    
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
            "market_size": "Estimated market size with specifics",
            "growth_rate": "Annual growth rate percentage",
            "entry_barriers": "Key barriers to entry",
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
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def call_model_with_retry(client, model_name, prompt, config):
        return await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )

    try:
        # Try multiple models in order of preference
        models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        model = None
        last_error = None
        analysis_data = None
        
        if not client_ai:
             raise Exception("AI Client not initialized")
        
        for model_name in models_to_try:
            try:
                # Configure generation
                generation_config = types.GenerateContentConfig(
                    temperature=0.7,
                    response_mime_type="application/json",
                    system_instruction=system_profile
                )
                
                logger.info(f"Attempting analysis with model: {model_name}")
                
                # Use retry wrapper
                response = await call_model_with_retry(client_ai, model_name, user_prompt, generation_config)
                
                # If we get here, the call worked, but we need to verify JSON validity
                response_text = response.text.strip()
                
                # Cleanup potential markdown
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                # Validate JSON (this will raise exception if invalid, triggering fallback)
                analysis_data = json.loads(response_text)
                
                # If valid, we're done
                model = model_name
                break
            except Exception as e:
                logger.warning(f"Model {model_name} failed (API or JSON error): {e}")
                last_error = e
                continue
        
        if not model or not analysis_data:
            # If all models fail, return a mock response to keep the app usable
            logger.error(f"All AI models failed. Using fallback mock data. Last error: {last_error}")
            return {
                "overview": f"Analysis generated in offline mode due to high AI demand. (Error: {str(last_error)[:100]}...)",
                "market_analysis": {
                    "market_size": "Estimated $10B+ (Offline Estimate)",
                    "growth_rate": "15% CAGR",
                    "entry_barriers": "Moderate",
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
                        "confidence": 80
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
                "confidence_score": 70,
                "biggest_opportunity": "Niche dominance",
                "biggest_risk": "Competitor speed",
                "next_action": "Launch MVP marketing campaign"
            }
        
        # Add live competitor data
        analysis_data['competitor_data'] = competitor_data
        analysis_data['market_trends'] = market_trends
        
        return analysis_data
        
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")

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

@api_router.post("/analyze", response_model=AnalysisResult)
@limiter.limit("5/minute")
async def analyze_business(
    request: Request, 
    business_input: BusinessInput, 
    premium: bool = False, 
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user)
):
    """Main AI analysis endpoint with live market data (Authenticated)"""
    try:
        # Save business profile
        business_profile = BusinessProfile(**business_input.model_dump())
        business_doc = business_profile.model_dump()
        business_doc['created_at'] = business_doc['created_at'].isoformat()
        business_doc['owner_id'] = current_user.id # Link to user
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
        analysis_doc['owner_id'] = current_user.id # Link to user
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
        "ai_enabled": bool(GOOGLE_API_KEY),
        "db_connected": client is not None,
        "serp_enabled": serp_service.enabled,
        "blockchain_enabled": blockchain_service.enabled,
        "scanner_enabled": background_scanner.enabled
    }

# ==================== CONTENT GENERATION ENDPOINTS ====================
@api_router.post("/generate/pitch-deck")
async def generate_pitch_deck(analysis_id: str):
    """Generate a pitch deck from analysis"""
    if not content_service:
        raise HTTPException(status_code=503, detail="Content service not available")
    
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        pitch_deck = await content_service.generate_pitch_deck(analysis)
        return pitch_deck
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pitch deck generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate/content-calendar")
async def generate_content_calendar(analysis_id: str, weeks: int = 4):
    """Generate a content calendar from analysis"""
    if not content_service:
        raise HTTPException(status_code=503, detail="Content service not available")
    
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        calendar = await content_service.generate_content_calendar(analysis, weeks)
        return calendar
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content calendar generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate/email-sequence")
async def generate_email_sequence(analysis_id: str, sequence_type: str = "onboarding"):
    """Generate an email sequence from analysis"""
    if not content_service:
        raise HTTPException(status_code=503, detail="Content service not available")
    
    try:
        analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        sequence = await content_service.generate_email_sequence(analysis, sequence_type)
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
