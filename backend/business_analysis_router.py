"""
Business Analysis API Router
Provides REST API endpoints for AI-powered business analysis feature
"""
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
import io

from auth_service import AuthService, UserInDB
from business_analysis_service import (
    BusinessAnalysisEngine, AnalysisSession, ChatResponse,
    BusinessIdea, Budget, ConversationState
)
from market_research_service import MarketResearchService, MarketResearchResult
from budget_analyzer import BudgetAnalyzer, BudgetBreakdown
from financial_projector import FinancialProjector, FinancialProjections
from risk_assessment import RiskAssessment, RiskAssessmentResult
from growth_strategy import GrowthStrategy, GrowthStrategyResult
from report_generator import ReportGenerator, Report, AnalysisData, SharingLink
from groq_service import GroqService
from serp_service import serp_service
from apify_market_service import apify_market_service
from real_market_service import real_market_service
from exchange_rate_service import ExchangeRateService

logger = logging.getLogger(__name__)

# ==================== REQUEST/RESPONSE MODELS ====================

class StartSessionRequest(BaseModel):
    """Request to start a new analysis session"""
    pass  # No parameters needed, user is from auth


class StartSessionResponse(BaseModel):
    """Response with new session details"""
    session_id: str
    message: str
    state: str


class ChatRequest(BaseModel):
    """Request to process a chat message"""
    session_id: str
    message: str


class ChatResponseModel(BaseModel):
    """Response to chat message"""
    message: str
    state: str
    session_id: str
    requires_input: bool = True
    metadata: Optional[Dict[str, Any]] = None


class GenerateReportRequest(BaseModel):
    """Request to generate analysis report"""
    session_id: str
    format: str = "pdf"  # "pdf", "docx", "json"


class GenerateReportResponse(BaseModel):
    """Response with report metadata"""
    report_id: str
    session_id: str
    format: str
    file_size: int
    generation_timestamp: datetime
    download_url: str


class SessionSummary(BaseModel):
    """Summary of an analysis session"""
    session_id: str
    state: str
    created_at: datetime
    business_idea_summary: Optional[str] = None
    budget_summary: Optional[str] = None


class SessionListResponse(BaseModel):
    """Response with list of user sessions"""
    sessions: List[SessionSummary]
    total_count: int


class ResumeSessionResponse(BaseModel):
    """Response when resuming a session"""
    session_id: str
    state: str
    message: str
    conversation_history: List[Dict[str, Any]]


class DeleteSessionResponse(BaseModel):
    """Response after deleting a session"""
    success: bool
    message: str


class AnalysisStatusResponse(BaseModel):
    """Response with analysis status"""
    session_id: str
    status: str  # "in_progress", "completed", "failed"
    progress_percentage: int
    current_step: str
    result: Optional[Dict[str, Any]] = None


# ==================== ROUTER SETUP ====================

router = APIRouter(
    prefix="/api/ai/business-analysis",
    tags=["Business Analysis"]
)


# ==================== DEPENDENCY INJECTION ====================

async def get_db(request) -> AsyncIOMotorDatabase:
    """Get database from app state"""
    return request.app.state.db


async def get_auth_service(request) -> AuthService:
    """Get auth service from app state"""
    return request.app.state.auth_service


async def get_business_analysis_engine(request) -> BusinessAnalysisEngine:
    """Get or create business analysis engine"""
    if not hasattr(request.app.state, 'business_analysis_engine'):
        db = await get_db(request)
        groq_service = GroqService()
        request.app.state.business_analysis_engine = BusinessAnalysisEngine(db, groq_service)
    return request.app.state.business_analysis_engine


async def get_market_research_service(request) -> MarketResearchService:
    """Get or create market research service"""
    if not hasattr(request.app.state, 'market_research_service'):
        db = await get_db(request)
        groq_service = GroqService()
        request.app.state.market_research_service = MarketResearchService(
            serp_service,
            apify_market_service,
            real_market_service,
            groq_service,
            db
        )
    return request.app.state.market_research_service


async def get_budget_analyzer(request) -> BudgetAnalyzer:
    """Get or create budget analyzer"""
    if not hasattr(request.app.state, 'budget_analyzer'):
        exchange_rate_service = ExchangeRateService()
        request.app.state.budget_analyzer = BudgetAnalyzer(exchange_rate_service)
    return request.app.state.budget_analyzer


async def get_financial_projector(request) -> FinancialProjector:
    """Get or create financial projector"""
    if not hasattr(request.app.state, 'financial_projector'):
        request.app.state.financial_projector = FinancialProjector()
    return request.app.state.financial_projector


async def get_risk_assessment(request) -> RiskAssessment:
    """Get or create risk assessment"""
    if not hasattr(request.app.state, 'risk_assessment'):
        request.app.state.risk_assessment = RiskAssessment()
    return request.app.state.risk_assessment


async def get_growth_strategy(request) -> GrowthStrategy:
    """Get or create growth strategy"""
    if not hasattr(request.app.state, 'growth_strategy'):
        request.app.state.growth_strategy = GrowthStrategy()
    return request.app.state.growth_strategy


async def get_report_generator(request) -> ReportGenerator:
    """Get or create report generator"""
    if not hasattr(request.app.state, 'report_generator'):
        db = await get_db(request)
        request.app.state.report_generator = ReportGenerator(db)
    return request.app.state.report_generator


async def get_current_user(
    request,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInDB:
    """Get current authenticated user"""
    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
    
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    return await auth_service.get_current_user(token)


# ==================== API ENDPOINTS ====================

@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    request,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine)
):
    """
    Start a new business analysis session
    
    Creates a new conversational session for business analysis.
    Returns session ID and initial greeting message.
    """
    try:
        logger.info(f"Starting new session for user {current_user.id}")
        
        session = await engine.start_session(current_user.id)
        
        # Get the greeting message from conversation history
        greeting_message = session.conversation_history[-1].content if session.conversation_history else "Hello! Let's analyze your business idea."
        
        return StartSessionResponse(
            session_id=session.session_id,
            message=greeting_message,
            state=session.state.value
        )
    
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponseModel)
async def process_chat_message(
    request,
    chat_request: ChatRequest,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine)
):
    """
    Process user message in conversation
    
    Processes user input and returns AI response.
    Manages conversation state and extracts business information.
    """
    try:
        logger.info(f"Processing message for session {chat_request.session_id}")
        
        # Verify user has access to this session
        has_access = await engine.verify_user_access(chat_request.session_id, current_user.id)
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Process message
        response = await engine.process_message(
            chat_request.session_id,
            chat_request.message
        )
        
        return ChatResponseModel(
            message=response.message,
            state=response.state.value,
            session_id=response.session_id,
            requires_input=response.requires_input,
            metadata=response.metadata
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/generate-report", response_model=GenerateReportResponse)
async def generate_report(
    request,
    report_request: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine),
    market_research: MarketResearchService = Depends(get_market_research_service),
    budget_analyzer: BudgetAnalyzer = Depends(get_budget_analyzer),
    financial_projector: FinancialProjector = Depends(get_financial_projector),
    risk_assessment: RiskAssessment = Depends(get_risk_assessment),
    growth_strategy: GrowthStrategy = Depends(get_growth_strategy),
    report_generator: ReportGenerator = Depends(get_report_generator)
):
    """
    Generate comprehensive business analysis report
    
    Compiles all analysis components into a professional report.
    Supports PDF, DOCX, and JSON formats.
    """
    try:
        logger.info(f"Generating report for session {report_request.session_id}")
        
        # Verify session belongs to user
        session = await engine.load_session(report_request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Verify session has required data
        if not session.business_idea or not session.budget:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session incomplete. Please complete the conversation first."
            )
        
        # Validate format
        if report_request.format not in ["pdf", "docx", "json"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Must be 'pdf', 'docx', or 'json'"
            )
        
        # Perform comprehensive analysis
        logger.info("Conducting market research...")
        market_research_result = await market_research.research_market(
            business_type=session.business_idea.product_service_type,
            industry=session.business_idea.industry,
            target_market=session.business_idea.target_market,
            geographic_location=session.business_idea.geographic_location,
            currency=session.budget.currency
        )
        
        logger.info("Analyzing budget...")
        budget_breakdown = await budget_analyzer.analyze_budget(
            budget_amount=session.budget.amount,
            currency=session.budget.currency,
            business_type=session.business_idea.product_service_type,
            industry=session.business_idea.industry
        )
        
        logger.info("Generating financial projections...")
        financial_projections = await financial_projector.generate_projections(
            business_type=session.business_idea.product_service_type,
            industry=session.business_idea.industry,
            initial_budget=session.budget.amount,
            market_size_value=market_research_result.market_size.value
        )
        
        logger.info("Assessing risks...")
        risk_assessment_result = risk_assessment.assess_risks(
            business_type=session.business_idea.product_service_type,
            industry=session.business_idea.industry,
            budget=session.budget.amount,
            geographic_location=session.business_idea.geographic_location
        )
        
        logger.info("Generating growth strategy...")
        growth_strategy_result = growth_strategy.generate_strategy(
            business_type=session.business_idea.product_service_type,
            industry=session.business_idea.industry,
            budget=session.budget.amount,
            target_market=session.business_idea.target_market,
            geographic_location=session.business_idea.geographic_location
        )
        
        # Compile analysis data
        analysis_data = AnalysisData(
            session_id=session.session_id,
            user_id=session.user_id,
            business_idea=session.business_idea.dict(),
            budget=budget_breakdown,
            market_research=market_research_result.dict(),
            financial_projections=financial_projections,
            risk_assessment=risk_assessment_result,
            growth_strategy=growth_strategy_result
        )
        
        # Generate report
        logger.info(f"Generating {report_request.format.upper()} report...")
        report, file_buffer = await report_generator.generate_report(
            analysis_data,
            format=report_request.format
        )
        
        # Store report metadata in session
        session.analysis_result = {
            "market_research": market_research_result.dict(),
            "budget_breakdown": budget_breakdown.dict(),
            "financial_projections": financial_projections.dict(),
            "risk_assessment": risk_assessment_result.dict(),
            "growth_strategy": growth_strategy_result.dict()
        }
        session.report_id = report.report_id
        session.state = ConversationState.COMPLETE
        await engine.save_session(session)
        
        # Store report file in database (in production, would use cloud storage)
        if engine.db:
            await engine.db.business_analysis_reports.insert_one({
                "report_id": report.report_id,
                "session_id": session.session_id,
                "user_id": current_user.id,
                "format": report_request.format,
                "file_size": report.file_size,
                "generation_timestamp": report.generation_timestamp,
                "analysis_data": analysis_data.dict()
            })
        
        download_url = f"/api/ai/business-analysis/download/{report.report_id}"
        
        return GenerateReportResponse(
            report_id=report.report_id,
            session_id=session.session_id,
            format=report_request.format,
            file_size=report.file_size,
            generation_timestamp=report.generation_timestamp,
            download_url=download_url
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/sessions", response_model=SessionListResponse)
async def list_user_sessions(
    request,
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine)
):
    """
    List user's analysis sessions
    
    Returns a list of the user's analysis sessions sorted by most recent first.
    """
    try:
        logger.info(f"Listing sessions for user {current_user.id}")
        
        sessions = await engine.get_user_sessions(current_user.id, limit=limit)
        
        session_summaries = [
            SessionSummary(
                session_id=s["session_id"],
                state=s["state"],
                created_at=datetime.fromisoformat(s["created_at"]) if isinstance(s["created_at"], str) else s["created_at"],
                business_idea_summary=s.get("business_idea_summary"),
                budget_summary=s.get("budget_summary")
            )
            for s in sessions
        ]
        
        return SessionListResponse(
            sessions=session_summaries,
            total_count=len(session_summaries)
        )
    
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/download/{report_id}")
async def download_report(
    request,
    report_id: str,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine),
    report_generator: ReportGenerator = Depends(get_report_generator)
):
    """
    Download generated report
    
    Downloads the report file in the format it was generated.
    """
    try:
        logger.info(f"Downloading report {report_id}")
        
        # Fetch report from database
        if not engine.db:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available"
            )
        
        report_doc = await engine.db.business_analysis_reports.find_one({"report_id": report_id})
        
        if not report_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Verify user has access
        if report_doc["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
        
        # Regenerate report from stored analysis data
        analysis_data_dict = report_doc["analysis_data"]
        analysis_data = AnalysisData(**analysis_data_dict)
        
        report_format = report_doc["format"]
        report, file_buffer = await report_generator.generate_report(
            analysis_data,
            format=report_format
        )
        
        # Determine content type and filename
        content_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "json": "application/json"
        }
        
        extensions = {
            "pdf": "pdf",
            "docx": "docx",
            "json": "json"
        }
        
        content_type = content_types.get(report_format, "application/octet-stream")
        extension = extensions.get(report_format, "bin")
        filename = f"business_analysis_report_{report_id[:8]}.{extension}"
        
        return StreamingResponse(
            file_buffer,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download report: {str(e)}"
        )


@router.put("/sessions/{session_id}/resume", response_model=ResumeSessionResponse)
async def resume_session(
    request,
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine)
):
    """
    Resume an interrupted session
    
    Resumes a previously started session and extends its expiration.
    """
    try:
        logger.info(f"Resuming session {session_id}")
        
        # Load and verify session
        session = await engine.load_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired"
            )
        
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Resume session (extends expiration)
        resumed_session = await engine.resume_session(session_id)
        
        # Convert conversation history to dict
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in resumed_session.conversation_history
        ]
        
        return ResumeSessionResponse(
            session_id=resumed_session.session_id,
            state=resumed_session.state.value,
            message="Session resumed successfully. You can continue where you left off.",
            conversation_history=conversation_history
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume session: {str(e)}"
        )


@router.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(
    request,
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine)
):
    """
    Delete an analysis session
    
    Permanently deletes a session and its associated data.
    """
    try:
        logger.info(f"Deleting session {session_id}")
        
        # Delete session
        deleted = await engine.delete_session(session_id, current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return DeleteSessionResponse(
            success=True,
            message="Session deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/sessions/{session_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    request,
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
    engine: BusinessAnalysisEngine = Depends(get_business_analysis_engine)
):
    """
    Get analysis status for a session
    
    Returns the current status and progress of the analysis.
    """
    try:
        logger.info(f"Getting status for session {session_id}")
        
        # Load session
        session = await engine.load_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Determine status and progress
        state_progress = {
            ConversationState.GREETING: (0, "Starting conversation"),
            ConversationState.BUSINESS_IDEA_COLLECTION: (20, "Collecting business idea"),
            ConversationState.BUSINESS_IDEA_CONFIRMATION: (40, "Confirming business idea"),
            ConversationState.BUDGET_COLLECTION: (60, "Collecting budget information"),
            ConversationState.BUDGET_CONFIRMATION: (80, "Confirming budget"),
            ConversationState.ANALYSIS_IN_PROGRESS: (90, "Analyzing data"),
            ConversationState.ANALYSIS_COMPLETE: (95, "Analysis complete"),
            ConversationState.REPORT_GENERATION: (98, "Generating report"),
            ConversationState.COMPLETE: (100, "Complete")
        }
        
        progress, current_step = state_progress.get(
            session.state,
            (0, "Unknown")
        )
        
        # Determine overall status
        if session.state == ConversationState.COMPLETE:
            status_str = "completed"
        elif session.state in [ConversationState.ANALYSIS_IN_PROGRESS, ConversationState.REPORT_GENERATION]:
            status_str = "in_progress"
        else:
            status_str = "in_progress"
        
        return AnalysisStatusResponse(
            session_id=session.session_id,
            status=status_str,
            progress_percentage=progress,
            current_step=current_step,
            result=session.analysis_result if session.analysis_result else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )
