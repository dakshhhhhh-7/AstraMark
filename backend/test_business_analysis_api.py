"""
Integration tests for Business Analysis API endpoints
Tests complete API workflows and authentication
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from server_enhanced import app
from business_analysis_service import AnalysisSession, ConversationState


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token"""
    return "Bearer test_token_123"


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return Mock(id="test_user_123", email="test@example.com")


@pytest.mark.asyncio
async def test_start_session_endpoint(client, mock_auth_token, mock_user):
    """Test POST /api/ai/business-analysis/start"""
    with patch('business_analysis_router.get_current_user', return_value=mock_user):
        with patch('business_analysis_router.get_business_analysis_engine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine_instance.start_session = AsyncMock(return_value=AnalysisSession(
                user_id=mock_user.id,
                state=ConversationState.GREETING
            ))
            mock_engine.return_value = mock_engine_instance
            
            response = client.post(
                "/api/ai/business-analysis/start",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data
            assert "message" in data
            assert data["state"] == "GREETING"


@pytest.mark.asyncio
async def test_start_session_unauthorized(client):
    """Test start session without authentication"""
    response = client.post("/api/ai/business-analysis/start")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_endpoint(client, mock_auth_token, mock_user):
    """Test POST /api/ai/business-analysis/chat"""
    with patch('business_analysis_router.get_current_user', return_value=mock_user):
        with patch('business_analysis_router.get_business_analysis_engine') as mock_engine:
            mock_engine_instance = Mock()
            
            # Mock session verification
            mock_session = AnalysisSession(
                session_id="session_123",
                user_id=mock_user.id,
                state=ConversationState.BUSINESS_IDEA_COLLECTION
            )
            mock_engine_instance.load_session = AsyncMock(return_value=mock_session)
            
            # Mock message processing
            from business_analysis_service import ChatResponse
            mock_engine_instance.process_message = AsyncMock(return_value=ChatResponse(
                message="Thank you for sharing!",
                state=ConversationState.BUSINESS_IDEA_COLLECTION,
                session_id="session_123"
            ))
            
            mock_engine.return_value = mock_engine_instance
            
            response = client.post(
                "/api/ai/business-analysis/chat",
                headers={"Authorization": mock_auth_token},
                json={
                    "session_id": "session_123",
                    "message": "I want to start a food delivery business"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "session_123"
            assert "message" in data


@pytest.mark.asyncio
async def test_chat_access_denied(client, mock_auth_token, mock_user):
    """Test chat with unauthorized session access"""
    with patch('business_analysis_router.get_current_user', return_value=mock_user):
        with patch('business_analysis_router.get_business_analysis_engine') as mock_engine:
            mock_engine_instance = Mock()
            
            # Mock session belonging to different user
            mock_session = AnalysisSession(
                session_id="session_123",
                user_id="different_user",
                state=ConversationState.BUSINESS_IDEA_COLLECTION
            )
            mock_engine_instance.load_session = AsyncMock(return_value=mock_session)
            mock_engine.return_value = mock_engine_instance
            
            response = client.post(
                "/api/ai/business-analysis/chat",
                headers={"Authorization": mock_auth_token},
                json={
                    "session_id": "session_123",
                    "message": "Test message"
                }
            )
            
            assert response.status_code == 403


@pytest.mark.asyncio
async def test_generate_report_endpoint(client, mock_auth_token, mock_user):
    """Test POST /api/ai/business-analysis/generate-report"""
    with patch('business_analysis_router.get_current_user', return_value=mock_user):
        with patch('business_analysis_router.get_business_analysis_engine') as mock_engine:
            with patch('business_analysis_router.get_market_research_service'):
                with patch('business_analysis_router.get_budget_analyzer'):
                    with patch('business_analysis_router.get_financial_projector'):
                        with patch('business_analysis_router.get_risk_assessment'):
                            with patch('business_analysis_router.get_growth_strategy'):
                                with patch('business_analysis_router.get_report_generator') as mock_report_gen:
                                    # Mock complete session
                                    from business_analysis_service import BusinessIdea, Budget
                                    mock_session = AnalysisSession(
                                        session_id="session_123",
                                        user_id=mock_user.id,
                                        state=ConversationState.ANALYSIS_COMPLETE,
                                        business_idea=BusinessIdea(
                                            description="Test",
                                            industry="Tech",
                                            target_market="SMBs",
                                            product_service_type="SaaS",
                                            geographic_location="US"
                                        ),
                                        budget=Budget(amount=50000, currency="USD")
                                    )
                                    
                                    mock_engine_instance = Mock()
                                    mock_engine_instance.load_session = AsyncMock(return_value=mock_session)
                                    mock_engine_instance.save_session = AsyncMock()
                                    mock_engine_instance.db = Mock()
                                    mock_engine_instance.db.business_analysis_reports = Mock()
                                    mock_engine_instance.db.business_analysis_reports.insert_one = AsyncMock()
                                    mock_engine.return_value = mock_engine_instance
                                    
                                    # Mock report generation
                                    from report_generator import Report
                                    import io
                                    mock_report = Report(
                                        report_id="report_123",
                                        session_id="session_123",
                                        user_id=mock_user.id,
                                        format="pdf",
                                        file_size=1024,
                                        generation_timestamp=datetime.now(timezone.utc)
                                    )
                                    mock_report_gen_instance = Mock()
                                    mock_report_gen_instance.generate_report = AsyncMock(
                                        return_value=(mock_report, io.BytesIO(b"test"))
                                    )
                                    mock_report_gen.return_value = mock_report_gen_instance
                                    
                                    response = client.post(
                                        "/api/ai/business-analysis/generate-report",
                                        headers={"Authorization": mock_auth_token},
                                        json={
                                            "session_id": "session_123",
                                            "format": "pdf"
                                        }
                                    )
                                    
                                    assert response.status_code == 200
                                    data = response.json()
                                    assert "report_id" in data
                                    assert data["format"] == "pdf"


@pytest.mark.asyncio
async def test_list_sessions_endpoint(client, mock_auth_token, mock_user):
    """Test GET /api/ai/business-analysis/sessions"""
    with patch('business_analysis_router.get_current_user', return_value=mock_user):
        with patch('business_analysis_router.get_business_analysis_engine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine_instance.get_user_sessions = AsyncMock(return_value=[
                {
                    "session_id": "session_1",
                    "state": "COMPLETE",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "business_idea_summary": "Food delivery",
                    "budget_summary": "USD 50,000"
                }
            ])
            mock_engine.return_value = mock_engine_instance
            
            response = client.get(
                "/api/ai/business-analysis/sessions",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "sessions" in data
            assert len(data["sessions"]) == 1


@pytest.mark.asyncio
async def test_delete_session_endpoint(client, mock_auth_token, mock_user):
    """Test DELETE /api/ai/business-analysis/sessions/{session_id}"""
    with patch('business_analysis_router.get_current_user', return_value=mock_user):
        with patch('business_analysis_router.get_business_analysis_engine') as mock_engine:
            mock_engine_instance = Mock()
            mock_engine_instance.delete_session = AsyncMock(return_value=True)
            mock_engine.return_value = mock_engine_instance
            
            response = client.delete(
                "/api/ai/business-analysis/sessions/session_123",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


@pytest.mark.asyncio
async def test_resume_session_endpoint(client, mock_auth_token, mock_user):
    """Test PUT /api/ai/business-analysis/sessions/{session_id}/resume"""
    with patch('business_analysis_router.get_current_user', return_value=mock_user):
        with patch('business_analysis_router.get_business_analysis_engine') as mock_engine:
            mock_session = AnalysisSession(
                session_id="session_123",
                user_id=mock_user.id,
                state=ConversationState.BUDGET_COLLECTION
            )
            
            mock_engine_instance = Mock()
            mock_engine_instance.load_session = AsyncMock(return_value=mock_session)
            mock_engine_instance.resume_session = AsyncMock(return_value=mock_session)
            mock_engine.return_value = mock_engine_instance
            
            response = client.put(
                "/api/ai/business-analysis/sessions/session_123/resume",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "session_123"
            assert "conversation_history" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
