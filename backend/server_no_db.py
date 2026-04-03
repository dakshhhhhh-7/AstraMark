"""
AstraMark Server - No Database Mode (For Testing)
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import uuid

# In-memory storage
users_db: Dict[str, Dict] = {}
analyses_db: Dict[str, Dict] = {}

# Configuration
SECRET_KEY = "kBxXt2gKL4CtKp0N0Cnjx65ZZFDRpl2fdfwoL8XBP24"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="AstraMark API - Testing Mode (No Database)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class BusinessInput(BaseModel):
    business_type: str
    target_market: str
    monthly_budget: str
    primary_goal: str
    additional_info: Optional[str] = None

# Helper functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Routes
@app.get("/")
async def root():
    return {"message": "AstraMark API - Testing Mode (In-Memory Database)", "status": "running"}

@app.get("/api/")
async def api_root():
    return {"message": "AstraMark AI Marketing Platform API - Testing Mode", "users_count": len(users_db)}

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate):
    """Register a new user (in-memory)"""
    if user_in.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    users_db[user_in.email] = {
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": get_password_hash(user_in.password),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    return {
        "id": user_id,
        "email": user_in.email,
        "full_name": user_in.full_name,
        "message": "User registered successfully (in-memory)"
    }

@app.post("/api/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm):
    """Login and get access token"""
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    return Token(access_token=access_token, token_type="bearer")

@app.post("/api/analyze")
async def analyze_business(business_input: BusinessInput):
    """Generate business analysis (mock data)"""
    analysis_id = str(uuid.uuid4())
    
    analysis = {
        "analysis_id": analysis_id,
        "business_id": str(uuid.uuid4()),
        "overview": f"Analysis for {business_input.business_type} targeting {business_input.target_market}",
        "market_analysis": {
            "market_size": "$10B+ (Estimated)",
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
                "demographics": "25-40, Urban, Middle Income",
                "psychographics": "Early adopter, ambitious, data-driven",
                "pain_points": ["Efficiency", "Scaling", "Market Visibility"],
                "buying_triggers": ["Automation", "ROI", "Time Savings"],
                "objections": ["Cost", "Complexity", "Learning Curve"]
            }
        ],
        "ai_insights": [
            {
                "insight_type": "Market Gap",
                "description": "High demand for specialized solutions in this vertical",
                "confidence": 85
            }
        ],
        "strategies": [
            {
                "channel": "SEO",
                "strategy": "Focus on long-tail keywords and local SEO",
                "content_ideas": ["How-to Guides", "Case Studies", "Industry Trends"],
                "posting_schedule": "2x Weekly",
                "kpi_benchmarks": {"organic_traffic": "1000/mo", "conversion_rate": "3%"}
            },
            {
                "channel": "Content Marketing",
                "strategy": "Educational content and thought leadership",
                "content_ideas": ["Blog Posts", "Whitepapers", "Webinars"],
                "posting_schedule": "3x Weekly",
                "kpi_benchmarks": {"engagement_rate": "5%", "lead_generation": "50/mo"}
            }
        ],
        "revenue_projection": {
            "min_monthly": f"${int(business_input.monthly_budget.replace('$', '').replace(',', '')) * 2}",
            "max_monthly": f"${int(business_input.monthly_budget.replace('$', '').replace(',', '')) * 10}",
            "growth_timeline": "6-12 Months"
        },
        "virality_score": 75,
        "retention_score": 80,
        "ai_verdict": "High Growth Potential",
        "confidence_score": 85,
        "biggest_opportunity": "Niche market dominance",
        "biggest_risk": "Competitor speed to market",
        "next_action": "Launch MVP marketing campaign",
        "created_at": datetime.utcnow().isoformat()
    }
    
    analyses_db[analysis_id] = analysis
    return analysis

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "testing (in-memory)",
        "users_count": len(users_db),
        "analyses_count": len(analyses_db),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
