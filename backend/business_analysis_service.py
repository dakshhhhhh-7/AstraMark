"""
Business Analysis Service - Core orchestration engine for AI-powered business analysis
Manages conversation state, extracts business information, and coordinates analysis components
"""
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os

from groq_service import GroqService

logger = logging.getLogger(__name__)


class ConversationState(str, Enum):
    """Conversation state machine states"""
    GREETING = "GREETING"
    BUSINESS_IDEA_COLLECTION = "BUSINESS_IDEA_COLLECTION"
    BUSINESS_IDEA_CONFIRMATION = "BUSINESS_IDEA_CONFIRMATION"
    BUDGET_COLLECTION = "BUDGET_COLLECTION"
    BUDGET_CONFIRMATION = "BUDGET_CONFIRMATION"
    ANALYSIS_IN_PROGRESS = "ANALYSIS_IN_PROGRESS"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    REPORT_GENERATION = "REPORT_GENERATION"
    COMPLETE = "COMPLETE"


class Message(BaseModel):
    """Chat message model"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BusinessIdea(BaseModel):
    """Structured business idea extracted from conversation"""
    description: str
    industry: str
    target_market: str
    product_service_type: str
    geographic_location: str
    key_features: List[str] = []
    unique_value_proposition: Optional[str] = None


class Budget(BaseModel):
    """Budget information extracted from conversation"""
    amount: float
    currency: str  # INR, USD, EUR
    confidence: float = 1.0  # 0.0 to 1.0


class AnalysisSession(BaseModel):
    """Analysis session model"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    state: ConversationState = ConversationState.GREETING
    conversation_history: List[Message] = []
    business_idea: Optional[BusinessIdea] = None
    budget: Optional[Budget] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))
    last_auto_save: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_result: Optional[Dict[str, Any]] = None
    report_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response to user message"""
    message: str
    state: ConversationState
    session_id: str
    requires_input: bool = True
    metadata: Optional[Dict[str, Any]] = None


class BusinessAnalysisEngine:
    """
    Core orchestration engine for business analysis feature.
    Manages conversation flow, extracts business information, and coordinates analysis.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, groq_service: GroqService):
        """
        Initialize the business analysis engine
        
        Args:
            db: MongoDB database instance
            groq_service: Groq AI service for natural language processing
        """
        self.db = db
        self.groq_service = groq_service
        self.sessions_collection = db.analysis_sessions
        
        # Auto-save interval in seconds
        self.auto_save_interval = 30
        
        # Initialize AES-256 encryption for sensitive data
        self._init_encryption()
        
        logger.info("BusinessAnalysisEngine initialized")
    
    def _init_encryption(self):
        """Initialize AES-256 encryption for business idea descriptions"""
        # Get encryption key from environment or generate one
        encryption_key = os.getenv('BUSINESS_ANALYSIS_ENCRYPTION_KEY')
        
        if not encryption_key:
            # Generate a key from a password (in production, use a secure key management system)
            password = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production').encode()
            salt = b'astramark_business_analysis_salt'  # In production, use a random salt stored securely
            
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self.cipher = Fernet(key)
        else:
            self.cipher = Fernet(encryption_key.encode())
        
        logger.info("Encryption initialized for sensitive data")
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data using AES-256"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data  # Fallback to unencrypted if encryption fails
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Fallback to returning as-is if decryption fails
    
    async def verify_user_access(self, session_id: str, user_id: str) -> bool:
        """
        Verify that the user has access to the session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            True if user has access, False otherwise
        """
        session_doc = await self.sessions_collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        return session_doc is not None
    
    async def start_session(self, user_id: str) -> AnalysisSession:
        """
        Start a new business analysis session
        
        Args:
            user_id: User identifier
            
        Returns:
            New AnalysisSession instance
        """
        session = AnalysisSession(user_id=user_id)
        
        # Add greeting message
        greeting_message = Message(
            role="assistant",
            content=(
                "Hello! I'm your AI Business Analysis Assistant. I'll help you evaluate "
                "your business idea with comprehensive market research, financial projections, "
                "and actionable strategies.\n\n"
                "To get started, please tell me about your business idea. What product or "
                "service are you planning to offer, and who is your target market?"
            )
        )
        session.conversation_history.append(greeting_message)
        
        # Save initial session
        await self.save_session(session)
        
        logger.info(f"Started new session {session.session_id} for user {user_id}")
        return session
    
    async def process_message(self, session_id: str, message: str) -> ChatResponse:
        """
        Process user message and return AI response
        
        Args:
            session_id: Session identifier
            message: User message content
            
        Returns:
            ChatResponse with AI reply and updated state
        """
        # Load session
        session = await self.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Add user message to history
        user_message = Message(role="user", content=message)
        session.conversation_history.append(user_message)
        
        # Process based on current state
        response = await self._process_state(session, message)
        
        # Add assistant response to history
        assistant_message = Message(role="assistant", content=response.message)
        session.conversation_history.append(assistant_message)
        
        # Update session state
        session.state = response.state
        session.updated_at = datetime.now(timezone.utc)
        
        # Auto-save if needed
        await self._auto_save_if_needed(session)
        
        logger.info(f"Processed message for session {session_id}, new state: {response.state}")
        return response
    
    async def _process_state(self, session: AnalysisSession, message: str) -> ChatResponse:
        """
        Process message based on current conversation state
        
        Args:
            session: Current session
            message: User message
            
        Returns:
            ChatResponse with appropriate reply
        """
        if session.state == ConversationState.GREETING:
            return await self._handle_greeting_state(session, message)
        
        elif session.state == ConversationState.BUSINESS_IDEA_COLLECTION:
            return await self._handle_business_idea_collection(session, message)
        
        elif session.state == ConversationState.BUSINESS_IDEA_CONFIRMATION:
            return await self._handle_business_idea_confirmation(session, message)
        
        elif session.state == ConversationState.BUDGET_COLLECTION:
            return await self._handle_budget_collection(session, message)
        
        elif session.state == ConversationState.BUDGET_CONFIRMATION:
            return await self._handle_budget_confirmation(session, message)
        
        else:
            # Default fallback
            return ChatResponse(
                message="I'm not sure how to help with that. Let's continue with the analysis.",
                state=session.state,
                session_id=session.session_id
            )
    
    async def _handle_greeting_state(self, session: AnalysisSession, message: str) -> ChatResponse:
        """Handle initial greeting and transition to business idea collection"""
        # User has provided their first message, move to business idea collection
        return await self._handle_business_idea_collection(session, message)
    
    async def _handle_business_idea_collection(self, session: AnalysisSession, message: str) -> ChatResponse:
        """
        Collect business idea information from user
        
        Args:
            session: Current session
            message: User message
            
        Returns:
            ChatResponse with follow-up questions or confirmation
        """
        # Try to extract business idea
        business_idea = await self.extract_business_idea(session.conversation_history)
        
        if business_idea:
            # We have enough information, confirm with user
            session.business_idea = business_idea
            await self.save_session(session)
            
            confirmation_message = (
                f"Great! Let me confirm I understand your business idea:\n\n"
                f"**Industry:** {business_idea.industry}\n"
                f"**Product/Service:** {business_idea.product_service_type}\n"
                f"**Target Market:** {business_idea.target_market}\n"
                f"**Location:** {business_idea.geographic_location}\n\n"
                f"Is this correct? (Yes/No)"
            )
            
            return ChatResponse(
                message=confirmation_message,
                state=ConversationState.BUSINESS_IDEA_CONFIRMATION,
                session_id=session.session_id,
                metadata={"business_idea": business_idea.dict()}
            )
        else:
            # Need more information
            clarifying_message = (
                "Thank you for sharing! To provide you with the most accurate analysis, "
                "I need a bit more information:\n\n"
                "- What industry is this business in?\n"
                "- Who is your target customer?\n"
                "- Where will you operate (city, country, or region)?\n\n"
                "Please provide any additional details about your business idea."
            )
            
            return ChatResponse(
                message=clarifying_message,
                state=ConversationState.BUSINESS_IDEA_COLLECTION,
                session_id=session.session_id
            )
    
    async def _handle_business_idea_confirmation(self, session: AnalysisSession, message: str) -> ChatResponse:
        """
        Handle user confirmation of business idea
        
        Args:
            session: Current session
            message: User message (yes/no)
            
        Returns:
            ChatResponse moving to budget collection or back to idea collection
        """
        message_lower = message.lower().strip()
        
        if any(word in message_lower for word in ["yes", "correct", "right", "accurate", "good"]):
            # Confirmed, move to budget collection
            budget_message = (
                "Perfect! Now, let's talk about your budget.\n\n"
                "What is your available investment budget for this business? "
                "Please specify the amount and currency (INR, USD, or EUR).\n\n"
                "For example: '50,000 USD' or '₹25,00,000 INR'"
            )
            
            return ChatResponse(
                message=budget_message,
                state=ConversationState.BUDGET_COLLECTION,
                session_id=session.session_id
            )
        
        elif any(word in message_lower for word in ["no", "incorrect", "wrong", "not quite"]):
            # Not confirmed, go back to collection
            session.business_idea = None
            await self.save_session(session)
            
            retry_message = (
                "No problem! Let's clarify your business idea. "
                "Please describe your business in more detail, including:\n\n"
                "- What product or service you'll offer\n"
                "- Who your target customers are\n"
                "- Where you plan to operate\n"
                "- What makes your business unique"
            )
            
            return ChatResponse(
                message=retry_message,
                state=ConversationState.BUSINESS_IDEA_COLLECTION,
                session_id=session.session_id
            )
        
        else:
            # Unclear response, ask again
            return ChatResponse(
                message="I didn't quite catch that. Is the business idea summary correct? Please answer Yes or No.",
                state=ConversationState.BUSINESS_IDEA_CONFIRMATION,
                session_id=session.session_id
            )
    
    async def _handle_budget_collection(self, session: AnalysisSession, message: str) -> ChatResponse:
        """
        Collect budget information from user
        
        Args:
            session: Current session
            message: User message with budget
            
        Returns:
            ChatResponse with budget confirmation or clarification request
        """
        # Try to extract budget
        budget = await self.extract_budget(session.conversation_history)
        
        if budget and budget.amount >= 10000:  # Minimum threshold (in base currency)
            # Valid budget extracted
            session.budget = budget
            await self.save_session(session)
            
            # Format budget for display
            currency_symbols = {"INR": "₹", "USD": "$", "EUR": "€"}
            symbol = currency_symbols.get(budget.currency, budget.currency)
            formatted_amount = f"{symbol}{budget.amount:,.2f}"
            
            confirmation_message = (
                f"Thank you! I've noted your budget as **{formatted_amount} {budget.currency}**.\n\n"
                f"Is this correct? (Yes/No)"
            )
            
            return ChatResponse(
                message=confirmation_message,
                state=ConversationState.BUDGET_CONFIRMATION,
                session_id=session.session_id,
                metadata={"budget": budget.dict()}
            )
        
        elif budget and budget.amount < 10000:
            # Budget too low
            clarifying_message = (
                "The budget you specified seems quite low for a comprehensive business analysis. "
                "Our minimum recommended budget is ₹10,000 INR (or equivalent).\n\n"
                "Could you please confirm your investment budget? If you'd like to proceed "
                "with a smaller amount, please let me know."
            )
            
            return ChatResponse(
                message=clarifying_message,
                state=ConversationState.BUDGET_COLLECTION,
                session_id=session.session_id
            )
        
        else:
            # Could not extract budget
            clarifying_message = (
                "I couldn't quite understand the budget amount. Please specify your "
                "investment budget with the currency.\n\n"
                "Examples:\n"
                "- '50,000 USD'\n"
                "- '₹25,00,000 INR'\n"
                "- '€30,000 EUR'"
            )
            
            return ChatResponse(
                message=clarifying_message,
                state=ConversationState.BUDGET_COLLECTION,
                session_id=session.session_id
            )
    
    async def _handle_budget_confirmation(self, session: AnalysisSession, message: str) -> ChatResponse:
        """
        Handle user confirmation of budget
        
        Args:
            session: Current session
            message: User message (yes/no)
            
        Returns:
            ChatResponse moving to analysis or back to budget collection
        """
        message_lower = message.lower().strip()
        
        if any(word in message_lower for word in ["yes", "correct", "right", "accurate", "good"]):
            # Confirmed, start analysis
            session.state = ConversationState.ANALYSIS_IN_PROGRESS
            await self.save_session(session)
            
            analysis_message = (
                "Excellent! I have everything I need to begin your comprehensive business analysis.\n\n"
                "I'll now analyze:\n"
                "✓ Market research and competitor analysis\n"
                "✓ Budget breakdown and allocation\n"
                "✓ Financial projections and ROI\n"
                "✓ Risk assessment and mitigation strategies\n"
                "✓ Growth strategy and action plan\n\n"
                "This will take a few moments. Please wait while I gather and analyze the data..."
            )
            
            return ChatResponse(
                message=analysis_message,
                state=ConversationState.ANALYSIS_IN_PROGRESS,
                session_id=session.session_id,
                requires_input=False,
                metadata={"start_analysis": True}
            )
        
        elif any(word in message_lower for word in ["no", "incorrect", "wrong"]):
            # Not confirmed, go back to collection
            session.budget = None
            await self.save_session(session)
            
            retry_message = (
                "No problem! Please specify your investment budget again, "
                "including the amount and currency (INR, USD, or EUR)."
            )
            
            return ChatResponse(
                message=retry_message,
                state=ConversationState.BUDGET_COLLECTION,
                session_id=session.session_id
            )
        
        else:
            # Unclear response, ask again
            return ChatResponse(
                message="I didn't quite catch that. Is the budget amount correct? Please answer Yes or No.",
                state=ConversationState.BUDGET_CONFIRMATION,
                session_id=session.session_id
            )
    
    async def extract_business_idea(self, conversation_history: List[Message]) -> Optional[BusinessIdea]:
        """
        Extract structured business idea from conversation history using AI
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            BusinessIdea if enough information is available, None otherwise
        """
        if not self.groq_service.is_available():
            logger.warning("Groq service not available for business idea extraction")
            return None
        
        # Build conversation context
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content}" 
            for msg in conversation_history[-10:]  # Last 10 messages
        ])
        
        system_prompt = """You are an expert business analyst. Extract structured business information from the conversation.
Return a JSON object with these fields:
- description: Brief description of the business (string)
- industry: Industry category (string)
- target_market: Target customer segment (string)
- product_service_type: Type of product or service (string)
- geographic_location: Operating location (string)
- key_features: List of key features or offerings (array of strings)
- unique_value_proposition: What makes it unique (string, optional)

If information is missing or unclear, return null. Only return a complete object if you have enough information."""
        
        user_prompt = f"""Extract business idea information from this conversation:

{conversation_text}

Return JSON with the business idea structure, or null if insufficient information."""
        
        try:
            result = await self.groq_service.generate_analysis(system_prompt, user_prompt)
            
            if result and isinstance(result, dict) and "description" in result:
                business_idea = BusinessIdea(**result)
                logger.info("Successfully extracted business idea")
                return business_idea
            else:
                logger.info("Insufficient information to extract business idea")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting business idea: {e}")
            return None
    
    async def extract_budget(self, conversation_history: List[Message]) -> Optional[Budget]:
        """
        Extract budget amount and currency from conversation history
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            Budget if found, None otherwise
        """
        # Get the last few messages
        recent_messages = conversation_history[-5:]
        
        # Look for budget patterns in recent messages
        import re
        
        for msg in reversed(recent_messages):
            if msg.role != "user":
                continue
            
            content = msg.content.lower()
            
            # Currency patterns
            currency = None
            if any(word in content for word in ["inr", "₹", "rupee", "rupees"]):
                currency = "INR"
            elif any(word in content for word in ["usd", "$", "dollar", "dollars"]):
                currency = "USD"
            elif any(word in content for word in ["eur", "€", "euro", "euros"]):
                currency = "EUR"
            
            # Amount patterns
            # Match patterns like: 50000, 50,000, 50.000, 5,00,000 (Indian format)
            amount_patterns = [
                r'(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)',  # Indian format: 5,00,000
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',    # Western format: 50,000
                r'(\d+(?:\.\d{2})?)',                    # Simple: 50000
            ]
            
            amount = None
            for pattern in amount_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    # Take the largest number found
                    for match in matches:
                        try:
                            # Remove commas and convert
                            num_str = match.replace(',', '')
                            num = float(num_str)
                            if amount is None or num > amount:
                                amount = num
                        except ValueError:
                            continue
            
            if amount and currency:
                logger.info(f"Extracted budget: {amount} {currency}")
                return Budget(amount=amount, currency=currency)
        
        logger.info("Could not extract budget from conversation")
        return None
    
    async def save_session(self, session: AnalysisSession) -> None:
        """
        Save session state to MongoDB with encryption for sensitive data
        
        Args:
            session: Session to save
        """
        session.updated_at = datetime.now(timezone.utc)
        session.last_auto_save = datetime.now(timezone.utc)
        
        session_dict = session.dict()
        
        # Encrypt business idea description if present
        if session_dict.get('business_idea') and session_dict['business_idea'].get('description'):
            session_dict['business_idea']['description'] = self._encrypt_data(
                session_dict['business_idea']['description']
            )
            session_dict['business_idea']['_encrypted'] = True
        
        # Convert datetime objects to ISO format for MongoDB
        for key in ['created_at', 'updated_at', 'expires_at', 'last_auto_save']:
            if key in session_dict and session_dict[key]:
                session_dict[key] = session_dict[key].isoformat()
        
        # Convert conversation history
        if 'conversation_history' in session_dict:
            for msg in session_dict['conversation_history']:
                if 'timestamp' in msg and msg['timestamp']:
                    msg['timestamp'] = msg['timestamp'].isoformat() if isinstance(msg['timestamp'], datetime) else msg['timestamp']
        
        await self.sessions_collection.update_one(
            {"session_id": session.session_id},
            {"$set": session_dict},
            upsert=True
        )
        
        logger.debug(f"Saved session {session.session_id}")
    
    async def load_session(self, session_id: str) -> Optional[AnalysisSession]:
        """
        Load session from MongoDB and decrypt sensitive data
        
        Args:
            session_id: Session identifier
            
        Returns:
            AnalysisSession if found, None otherwise
        """
        session_dict = await self.sessions_collection.find_one({"session_id": session_id})
        
        if not session_dict:
            logger.warning(f"Session {session_id} not found")
            return None
        
        # Remove MongoDB _id field
        session_dict.pop('_id', None)
        
        # Decrypt business idea description if encrypted
        if session_dict.get('business_idea') and session_dict['business_idea'].get('_encrypted'):
            session_dict['business_idea']['description'] = self._decrypt_data(
                session_dict['business_idea']['description']
            )
            session_dict['business_idea'].pop('_encrypted', None)
        
        # Convert ISO strings back to datetime
        for key in ['created_at', 'updated_at', 'expires_at', 'last_auto_save']:
            if key in session_dict and isinstance(session_dict[key], str):
                session_dict[key] = datetime.fromisoformat(session_dict[key])
        
        # Convert conversation history timestamps
        if 'conversation_history' in session_dict:
            for msg in session_dict['conversation_history']:
                if 'timestamp' in msg and isinstance(msg['timestamp'], str):
                    msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
        
        session = AnalysisSession(**session_dict)
        
        # Check if session has expired
        if session.expires_at < datetime.now(timezone.utc):
            logger.warning(f"Session {session_id} has expired")
            return None
        
        logger.debug(f"Loaded session {session_id}")
        return session
    
    async def resume_session(self, session_id: str) -> AnalysisSession:
        """
        Resume an interrupted session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Resumed AnalysisSession
            
        Raises:
            ValueError: If session not found or expired
        """
        session = await self.load_session(session_id)
        
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")
        
        # Extend expiration by 24 hours
        session.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        await self.save_session(session)
        
        logger.info(f"Resumed session {session_id}")
        return session
    
    async def _auto_save_if_needed(self, session: AnalysisSession) -> None:
        """
        Auto-save session if enough time has passed since last save
        
        Args:
            session: Session to potentially save
        """
        time_since_save = (datetime.now(timezone.utc) - session.last_auto_save).total_seconds()
        
        if time_since_save >= self.auto_save_interval:
            await self.save_session(session)
            logger.debug(f"Auto-saved session {session.session_id}")
    
    async def get_user_sessions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get list of user's analysis sessions
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        cursor = self.sessions_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        sessions = []
        async for session_dict in cursor:
            session_dict.pop('_id', None)
            
            # Create summary
            summary = {
                "session_id": session_dict.get("session_id"),
                "state": session_dict.get("state"),
                "created_at": session_dict.get("created_at"),
                "business_idea_summary": None,
                "budget_summary": None
            }
            
            if session_dict.get("business_idea"):
                idea = session_dict["business_idea"]
                summary["business_idea_summary"] = f"{idea.get('product_service_type', 'Business')} in {idea.get('industry', 'Unknown')}"
            
            if session_dict.get("budget"):
                budget = session_dict["budget"]
                summary["budget_summary"] = f"{budget.get('currency', '')} {budget.get('amount', 0):,.0f}"
            
            sessions.append(summary)
        
        return sessions
    
    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
            user_id: User identifier (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.sessions_collection.delete_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            logger.info(f"Deleted session {session_id}")
            return True
        else:
            logger.warning(f"Session {session_id} not found for deletion")
            return False
