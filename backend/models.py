from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

class BusinessInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    business_type: str = Field(..., min_length=2, max_length=100, alias="business_type")
    target_market: str = Field(..., min_length=2, max_length=200, alias="target_market")
    monthly_budget: str = Field(..., pattern=r'^\$?\d+([,.]\d+)?$', alias="monthly_budget")
    primary_goal: str = Field(..., min_length=10, max_length=500, alias="primary_goal")
    additional_info: Optional[str] = Field(None, max_length=1000, alias="additional_info")
    
    @validator('business_type')
    def validate_business_type(cls, v):
        # Block SQL injection attempts
        if any(char in v for char in ['<', '>', '{', '}', 'script']):
            raise ValueError('Invalid characters in business_type')
        return v.strip()

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
