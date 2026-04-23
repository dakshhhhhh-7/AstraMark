# Design Document: AI Business Analysis Feature

## Overview

The AI Business Analysis feature provides AstraMark users with comprehensive business feasibility analysis through an interactive conversational interface. Users describe their business idea and budget through natural language chat, and receive detailed market research, financial projections, competitor analysis, risk assessment, and actionable growth strategies compiled into a professional downloadable report.

This feature integrates seamlessly with the existing AstraMark AI Chat panel, leveraging Groq AI for natural language processing, SERP/Apify/Real Market Service for live market data, and MongoDB for session persistence. The system orchestrates multiple analysis components (market research, financial projections, budget allocation, risk assessment) and generates professional PDF reports with charts and visualizations.

**Key Design Principles:**
- **Conversational UX**: Natural language interaction without complex forms
- **Real-time Intelligence**: Live market data from multiple sources
- **Comprehensive Analysis**: Multi-dimensional business evaluation
- **Professional Output**: Publication-ready feasibility reports
- **Session Persistence**: Auto-save and resume capability
- **Multi-currency Support**: INR, USD, EUR with regional context

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                              │
│                    React + Tailwind + Framer Motion                 │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              AI Chat Panel (Enhanced)                        │  │
│  │  • Business Analysis Mode                                    │  │
│  │  • Conversational Interface                                  │  │
│  │  • Real-time Status Updates                                  │  │
│  │  • Report Preview & Download                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   Budget     │  │   Analysis   │  │  History & Session       │ │
│  │   Input      │  │   Progress   │  │  Management              │ │
│  │  Component   │  │  Indicator   │  │  Component               │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ HTTPS REST API
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND LAYER                          │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         Business Analysis API Router                         │  │
│  │  POST   /api/ai/business-analysis/start                      │  │
│  │  POST   /api/ai/business-analysis/chat                       │  │
│  │  POST   /api/ai/business-analysis/generate-report            │  │
│  │  GET    /api/ai/business-analysis/sessions                   │  │
│  │  GET    /api/ai/business-analysis/download/{report_id}       │  │
│  │  PUT    /api/ai/business-analysis/sessions/{id}/resume       │  │
│  │  DELETE /api/ai/business-analysis/sessions/{id}              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         Business Analysis Engine (Orchestrator)              │  │
│  │  • Conversation State Management                             │  │
│  │  • Multi-step Analysis Workflow                              │  │
│  │  • Component Coordination                                    │  │
│  │  • Error Handling & Fallbacks                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   Market     │  │   Budget     │  │  Financial               │ │
│  │  Research    │  │  Analyzer    │  │  Projector               │ │
│  │  Service     │  │              │  │                          │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────────────┘ │
│         │                  │                  │                     │
│  ┌──────┴──────────────────┴──────────────────┴──────────────────┐ │
│  │              Report Generator Service                         │ │
│  │  • PDF Compilation (ReportLab)                                │ │
│  │  • Chart Generation (matplotlib/plotly)                       │ │
│  │  • DOCX Export                                                │ │
│  │  • JSON Export                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   Groq AI    │  │   Growth     │  │  Existing Services       │ │
│  │   Service    │  │   Engine     │  │  • SERP                  │ │
│  │  (Primary)   │  │  Integration │  │  • Apify                 │ │
│  │              │  │              │  │  • Real Market           │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└────────┬──────────────┬──────────────┬──────────────┬──────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────┐
│  Groq API    │ │ External │ │  MongoDB     │ │  Exchange    │
│  (Llama 3.3) │ │ Market   │ │  Database    │ │  Rate API    │
│              │ │ Data APIs│ │              │ │              │
│              │ │          │ │ Collections: │ │ • Currency   │
│              │ │ • SERP   │ │ • analysis_  │ │   Conversion │
│              │ │ • Apify  │ │   sessions   │ │              │
│              │ │ • Real   │ │ • business_  │ │              │
│              │ │   Market │ │   analysis_  │ │              │
│              │ │          │ │   reports    │ │              │
│              │ │          │ │ • market_    │ │              │
│              │ │          │ │   research_  │ │              │
│              │ │          │ │   cache      │ │              │
└──────────────┘ └──────────┘ └──────────────┘ └──────────────┘
```

### Component Interaction Flow

```
User Input → AI Chat Panel → Business Analysis Engine
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
            Market Research    Budget Analyzer   Financial Projector
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
                            Report Generator
                                      │
                                      ▼
                            PDF/DOCX/JSON Output
```

---

## Components and Interfaces

### 1. Business Analysis Engine

**Purpose**: Orchestrates the entire analysis workflow, manages conversation state, and coordinates between components.

**Key Responsibilities:**
- Conversation flow management
- Business idea extraction and validation
- Budget specification and validation
- Component orchestration
- Session persistence
- Error handling and recovery

**Interface:**

```python
class BusinessAnalysisEngine:
    def __init__(self, db: AsyncIOMotorDatabase, groq_service: GroqService, 
                 market_research_service: MarketResearchService,
                 budget_analyzer: BudgetAnalyzer,
                 financial_projector: FinancialProjector,
                 report_generator: ReportGenerator):
        """Initialize the business analysis engine"""
        
    async def start_session(self, user_id: str) -> AnalysisSession:
        """Start a new business analysis session"""
        
    async def process_message(self, session_id: str, message: str) -> ChatResponse:
        """Process user message and return AI response"""
        
    async def extract_business_idea(self, conversation_history: List[Message]) -> BusinessIdea:
        """Extract structured business idea from conversation"""
        
    async def extract_budget(self, conversation_history: List[Message]) -> Budget:
        """Extract budget amount and currency from conversation"""
        
    async def generate_analysis(self, session_id: str) -> AnalysisResult:
        """Generate complete business analysis"""
        
    async def save_session(self, session: AnalysisSession) -> None:
        """Auto-save session state"""
        
    async def resume_session(self, session_id: str) -> AnalysisSession:
        """Resume interrupted session"""
```

**State Machine:**

```
START → GREETING → BUSINESS_IDEA_COLLECTION → BUSINESS_IDEA_CONFIRMATION →
BUDGET_COLLECTION → BUDGET_CONFIRMATION → ANALYSIS_IN_PROGRESS →
ANALYSIS_COMPLETE → REPORT_GENERATION → COMPLETE
```

### 2. Market Research Service

**Purpose**: Aggregates market data from multiple sources (SERP, Apify, Real Market Service) to provide comprehensive market intelligence.

**Key Responsibilities:**
- Competitor identification and analysis
- Market size estimation
- Industry trend extraction
- Target audience demographics
- Data caching and freshness management

**Interface:**

```python
class MarketResearchService:
    def __init__(self, serp_service: SERPService, apify_service: ApifyService,
                 real_market_service: RealMarketService, db: AsyncIOMotorDatabase):
        """Initialize market research service"""
        
    async def research_market(self, business_idea: BusinessIdea, 
                             currency: str) -> MarketResearchResult:
        """Conduct comprehensive market research"""
        
    async def find_competitors(self, business_type: str, 
                              target_market: str, 
                              limit: int = 10) -> List[Competitor]:
        """Identify direct competitors"""
        
    async def estimate_market_size(self, industry: str, 
                                   geography: str) -> MarketSize:
        """Estimate total addressable market"""
        
    async def extract_trends(self, industry: str, 
                            count: int = 5) -> List[Trend]:
        """Extract current industry trends"""
        
    async def identify_target_audience(self, business_type: str) -> TargetAudience:
        """Identify target audience demographics"""
        
    async def get_cached_research(self, cache_key: str) -> Optional[MarketResearchResult]:
        """Retrieve cached research data"""
        
    async def cache_research(self, cache_key: str, data: MarketResearchResult, 
                            ttl_hours: int = 24) -> None:
        """Cache research data with TTL"""
```

**Data Models:**

```python
class Competitor(BaseModel):
    name: str
    domain: str
    description: str
    strengths: List[str]
    weaknesses: List[str]
    market_position: str
    pricing_strategy: str
    estimated_traffic: Optional[str]
    ad_spend_monthly: Optional[str]

class MarketSize(BaseModel):
    value: str  # e.g., "$10B"
    confidence_interval: str  # e.g., "$8B - $12B"
    confidence_level: str  # "High", "Medium", "Low"
    source: str

class Trend(BaseModel):
    title: str
    description: str
    relevance_score: float
    source: str
    published_date: datetime

class TargetAudience(BaseModel):
    age_range: str
    income_level: str
    geographic_distribution: List[str]
    behavioral_characteristics: List[str]
    pain_points: List[str]

class MarketResearchResult(BaseModel):
    competitors: List[Competitor]
    market_size: MarketSize
    trends: List[Trend]
    target_audience: TargetAudience
    research_timestamp: datetime
    data_sources: List[str]
```

### 3. Budget Analyzer

**Purpose**: Breaks down user budget into optimal allocations across business categories with industry-specific benchmarks.

**Key Responsibilities:**
- Budget validation and currency conversion
- Category allocation calculation
- Sub-category itemization
- Industry benchmark application
- Regional cost adjustment

**Interface:**

```python
class BudgetAnalyzer:
    def __init__(self, exchange_rate_service: ExchangeRateService):
        """Initialize budget analyzer"""
        
    async def analyze_budget(self, budget_amount: float, currency: str,
                            business_type: str, industry: str) -> BudgetBreakdown:
        """Generate comprehensive budget breakdown"""
        
    async def validate_budget(self, amount: float, currency: str) -> ValidationResult:
        """Validate budget amount against thresholds"""
        
    async def convert_currency(self, amount: float, from_currency: str,
                              to_currency: str) -> float:
        """Convert between currencies using real-time rates"""
        
    def calculate_allocations(self, budget: float, business_type: str) -> Dict[str, float]:
        """Calculate category allocations based on industry benchmarks"""
        
    def generate_sub_categories(self, category: str, allocation: float,
                               business_type: str) -> List[SubCategory]:
        """Generate itemized sub-categories"""
```

**Data Models:**

```python
class BudgetBreakdown(BaseModel):
    total_budget: float
    currency: str
    categories: List[CategoryAllocation]
    sub_categories: Dict[str, List[SubCategory]]
    allocation_rationale: str
    industry_benchmarks: Dict[str, str]

class CategoryAllocation(BaseModel):
    category: str  # "Marketing", "Operations", "Technology", "Staffing", "Contingency"
    amount: float
    percentage: float
    rationale: str

class SubCategory(BaseModel):
    name: str
    amount: float
    description: str
    priority: str  # "High", "Medium", "Low"
```

**Allocation Logic:**

```python
# Industry-specific allocation percentages
ALLOCATION_BENCHMARKS = {
    "SaaS": {
        "Marketing": (25, 35),  # (min%, max%)
        "Operations": (15, 25),
        "Technology": (20, 30),
        "Staffing": (25, 35),
        "Contingency": (10, 15)
    },
    "E-commerce": {
        "Marketing": (30, 40),
        "Operations": (25, 35),
        "Technology": (15, 25),
        "Staffing": (15, 25),
        "Contingency": (10, 15)
    },
    # ... more industries
}
```

### 4. Financial Projector

**Purpose**: Generates detailed financial projections including revenue forecasts, cost projections, profitability analysis, and ROI calculations.

**Key Responsibilities:**
- Revenue forecasting (monthly/quarterly)
- Cost projection (fixed/variable)
- Break-even analysis
- Profit margin calculation
- ROI calculation
- Cash flow projection
- Scenario modeling (best/realistic/worst case)

**Interface:**

```python
class FinancialProjector:
    def __init__(self, industry_benchmarks: Dict[str, Any]):
        """Initialize financial projector"""
        
    async def generate_projections(self, business_idea: BusinessIdea,
                                   budget: BudgetBreakdown,
                                   market_research: MarketResearchResult) -> FinancialProjections:
        """Generate comprehensive financial projections"""
        
    def forecast_revenue(self, business_type: str, market_size: MarketSize,
                        months: int = 36) -> List[RevenueProjection]:
        """Forecast revenue for specified period"""
        
    def project_costs(self, budget: BudgetBreakdown, months: int = 36) -> List[CostProjection]:
        """Project costs over time"""
        
    def calculate_break_even(self, revenue_projections: List[RevenueProjection],
                            cost_projections: List[CostProjection]) -> BreakEvenAnalysis:
        """Calculate break-even point"""
        
    def calculate_margins(self, revenue: float, costs: float) -> ProfitMargins:
        """Calculate profit margins"""
        
    def calculate_roi(self, initial_investment: float,
                     projections: List[RevenueProjection],
                     period_months: int) -> ROICalculation:
        """Calculate ROI for specified period"""
        
    def project_cash_flow(self, revenue_projections: List[RevenueProjection],
                         cost_projections: List[CostProjection]) -> List[CashFlowProjection]:
        """Project monthly cash flow"""
        
    def generate_scenarios(self, base_projections: FinancialProjections) -> ScenarioAnalysis:
        """Generate best/realistic/worst case scenarios"""
```

**Data Models:**

```python
class RevenueProjection(BaseModel):
    period: str  # "Month 1", "Q1", etc.
    revenue: float
    growth_rate: float
    assumptions: List[str]

class CostProjection(BaseModel):
    period: str
    fixed_costs: float
    variable_costs: float
    total_costs: float

class BreakEvenAnalysis(BaseModel):
    break_even_month: int
    break_even_revenue: float
    cumulative_investment_at_break_even: float

class ProfitMargins(BaseModel):
    gross_margin: float
    net_margin: float
    operating_margin: float

class ROICalculation(BaseModel):
    period_months: int
    roi_percentage: float
    total_return: float
    payback_period_months: int

class CashFlowProjection(BaseModel):
    period: str
    inflows: float
    outflows: float
    net_cash_flow: float
    cumulative_cash: float

class ScenarioAnalysis(BaseModel):
    best_case: FinancialProjections
    realistic_case: FinancialProjections
    worst_case: FinancialProjections
    scenario_assumptions: Dict[str, List[str]]

class FinancialProjections(BaseModel):
    revenue_projections: List[RevenueProjection]
    cost_projections: List[CostProjection]
    break_even_analysis: BreakEvenAnalysis
    profit_margins: ProfitMargins
    roi_calculations: Dict[str, ROICalculation]  # "1_year", "2_year", "3_year"
    cash_flow_projections: List[CashFlowProjection]
    scenario_analysis: ScenarioAnalysis
```

### 5. Report Generator

**Purpose**: Compiles all analysis components into professional, downloadable reports in multiple formats (PDF, DOCX, JSON).

**Key Responsibilities:**
- PDF generation with charts and tables
- DOCX generation for editing
- JSON export for programmatic access
- Chart generation (revenue, budget allocation, cash flow)
- Professional formatting and branding
- Secure sharing link generation

**Interface:**

```python
class ReportGenerator:
    def __init__(self, pdf_service: PDFService, db: AsyncIOMotorDatabase):
        """Initialize report generator"""
        
    async def generate_report(self, session_id: str, format: str = "pdf") -> Report:
        """Generate complete feasibility report"""
        
    async def generate_pdf(self, analysis_data: AnalysisData) -> BytesIO:
        """Generate PDF report"""
        
    async def generate_docx(self, analysis_data: AnalysisData) -> BytesIO:
        """Generate DOCX report"""
        
    async def generate_json(self, analysis_data: AnalysisData) -> Dict[str, Any]:
        """Generate JSON export"""
        
    def create_revenue_chart(self, projections: List[RevenueProjection]) -> bytes:
        """Generate revenue projection chart"""
        
    def create_budget_pie_chart(self, breakdown: BudgetBreakdown) -> bytes:
        """Generate budget allocation pie chart"""
        
    def create_cash_flow_chart(self, cash_flow: List[CashFlowProjection]) -> bytes:
        """Generate cash flow chart"""
        
    async def create_sharing_link(self, report_id: str, expiration_days: int) -> SharingLink:
        """Generate secure sharing link"""
        
    async def track_share_access(self, link_id: str, accessor_info: Dict) -> None:
        """Track sharing link access"""
```

**Report Structure:**

```
1. Cover Page
   - Report Title
   - Business Name
   - Generation Date
   - Report ID
   - AstraMark Branding

2. Table of Contents

3. Executive Summary
   - Business Overview
   - Key Findings
   - Recommendation Summary

4. Business Overview
   - Business Idea Description
   - Target Market
   - Primary Goals
   - Budget Summary

5. Market Analysis
   - Market Size & Growth
   - Industry Trends
   - Target Audience Demographics
   - Competitive Landscape

6. Competitor Analysis
   - Competitor Comparison Table
   - Strengths & Weaknesses
   - Market Positioning
   - Competitive Advantages

7. Financial Projections
   - Revenue Forecasts (Chart)
   - Cost Projections
   - Break-even Analysis
   - Profit Margins
   - ROI Calculations
   - Cash Flow Projections (Chart)
   - Scenario Analysis

8. Budget Breakdown
   - Budget Allocation (Pie Chart)
   - Category Details
   - Sub-category Itemization
   - Allocation Rationale

9. Risk Assessment
   - Identified Risks (by category)
   - Risk Severity & Probability
   - Mitigation Strategies
   - Regulatory Requirements

10. Growth Strategy
    - Growth Phases (Launch, Growth, Scale)
    - Milestones & Timelines
    - Customer Acquisition Strategies
    - KPIs to Track
    - 90-Day Action Plan

11. Appendices
    - Data Sources & Citations
    - Methodology
    - Assumptions
    - Disclaimers

12. Footer
    - Page Numbers
    - Generation Timestamp
    - Report ID
```

---

## Data Models

### MongoDB Collections

#### 1. `analysis_sessions`

```python
{
    "_id": ObjectId,
    "session_id": str,  # UUID
    "user_id": str,
    "status": str,  # "in_progress", "completed", "interrupted"
    "conversation_state": str,  # State machine state
    "conversation_history": [
        {
            "role": str,  # "user" or "assistant"
            "content": str,
            "timestamp": datetime
        }
    ],
    "business_idea": {
        "description": str,
        "industry": str,
        "target_market": str,
        "geographic_location": str,
        "product_service_type": str,
        "extracted_at": datetime
    },
    "budget": {
        "amount": float,
        "currency": str,  # "INR", "USD", "EUR"
        "extracted_at": datetime
    },
    "analysis_result_id": Optional[str],  # Reference to business_analysis_reports
    "created_at": datetime,
    "updated_at": datetime,
    "last_activity_at": datetime,
    "expires_at": datetime,  # 24 hours after last activity
    "metadata": {
        "user_agent": str,
        "ip_address": str,
        "session_duration_seconds": int
    }
}
```

**Indexes:**
- `session_id` (unique)
- `user_id` + `created_at` (compound, for history queries)
- `expires_at` (TTL index for auto-cleanup)

#### 2. `business_analysis_reports`

```python
{
    "_id": ObjectId,
    "report_id": str,  # UUID
    "session_id": str,  # Reference to analysis_sessions
    "user_id": str,
    "business_idea": BusinessIdea,
    "budget": BudgetBreakdown,
    "market_research": MarketResearchResult,
    "financial_projections": FinancialProjections,
    "risk_assessment": RiskAssessment,
    "growth_strategy": GrowthStrategy,
    "report_files": {
        "pdf_url": Optional[str],
        "docx_url": Optional[str],
        "json_url": Optional[str]
    },
    "sharing_links": [
        {
            "link_id": str,
            "url": str,
            "created_at": datetime,
            "expires_at": datetime,
            "access_count": int,
            "last_accessed_at": Optional[datetime]
        }
    ],
    "generation_metadata": {
        "generation_time_seconds": float,
        "ai_service_used": str,  # "groq", "gemini", "fallback"
        "data_sources": List[str],
        "confidence_scores": Dict[str, float]
    },
    "created_at": datetime,
    "updated_at": datetime
}
```

**Indexes:**
- `report_id` (unique)
- `user_id` + `created_at` (compound)
- `session_id` (for lookups)

#### 3. `market_research_cache`

```python
{
    "_id": ObjectId,
    "cache_key": str,  # Hash of (business_type + target_market + currency)
    "business_type": str,
    "target_market": str,
    "currency": str,
    "research_data": MarketResearchResult,
    "cached_at": datetime,
    "expires_at": datetime,  # 24 hours TTL
    "hit_count": int,
    "last_accessed_at": datetime
}
```

**Indexes:**
- `cache_key` (unique)
- `expires_at` (TTL index)

---

## AI Conversation Flow

### Conversation Design

**Phase 1: Greeting & Introduction**

```
Assistant: "Hello! I'm your AI Business Analyst. I'll help you evaluate your business idea with comprehensive market research, financial projections, and actionable strategies.

To get started, please describe your business idea. What product or service are you planning to offer, and who is your target market?"

User: [Describes business idea]

Assistant: [Analyzes input, extracts key attributes]
"Great! I understand you're planning to [summarized business idea]. Let me confirm:
- Industry: [extracted industry]
- Target Market: [extracted market]
- Product/Service: [extracted type]
- Location: [extracted location]

Is this correct? Would you like to add or clarify anything?"

User: "Yes, that's correct" / [Provides clarifications]
```

**Phase 2: Budget Collection**

```
Assistant: "Perfect! Now, to provide realistic financial planning, I need to know your available budget.

What is your total investment budget for this business? Please specify the amount and currency (INR, USD, or EUR)."

User: "50 lakhs INR" / "$50,000" / "€45,000"