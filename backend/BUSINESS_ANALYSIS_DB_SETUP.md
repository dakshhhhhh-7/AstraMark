# Business Analysis Database Setup

## Overview

This document describes the MongoDB collections and indexes created for the AI Business Analysis feature. The database infrastructure supports efficient storage and retrieval of analysis sessions, reports, and cached market research data.

## Collections

### 1. `analysis_sessions`

Stores active and completed business analysis sessions with conversation history and extracted data.

**Schema:**
```javascript
{
  "_id": ObjectId,
  "session_id": String (UUID),           // Unique session identifier
  "user_id": String,                     // User who created the session
  "status": String,                      // "in_progress", "completed", "interrupted"
  "conversation_state": String,          // State machine state
  "conversation_history": [              // Chat messages
    {
      "role": String,                    // "user" or "assistant"
      "content": String,                 // Message content
      "timestamp": DateTime
    }
  ],
  "business_idea": {                     // Extracted business idea
    "description": String,
    "industry": String,
    "target_market": String,
    "geographic_location": String,
    "product_service_type": String,
    "extracted_at": DateTime
  },
  "budget": {                            // Extracted budget
    "amount": Float,
    "currency": String,                  // "INR", "USD", "EUR"
    "extracted_at": DateTime
  },
  "analysis_result_id": String,          // Reference to business_analysis_reports
  "created_at": DateTime,
  "updated_at": DateTime,
  "last_activity_at": DateTime,
  "expires_at": DateTime,                // Auto-cleanup after 24 hours
  "metadata": {
    "user_agent": String,
    "ip_address": String,
    "session_duration_seconds": Int
  }
}
```

**Indexes:**
- `session_id_unique` - Unique index on `session_id` for fast lookups
- `user_id_created_at_compound` - Compound index on `user_id` + `created_at` (descending) for user history queries
- `expires_at_ttl` - TTL index on `expires_at` for automatic cleanup after 24 hours
- `status_index` - Index on `status` for filtering by session status
- `last_activity_at_index` - Index on `last_activity_at` for activity-based queries

**Purpose:**
- Store conversation state for resumable sessions
- Enable session recovery after interruptions
- Auto-cleanup expired sessions (24 hours after last activity)
- Support user analysis history

---

### 2. `business_analysis_reports`

Stores generated business analysis reports with all analysis components.

**Schema:**
```javascript
{
  "_id": ObjectId,
  "report_id": String (UUID),            // Unique report identifier
  "session_id": String,                  // Reference to analysis_sessions
  "user_id": String,                     // User who owns the report
  "business_idea": Object,               // Business idea details
  "budget": Object,                      // Budget breakdown
  "market_research": Object,             // Market research results
  "financial_projections": Object,       // Financial projections
  "risk_assessment": Object,             // Risk analysis
  "growth_strategy": Object,             // Growth strategy
  "report_files": {                      // Generated report files
    "pdf_url": String,
    "docx_url": String,
    "json_url": String
  },
  "sharing_links": [                     // Shared report links
    {
      "link_id": String,
      "url": String,
      "created_at": DateTime,
      "expires_at": DateTime,
      "access_count": Int,
      "last_accessed_at": DateTime
    }
  ],
  "generation_metadata": {
    "generation_time_seconds": Float,
    "ai_service_used": String,           // "groq", "gemini", "fallback"
    "data_sources": [String],
    "confidence_scores": Object
  },
  "created_at": DateTime,
  "updated_at": DateTime
}
```

**Indexes:**
- `report_id_unique` - Unique index on `report_id` for fast lookups
- `user_id_created_at_compound` - Compound index on `user_id` + `created_at` (descending) for user report history
- `session_id_index` - Index on `session_id` for linking reports to sessions

**Purpose:**
- Store complete analysis results
- Enable report downloads and sharing
- Support user report history
- Track report generation metadata

---

### 3. `market_research_cache`

Caches market research data to reduce external API calls and improve performance.

**Schema:**
```javascript
{
  "_id": ObjectId,
  "cache_key": String,                   // Hash of (business_type + target_market + currency)
  "business_type": String,               // Industry/business type
  "target_market": String,               // Target market description
  "currency": String,                    // "INR", "USD", "EUR"
  "research_data": Object,               // Cached market research results
  "cached_at": DateTime,
  "expires_at": DateTime,                // Auto-cleanup after 24 hours
  "hit_count": Int,                      // Number of cache hits
  "last_accessed_at": DateTime
}
```

**Indexes:**
- `cache_key_unique` - Unique index on `cache_key` for fast cache lookups
- `expires_at_ttl` - TTL index on `expires_at` for automatic cleanup after 24 hours
- `business_type_target_market_compound` - Compound index on `business_type` + `target_market` for queries
- `last_accessed_at_index` - Index on `last_accessed_at` for cache management

**Purpose:**
- Cache market research results to reduce API calls
- Improve response times for similar business ideas
- Auto-cleanup stale cache entries (24 hours)
- Track cache hit rates

---

## Setup Instructions

### 1. Initialize Collections and Indexes

Run the initialization script to create all collections and indexes:

```bash
cd backend
python init_business_analysis_db.py
```

This will:
- Create the three collections
- Add all required indexes
- Verify the setup

### 2. Verify Setup

Verify that all collections and indexes exist:

```bash
python init_business_analysis_db.py --verify
```

### 3. Test Collections

Run the test script to verify collections work correctly:

```bash
python test_business_analysis_db.py
```

This will:
- Insert sample documents
- Test all indexes
- Verify TTL behavior
- Clean up test data

---

## Key Features

### Automatic Cleanup (TTL Indexes)

Both `analysis_sessions` and `market_research_cache` collections have TTL indexes on the `expires_at` field:

- **Sessions**: Automatically deleted 24 hours after `last_activity_at`
- **Cache**: Automatically deleted 24 hours after `cached_at`

MongoDB checks TTL indexes every 60 seconds and removes expired documents.

### Efficient Queries

**User History Queries:**
```python
# Get user's recent sessions (uses compound index)
sessions = await db.analysis_sessions.find(
    {"user_id": user_id}
).sort("created_at", -1).limit(10).to_list(length=10)

# Get user's recent reports (uses compound index)
reports = await db.business_analysis_reports.find(
    {"user_id": user_id}
).sort("created_at", -1).limit(10).to_list(length=10)
```

**Cache Lookups:**
```python
# Fast cache lookup (uses unique index)
import hashlib
cache_key = hashlib.sha256(
    f"{business_type}_{target_market}_{currency}".encode()
).hexdigest()

cached_data = await db.market_research_cache.find_one(
    {"cache_key": cache_key}
)
```

**Session Recovery:**
```python
# Fast session lookup (uses unique index)
session = await db.analysis_sessions.find_one(
    {"session_id": session_id}
)
```

---

## Maintenance

### Drop Collections (CAUTION!)

To drop all business analysis collections (this will delete all data):

```bash
python init_business_analysis_db.py --drop
```

You will be prompted to confirm before deletion.

### Monitor TTL Index

Check TTL index status:

```javascript
// In MongoDB shell
use astramark_dev

// Check TTL index on analysis_sessions
db.analysis_sessions.getIndexes()

// Check TTL index on market_research_cache
db.market_research_cache.getIndexes()
```

### View Collection Stats

```javascript
// In MongoDB shell
use astramark_dev

// View collection statistics
db.analysis_sessions.stats()
db.business_analysis_reports.stats()
db.market_research_cache.stats()
```

---

## Requirements Satisfied

This implementation satisfies the following requirements:

- **REQ-9**: Report Download and Storage
  - Stores analysis sessions and reports in MongoDB
  - Provides analysis history for users
  - Retains sessions for at least 365 days (reports are permanent, sessions expire after 24 hours of inactivity)

- **REQ-12**: Analysis Session Management and Recovery
  - Auto-saves session state
  - Preserves interrupted sessions for 24 hours
  - Enables session resumption

- **REQ-13**: Data Privacy and Security
  - User-specific access control via `user_id` indexes
  - Efficient queries for user data
  - Automatic cleanup of expired sessions

---

## Performance Considerations

### Index Usage

All queries use indexes for optimal performance:

1. **Unique lookups** (session_id, report_id, cache_key) - O(log n)
2. **User history queries** (user_id + created_at) - O(log n + k) where k is result size
3. **Status filtering** - O(log n + k)
4. **Cache lookups** - O(log n)

### TTL Index Overhead

TTL indexes have minimal overhead:
- MongoDB checks every 60 seconds
- Deletion is performed in the background
- Does not impact query performance

### Cache Hit Rate

Monitor cache hit rate to optimize API usage:

```python
# Get cache statistics
cache_stats = await db.market_research_cache.aggregate([
    {
        "$group": {
            "_id": None,
            "total_entries": {"$sum": 1},
            "total_hits": {"$sum": "$hit_count"},
            "avg_hits": {"$avg": "$hit_count"}
        }
    }
]).to_list(length=1)
```

---

## Troubleshooting

### Issue: Collections not created

**Solution:** Ensure MongoDB is running and accessible:
```bash
# Check MongoDB status
mongosh --eval "db.adminCommand('ping')"

# Run initialization script
python init_business_analysis_db.py
```

### Issue: TTL index not working

**Solution:** TTL indexes require:
1. The field must be a Date type (not string)
2. MongoDB checks every 60 seconds
3. The document must have passed the expiration time

Verify TTL index:
```javascript
db.analysis_sessions.getIndexes().filter(idx => idx.name === "expires_at_ttl")
```

### Issue: Slow queries

**Solution:** Verify indexes are being used:
```javascript
// Explain query plan
db.analysis_sessions.find({"user_id": "test_user"}).explain("executionStats")
```

Look for `"stage": "IXSCAN"` (index scan) instead of `"stage": "COLLSCAN"` (collection scan).

---

## Files

- `init_business_analysis_db.py` - Initialization script
- `test_business_analysis_db.py` - Test script
- `BUSINESS_ANALYSIS_DB_SETUP.md` - This documentation

---

## Next Steps

After setting up the database:

1. ✅ Collections and indexes created
2. ✅ Test script verified functionality
3. ⏭️ Integrate with `business_analysis_service.py`
4. ⏭️ Implement session management in API router
5. ⏭️ Add encryption for sensitive data (REQ-13)

---

**Last Updated:** 2026-05-14
**Version:** 1.0
**Author:** AstraMark Development Team
