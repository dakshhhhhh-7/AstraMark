"""
Enhanced AstraMark Server with Live Market Data, Background Scanning, and Content Generation
"""
from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import json
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import google.generativeai as genai

# Import our new services
from serp_service import serp_service
from blockchain_service import blockchain_service
from pdf_service import pdf_generator
from content_service import ContentGenerationService
from scanner_service import BackgroundScanner

# ==================== DATA MODELS ====================
class BusinessInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    business_type: str = Field(..., alias="business_type")
    target_market: str = Field(..., alias="target_market")
    monthly_budget: str = Field(..., alias="monthly_budget")
    primary_goal: str = Field(..., alias="primary_goal")
    additional_info: Optional[str] = Field(None, alias="additional_info")

class BusinessProfile(BusinessInput):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MarketAnalysis(BaseModel):
    market_size: str
    growth_rate: str
    entry_barriers: str
    opportunities: List[str]
    risks: List[str]
    strengths: List[str]
    weaknesses: List[str]

class UserPersona(BaseModel):
    name: str
    demographics: str
    psychographics: str
    pain_points: List[str]
    buying_triggers: List[str]
    objections: List[str]

class AIInsight(BaseModel):
    insight_type: str
    description: str
    confidence: int

class ChannelStrategy(BaseModel):
    channel: str
    strategy: str
    content_ideas: List[str]
    posting_schedule: str
    kpi_benchmarks: Dict[str, Any]

class RevenueProjection(BaseModel):
    min_monthly: str
    max_monthly: str
    growth_timeline: str

class MarketSignal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    severity: str
    message: str
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%H:%M:%S"))

class BlockchainProof(BaseModel):
    hash: str
    timestamp: str 
    network: str = "AstraMark Intelligence Ledger"
    tx_hash: Optional[str] = None
    verified: bool = False

class AILearningUpdate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    update_type: str
    learning_description: str
    improvement_metric: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%H:%M:%S"))

class ExecutionAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    action_name: str
    description: str
    is_premium: bool = False
    status: str = "active"

class CompetitorInsight(BaseModel):
    name: str
    domain: str
    description: str
    position: int
    estimated_traffic: str
    ad_spend_monthly: Optional[str] = None
    active_campaigns: Optional[int] = None
    top_keywords: Optional[List[str]] = None

class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    overview: str
    market_analysis: MarketAnalysis
    user_personas: List[UserPersona]
    ai_insights: List[AIInsight]
    strategies: List[ChannelStrategy]
    revenue_projection: RevenueProjection
    virality_score: int
    retention_score: int
    ai_verdict: str
    confidence_score: int
    biggest_opportunity: str
    biggest_risk: str
    next_action: str
    is_premium: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Enhanced features
    market_signals: List[MarketSignal] = []
    blockchain_proof: Optional[BlockchainProof] = None
    ai_learning_updates: List[AILearningUpdate] = []
    execution_actions: List[ExecutionAction] = []
    competitor_insights: List[CompetitorInsight] = []
    last_market_scan: str = ""
    monitoring_status: str = "active"

# ==================== INITIALIZATION ====================
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AstraMark AI Marketing API - Enhanced")
api_router = APIRouter(prefix="/api")

# Database Configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Mock DB for when MongoDB is not available
class MockCursor:
    def __init__(self, data):
        self.data = data
        self._sort_key = None
        self._sort_order = 1
        self._limit = None

    def sort(self, key, order=1):
        self._sort_key = key
        self._sort_order = order
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    async def to_list(self, length=None):
        data = list(self.data)
        if self._sort_key:
            try:
                data.sort(key=lambda x: str(x.get(self._sort_key, '')), reverse=(self._sort_order == -1))
            except:
                pass
        if self._limit:
            data = data[:self._limit]
        return data

class MockCollection:
    def __init__(self):
        self.data = []

    async def insert_one(self, doc):
        self.data.append(doc)
        return type('obj', (object,), {'inserted_id': str(uuid.uuid4())})

    def find(self, query=None, projection=None):
        query = query or {}
        filtered_data = self.data
        if "id" in query:
             filtered_data = [d for d in self.data if d.get("id") == query["id"]]
        return MockCursor(filtered_data)

    async def find_one(self, query=None, projection=None):
        query = query or {}
        if "id" in query:
             for d in self.data:
                 if d.get("id") == query["id"]:
                     return d
        return self.data[0] if self.data else None

class MockDB:
    def __init__(self):
        self.businesses = MockCollection()
        self.analyses = MockCollection()
        self.market_signals = MockCollection()
        self.competitor_snapshots = MockCollection()
        self.blockchain_proofs = MockCollection()

# Database Initialization
try:
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=2000)
    db = client[DB_NAME]
    logger.info(f"Connected to MongoDB: {MONGO_URL}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB, falling back to In-Memory DB: {e}")
    db = MockDB()
    client = None

# Initialize Gemini AI
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    logger.info("Gemini AI configured (gemini-2.0-flash)")
else:
    logger.warning("GOOGLE_API_KEY not found")
    gemini_model = None

# Initialize services
content_service = ContentGenerationService(gemini_model) if gemini_model else None
background_scanner = BackgroundScanner(serp_service, db)

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
    async def call_model_with_retry(model_instance, prompt, config):
        return await model_instance.generate_content_async(prompt, generation_config=config)

    try:
        # Try multiple models in order of preference
        models_to_try = ['gemini-2.0-flash', 'gemini-flash-latest', 'gemini-pro-latest']
        model = None
        last_error = None
        response = None
        
        for model_name in models_to_try:
            try:
                # Configure generation
                generation_config = genai.types.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json" 
                )
                
                model_instance = genai.GenerativeModel(model_name, system_instruction=system_profile)
                logger.info(f"Attempting analysis with model: {model_name}")
                
                # Use retry wrapper
                response = await call_model_with_retry(model_instance, user_prompt, generation_config)
                
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
                model = model_instance
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
async def analyze_business(business_input: BusinessInput, premium: bool = False, background_tasks: BackgroundTasks = None):
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
async def health_check():
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
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Start background services"""
    logger.info("Starting AstraMark Enhanced Server...")
    background_scanner.start()
    logger.info("Background scanner started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    background_scanner.stop()
    if client:
        client.close()
    logger.info("Server shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
