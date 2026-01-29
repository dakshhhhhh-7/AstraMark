# ⚡ Quick Start Fixes - Do These First

**Time Required:** 10-15 hours  
**Priority:** CRITICAL - Do before any public launch

---

## 🔴 Critical Security Fixes (Do Today)

### 1. Remove Hardcoded API Keys (30 minutes)

**Problem:** Google API key is exposed in `.env` file

**Fix:**
```bash
# 1. Remove from .env
# 2. Add to .env.example (without real key)
GOOGLE_API_KEY=your_key_here

# 3. Add .env to .gitignore (if not already)
echo ".env" >> .gitignore

# 4. Regenerate Google API key (old one is compromised)
# Go to: https://console.cloud.google.com/apis/credentials
```

**Files to Update:**
- `backend/.env` - Remove real keys
- `.gitignore` - Ensure `.env` is ignored
- Create `backend/.env.example` - Template with placeholders

---

### 2. Fix CORS Configuration (15 minutes)

**Problem:** `CORS_ORIGINS=*` allows any website to access your API

**Fix:**
```python
# backend/server_enhanced.py (line 863-868)

# BEFORE:
allow_origins=os.environ.get('CORS_ORIGINS', '*').split(',')

# AFTER:
allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,  # Specific origins only
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Update `.env`:**
```bash
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

### 3. Add Rate Limiting (1 hour)

**Problem:** No protection against API abuse

**Install:**
```bash
cd backend
pip install slowapi
```

**Add to `server_enhanced.py`:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to analyze endpoint:
@api_router.post("/analyze")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def analyze_business(...):
    ...
```

---

### 4. Add Input Validation (2 hours)

**Problem:** No validation on user inputs

**Add Pydantic validators:**
```python
# backend/models.py
from pydantic import BaseModel, Field, validator

class BusinessInput(BaseModel):
    business_type: str = Field(..., min_length=2, max_length=100)
    target_market: str = Field(..., min_length=2, max_length=200)
    monthly_budget: str = Field(..., regex=r'^\$?\d+([,.]\d+)?$')
    primary_goal: str = Field(..., min_length=10, max_length=500)
    additional_info: Optional[str] = Field(None, max_length=1000)
    
    @validator('business_type')
    def validate_business_type(cls, v):
        # Block SQL injection attempts
        if any(char in v for char in ['<', '>', '{', '}', 'script']):
            raise ValueError('Invalid characters in business_type')
        return v.strip()
```

---

### 5. Fix Deprecated Code (1 hour)

**Problem:** Using deprecated `google.generativeai` and `on_event`

**Fix 1 - Update Gemini Import:**
```python
# BEFORE:
import google.generativeai as genai

# AFTER:
from google import genai  # New package
```

**Fix 2 - Replace on_event:**
```python
# BEFORE:
@app.on_event("startup")
async def startup_event():
    ...

# AFTER:
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AstraMark Enhanced Server...")
    background_scanner.start()
    yield
    # Shutdown
    background_scanner.stop()
    if client:
        client.close()

app = FastAPI(title="AstraMark", lifespan=lifespan)
```

---

## 🟡 Important Fixes (Do This Week)

### 6. Add Error Handling (2 hours)

**Add global exception handler:**
```python
# backend/middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    if os.getenv("ENVIRONMENT") == "production":
        message = "An error occurred. Please try again later."
    else:
        message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": message,
            "request_id": getattr(request.state, "request_id", None)
        }
    )
```

---

### 7. Add Structured Logging (1 hour)

**Install:**
```bash
pip install structlog
```

**Setup:**
```python
# backend/logging_config.py
import structlog
import logging

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

---

### 8. Remove Mock Database Fallback (30 minutes)

**Problem:** Mock DB loses data on restart

**Fix:**
```python
# backend/server_enhanced.py

# REMOVE MockDB class entirely (lines 156-212)

# UPDATE connection to fail fast:
try:
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    # Test connection
    await client.admin.command('ping')
    db = client[DB_NAME]
    logger.info(f"Connected to MongoDB: {MONGO_URL}")
except Exception as e:
    logger.critical(f"MongoDB connection failed: {e}")
    raise  # Fail fast, don't use mock
```

---

## 🟢 Database Improvements (Do This Week)

### 9. Add Database Indexes (30 minutes)

**Create migration script:**
```python
# backend/migrations/add_indexes.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def add_indexes():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    # Users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")
    
    # Analyses collection
    await db.analyses.create_index("business_id")
    await db.analyses.create_index("created_at")
    await db.analyses.create_index([("business_id", 1), ("created_at", -1)])
    
    # Market signals
    await db.market_signals.create_index("detected_at")
    await db.market_signals.create_index([("business_type", 1), ("detected_at", -1)])
    
    print("Indexes created successfully")

asyncio.run(add_indexes())
```

---

## 📋 Checklist

**Do Today (Critical):**
- [ ] Remove hardcoded API keys
- [ ] Fix CORS configuration
- [ ] Add rate limiting
- [ ] Regenerate compromised API keys

**Do This Week:**
- [ ] Add input validation
- [ ] Fix deprecated code
- [ ] Add error handling
- [ ] Add structured logging
- [ ] Remove mock database
- [ ] Add database indexes

**Total Time:** ~10-15 hours

---

## 🚀 After Quick Fixes

Once these are done, you can:
1. Deploy to staging environment
2. Start Phase 1 of the Production Roadmap
3. Begin adding authentication
4. Integrate real data sources

---

**Priority Order:**
1. Security fixes (today)
2. Error handling (this week)
3. Database improvements (this week)
4. Then proceed with Production Roadmap Phase 1

---

*These fixes make your app secure enough for limited testing. Full production readiness requires completing the Production Roadmap.*
