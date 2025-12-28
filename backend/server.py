from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize LLM
EMERGENT_LLM_KEY = os.environ['EMERGENT_LLM_KEY']

# ==================== MODELS ====================
class BusinessInput(BaseModel):
    business_type: str
    target_market: str
    monthly_budget: str
    primary_goal: str
    additional_info: Optional[str] = None

class BusinessProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_type: str
    target_market: str
    monthly_budget: str
    primary_goal: str
    additional_info: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserPersona(BaseModel):
    name: str
    demographics: str
    psychographics: str
    pain_points: List[str]
    buying_triggers: List[str]
    objections: List[str]

class ChannelStrategy(BaseModel):
    channel: str
    strategy: str
    content_ideas: List[str]
    posting_schedule: str
    kpi_benchmarks: Dict[str, str]

class MarketAnalysis(BaseModel):
    market_size: str
    growth_rate: str
    entry_barriers: str
    opportunities: List[str]
    risks: List[str]

class AIInsight(BaseModel):
    insight_type: str
    description: str
    confidence: int

class RevenueProjection(BaseModel):
    min_monthly: str
    max_monthly: str
    growth_timeline: str

class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
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

# ==================== AI ENGINE ====================
async def generate_market_analysis(business: BusinessInput, use_web_search: bool = False) -> Dict[str, Any]:
    """Generate comprehensive market analysis using AI"""
    
    system_prompt = """You are AstraMark, an autonomous AI marketing strategist. You operate as a Chief Marketing Officer, 
    Market Research Analyst, Growth Hacker, and Revenue Architect combined. 
    
    Analyze the business and provide actionable marketing intelligence. Be specific, data-driven, and strategic."""
    
    user_prompt = f"""
    Analyze this business and provide a comprehensive marketing strategy:
    
    Business Type: {business.business_type}
    Target Market: {business.target_market}
    Monthly Budget: {business.monthly_budget}
    Primary Goal: {business.primary_goal}
    Additional Info: {business.additional_info or 'None'}
    
    Provide a detailed analysis in the following JSON structure:
    {{
        "overview": "Brief business snapshot and goal alignment",
        "market_analysis": {{
            "market_size": "Estimated market size with specifics",
            "growth_rate": "Annual growth rate percentage",
            "entry_barriers": "Key barriers to entry",
            "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
            "risks": ["risk1", "risk2", "risk3"]
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
            "min_monthly": "₹XX,XXX",
            "max_monthly": "₹XX,XXX",
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
    
    Return ONLY valid JSON, no markdown or extra text.
    """
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"analysis-{uuid.uuid4()}",
            system_message=system_prompt
        ).with_model("gemini", "gemini-3-flash-preview")
        
        message = UserMessage(text=user_prompt)
        response = await chat.send_message(message)
        
        # Parse JSON response
        # Remove markdown code blocks if present
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        analysis_data = json.loads(response_text)
        return analysis_data
        
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}, Response: {response}")
        raise HTTPException(status_code=500, detail="AI response parsing failed")
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

# ==================== API ROUTES ====================
@api_router.get("/")
async def root():
    return {"message": "AstraMark AI Marketing Platform API"}

@api_router.post("/analyze", response_model=AnalysisResult)
async def analyze_business(business_input: BusinessInput, premium: bool = False):
    """Main AI analysis endpoint"""
    try:
        # Save business profile
        business_profile = BusinessProfile(**business_input.model_dump())
        business_doc = business_profile.model_dump()
        business_doc['created_at'] = business_doc['created_at'].isoformat()
        await db.businesses.insert_one(business_doc)
        
        # Generate AI analysis
        analysis_data = await generate_market_analysis(business_input)
        
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
            is_premium=premium
        )
        
        # Save analysis
        analysis_doc = analysis_result.model_dump()
        analysis_doc['created_at'] = analysis_doc['created_at'].isoformat()
        await db.analyses.insert_one(analysis_doc)
        
        return analysis_result
        
    except Exception as e:
        logging.error(f"Analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analyses", response_model=List[AnalysisResult])
async def get_analyses(limit: int = 10):
    """Get recent analyses"""
    try:
        analyses = await db.analyses.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        # Convert ISO strings back to datetime
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
        "ai_enabled": bool(EMERGENT_LLM_KEY),
        "db_connected": client is not None
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
