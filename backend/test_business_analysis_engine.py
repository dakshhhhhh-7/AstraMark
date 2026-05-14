"""
Unit tests for BusinessAnalysisEngine
Tests conversation flow, state management, and data extraction
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from motor.motor_asyncio import AsyncIOMotorDatabase

from business_analysis_service import (
    BusinessAnalysisEngine, AnalysisSession, ChatResponse,
    BusinessIdea, Budget, ConversationState, Message
)
from groq_service import GroqService


@pytest.fixture
def mock_db():
    """Mock MongoDB database"""
    db = Mock(spec=AsyncIOMotorDatabase)
    db.analysis_sessions = Mock()
    db.analysis_sessions.find_one = AsyncMock(return_value=None)
    db.analysis_sessions.update_one = AsyncMock()
    db.analysis_sessions.find = Mock()
    db.analysis_sessions.delete_one = AsyncMock()
    return db


@pytest.fixture
def mock_groq_service():
    """Mock Groq AI service"""
    service = Mock(spec=GroqService)
    service.is_available = Mock(return_value=True)
    service.generate_analysis = AsyncMock()
    return service


@pytest.fixture
def engine(mock_db, mock_groq_service):
    """Create BusinessAnalysisEngine instance"""
    return BusinessAnalysisEngine(mock_db, mock_groq_service)


@pytest.mark.asyncio
async def test_start_session(engine, mock_db):
    """Test starting a new analysis session"""
    user_id = "test_user_123"
    
    session = await engine.start_session(user_id)
    
    assert session.user_id == user_id
    assert session.state == ConversationState.GREETING
    assert len(session.conversation_history) == 1
    assert session.conversation_history[0].role == "assistant"
    assert "AI Business Analysis Assistant" in session.conversation_history[0].content
    
    # Verify session was saved
    mock_db.analysis_sessions.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_extract_business_idea_success(engine, mock_groq_service):
    """Test successful business idea extraction"""
    mock_groq_service.generate_analysis.return_value = {
        "description": "Online food delivery platform",
        "industry": "Food & Beverage",
        "target_market": "Urban millennials",
        "product_service_type": "Mobile app",
        "geographic_location": "Mumbai, India",
        "key_features": ["Real-time tracking", "Multiple cuisines"],
        "unique_value_proposition": "15-minute delivery guarantee"
    }
    
    messages = [
        Message(role="user", content="I want to start a food delivery app in Mumbai")
    ]
    
    business_idea = await engine.extract_business_idea(messages)
    
    assert business_idea is not None
    assert business_idea.industry == "Food & Beverage"
    assert business_idea.target_market == "Urban millennials"
    assert business_idea.geographic_location == "Mumbai, India"


@pytest.mark.asyncio
async def test_extract_budget_success(engine):
    """Test successful budget extraction"""
    messages = [
        Message(role="user", content="My budget is $50,000 USD")
    ]
    
    budget = await engine.extract_budget(messages)
    
    assert budget is not None
    assert budget.amount == 50000
    assert budget.currency == "USD"


@pytest.mark.asyncio
async def test_extract_budget_indian_format(engine):
    """Test budget extraction with Indian number format"""
    messages = [
        Message(role="user", content="I have ₹25,00,000 INR available")
    ]
    
    budget = await engine.extract_budget(messages)
    
    assert budget is not None
    assert budget.amount == 2500000
    assert budget.currency == "INR"


@pytest.mark.asyncio
async def test_process_message_business_idea_collection(engine, mock_db, mock_groq_service):
    """Test processing message in business idea collection state"""
    # Setup session
    session = AnalysisSession(
        user_id="test_user",
        state=ConversationState.BUSINESS_IDEA_COLLECTION
    )
    
    # Mock load_session to return our test session
    engine.load_session = AsyncMock(return_value=session)
    engine.save_session = AsyncMock()
    
    # Mock business idea extraction
    mock_groq_service.generate_analysis.return_value = {
        "description": "SaaS platform",
        "industry": "Technology",
        "target_market": "Small businesses",
        "product_service_type": "Web application",
        "geographic_location": "United States"
    }
    
    response = await engine.process_message(
        session.session_id,
        "I want to build a SaaS platform for small businesses in the US"
    )
    
    assert response.state == ConversationState.BUSINESS_IDEA_CONFIRMATION
    assert "confirm" in response.message.lower()


@pytest.mark.asyncio
async def test_verify_user_access_authorized(engine, mock_db):
    """Test user access verification - authorized"""
    mock_db.analysis_sessions.find_one.return_value = {
        "session_id": "session_123",
        "user_id": "user_123"
    }
    
    has_access = await engine.verify_user_access("session_123", "user_123")
    
    assert has_access is True


@pytest.mark.asyncio
async def test_verify_user_access_unauthorized(engine, mock_db):
    """Test user access verification - unauthorized"""
    mock_db.analysis_sessions.find_one.return_value = None
    
    has_access = await engine.verify_user_access("session_123", "wrong_user")
    
    assert has_access is False


@pytest.mark.asyncio
async def test_encryption_decryption(engine):
    """Test data encryption and decryption"""
    original_data = "Sensitive business idea description"
    
    encrypted = engine._encrypt_data(original_data)
    assert encrypted != original_data
    
    decrypted = engine._decrypt_data(encrypted)
    assert decrypted == original_data


@pytest.mark.asyncio
async def test_session_expiration(engine, mock_db):
    """Test expired session handling"""
    expired_session = {
        "session_id": "expired_123",
        "user_id": "user_123",
        "state": "GREETING",
        "conversation_history": [],
        "created_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        "updated_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        "expires_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        "last_auto_save": datetime.now(timezone.utc).isoformat()
    }
    
    mock_db.analysis_sessions.find_one.return_value = expired_session
    
    session = await engine.load_session("expired_123")
    
    assert session is None


@pytest.mark.asyncio
async def test_auto_save_functionality(engine, mock_db):
    """Test auto-save after interval"""
    session = AnalysisSession(user_id="test_user")
    session.last_auto_save = datetime.now(timezone.utc) - timedelta(seconds=35)
    
    engine.save_session = AsyncMock()
    
    await engine._auto_save_if_needed(session)
    
    engine.save_session.assert_called_once()


@pytest.mark.asyncio
async def test_delete_session(engine, mock_db):
    """Test session deletion"""
    mock_db.analysis_sessions.delete_one.return_value = Mock(deleted_count=1)
    
    deleted = await engine.delete_session("session_123", "user_123")
    
    assert deleted is True
    mock_db.analysis_sessions.delete_one.assert_called_once_with({
        "session_id": "session_123",
        "user_id": "user_123"
    })


@pytest.mark.asyncio
async def test_resume_session(engine, mock_db):
    """Test resuming an interrupted session"""
    session_data = {
        "session_id": "session_123",
        "user_id": "user_123",
        "state": "BUDGET_COLLECTION",
        "conversation_history": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "last_auto_save": datetime.now(timezone.utc).isoformat()
    }
    
    mock_db.analysis_sessions.find_one.return_value = session_data
    engine.save_session = AsyncMock()
    
    resumed_session = await engine.resume_session("session_123")
    
    assert resumed_session is not None
    assert resumed_session.expires_at > datetime.now(timezone.utc) + timedelta(hours=23)
    engine.save_session.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
