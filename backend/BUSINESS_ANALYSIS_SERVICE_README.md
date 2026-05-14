# Business Analysis Service - Implementation Documentation

## Overview

The `business_analysis_service.py` module implements the core orchestration engine for AstraMark's AI-powered business analysis feature. It manages conversational workflows, extracts business information using AI, and coordinates the analysis process.

## Key Components

### 1. BusinessAnalysisEngine Class

The main orchestration class that manages the entire business analysis workflow.

**Key Features:**
- Conversation state management with state machine
- Session persistence with MongoDB
- Auto-save functionality (every 30 seconds)
- Session expiration handling (24 hours)
- Business idea extraction using Groq AI
- Budget extraction with multi-currency support (INR, USD, EUR)

### 2. Conversation State Machine

The service implements a state machine with the following states:

```
GREETING → BUSINESS_IDEA_COLLECTION → BUSINESS_IDEA_CONFIRMATION →
BUDGET_COLLECTION → BUDGET_CONFIRMATION → ANALYSIS_IN_PROGRESS →
ANALYSIS_COMPLETE → REPORT_GENERATION → COMPLETE
```

**State Descriptions:**
- **GREETING**: Initial welcome message
- **BUSINESS_IDEA_COLLECTION**: Gathering business idea details
- **BUSINESS_IDEA_CONFIRMATION**: User confirms extracted business idea
- **BUDGET_COLLECTION**: Gathering budget information
- **BUDGET_CONFIRMATION**: User confirms budget amount
- **ANALYSIS_IN_PROGRESS**: Running market research and analysis
- **ANALYSIS_COMPLETE**: Analysis finished, ready for report
- **REPORT_GENERATION**: Generating PDF/DOCX report
- **COMPLETE**: Session complete

### 3. Data Models

**AnalysisSession**: Main session model containing:
- `session_id`: Unique identifier
- `user_id`: User identifier
- `state`: Current conversation state
- `conversation_history`: List of messages
- `business_idea`: Extracted business information
- `budget`: Extracted budget information
- `created_at`, `updated_at`, `expires_at`: Timestamps
- `analysis_result`: Analysis data (populated later)
- `report_id`: Generated report ID (populated later)

**BusinessIdea**: Structured business information:
- `description`: Business description
- `industry`: Industry category
- `target_market`: Target customer segment
- `product_service_type`: Product/service type
- `geographic_location`: Operating location
- `key_features`: List of key features
- `unique_value_proposition`: Unique selling point

**Budget**: Budget information:
- `amount`: Budget amount (float)
- `currency`: Currency code (INR, USD, EUR)
- `confidence`: Extraction confidence (0.0-1.0)

**Message**: Chat message:
- `role`: "user" or "assistant"
- `content`: Message text
- `timestamp`: Message timestamp

**ChatResponse**: Response to user message:
- `message`: AI response text
- `state`: New conversation state
- `session_id`: Session identifier
- `requires_input`: Whether user input is needed
- `metadata`: Optional additional data

## Key Methods

### Session Management

**`start_session(user_id: str) -> AnalysisSession`**
- Creates a new analysis session
- Initializes with greeting message
- Saves to MongoDB
- Returns new session object

**`save_session(session: AnalysisSession) -> None`**
- Saves session state to MongoDB
- Updates timestamps
- Handles datetime serialization

**`load_session(session_id: str) -> Optional[AnalysisSession]`**
- Loads session from MongoDB
- Checks expiration
- Returns None if expired or not found

**`resume_session(session_id: str) -> AnalysisSession`**
- Resumes interrupted session
- Extends expiration by 24 hours
- Raises ValueError if not found

**`delete_session(session_id: str, user_id: str) -> bool`**
- Deletes session from database
- Requires user_id for authorization
- Returns True if deleted

**`get_user_sessions(user_id: str, limit: int = 10) -> List[Dict]`**
- Retrieves user's session list
- Returns summaries sorted by date
- Includes business idea and budget summaries

### Message Processing

**`process_message(session_id: str, message: str) -> ChatResponse`**
- Main message processing method
- Routes to appropriate state handler
- Updates conversation history
- Triggers auto-save if needed
- Returns AI response

### Information Extraction

**`extract_business_idea(conversation_history: List[Message]) -> Optional[BusinessIdea]`**
- Uses Groq AI to extract structured business information
- Analyzes last 10 messages
- Returns BusinessIdea object or None
- Handles extraction errors gracefully

**`extract_budget(conversation_history: List[Message]) -> Optional[Budget]`**
- Extracts budget amount and currency using regex
- Supports multiple number formats:
  - Indian: 5,00,000
  - Western: 50,000
  - Simple: 50000
- Detects currency from keywords (₹, $, €, INR, USD, EUR)
- Returns Budget object or None

### State Handlers

**`_handle_greeting_state(session, message) -> ChatResponse`**
- Transitions from greeting to business idea collection

**`_handle_business_idea_collection(session, message) -> ChatResponse`**
- Collects business idea information
- Asks clarifying questions if needed
- Moves to confirmation when complete

**`_handle_business_idea_confirmation(session, message) -> ChatResponse`**
- Confirms business idea with user
- Moves to budget collection on "yes"
- Returns to collection on "no"

**`_handle_budget_collection(session, message) -> ChatResponse`**
- Collects budget information
- Validates minimum threshold (10,000 base currency)
- Moves to confirmation when valid

**`_handle_budget_confirmation(session, message) -> ChatResponse`**
- Confirms budget with user
- Starts analysis on "yes"
- Returns to collection on "no"

## Usage Example

```python
from motor.motor_asyncio import AsyncIOMotorClient
from groq_service import GroqService
from business_analysis_service import BusinessAnalysisEngine

# Initialize dependencies
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.astramark_dev
groq_service = GroqService()

# Create engine
engine = BusinessAnalysisEngine(db=db, groq_service=groq_service)

# Start new session
session = await engine.start_session(user_id="user123")
print(f"Session ID: {session.session_id}")

# Process user messages
response = await engine.process_message(
    session.session_id,
    "I want to start an online clothing store targeting young professionals"
)
print(f"AI: {response.message}")

# Continue conversation
response = await engine.process_message(
    session.session_id,
    "My budget is $50,000 USD"
)
print(f"AI: {response.message}")

# Resume later
resumed_session = await engine.resume_session(session.session_id)
```

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **REQ-1**: Business Idea Input and Processing
  - Natural language input through chatbot
  - Extracts key business attributes
  - Asks clarifying questions
  - Confirms understanding with user

- **REQ-2**: Budget Specification and Validation
  - Accepts INR, USD, EUR
  - Validates minimum threshold
  - Proper currency formatting
  - Real-time validation

- **REQ-10**: Interactive Conversational Experience
  - Maintains conversation context
  - Supports natural language inputs
  - Allows interruption and modification
  - Professional, consultative tone

- **REQ-12**: Analysis Session Management and Recovery
  - Auto-save every 30 seconds
  - 24-hour session preservation
  - Resume capability
  - Session state persistence

## Testing

The implementation includes comprehensive unit tests in `test_business_analysis_service.py`:

- Session creation and management
- Budget extraction (INR, USD, EUR)
- Session expiration handling
- Resume functionality
- Auto-save functionality
- State machine transitions
- User session listing
- Session deletion

Run tests with:
```bash
pytest test_business_analysis_service.py -v
```

## Integration Points

This service integrates with:

1. **MongoDB**: Session persistence and storage
2. **Groq AI Service**: Business idea extraction using LLM
3. **Market Research Service**: (To be integrated in Task 4)
4. **Budget Analyzer**: (To be integrated in Task 5)
5. **Financial Projector**: (To be integrated in Task 6)
6. **Report Generator**: (To be integrated in Task 8)

## Next Steps

The following components need to be implemented to complete the feature:

1. Market Research Service (Task 4)
2. Budget Analyzer (Task 5)
3. Financial Projector (Task 6)
4. Risk Assessment & Growth Strategy (Task 7)
5. Report Generator (Task 8)
6. API Router (Task 9)
7. Frontend Integration (Task 12)

## Notes

- The service uses async/await for all database operations
- Session expiration is checked on load
- Auto-save prevents data loss during long conversations
- State machine ensures consistent conversation flow
- Budget extraction supports multiple number formats
- Business idea extraction uses AI for intelligent parsing
