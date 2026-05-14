# AI Business Analysis API Documentation

## Base URL

```
https://api.astramark.com/api/ai/business-analysis
```

## Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. Start New Session

Start a new business analysis session.

**Endpoint:** `POST /start`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "message": "Hello! I'm your AI Business Analysis Assistant...",
  "state": "GREETING"
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `500`: Server error

---

### 2. Send Chat Message

Process user message in conversation.

**Endpoint:** `POST /chat`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "message": "I want to start a food delivery business in Mumbai"
}
```

**Response:**
```json
{
  "message": "Great! Let me confirm I understand your business idea...",
  "state": "BUSINESS_IDEA_CONFIRMATION",
  "session_id": "uuid-string",
  "requires_input": true,
  "metadata": {
    "business_idea": {
      "industry": "Food & Beverage",
      "product_service_type": "Food Delivery",
      "target_market": "Urban consumers",
      "geographic_location": "Mumbai"
    }
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `403`: Access denied (not your session)
- `404`: Session not found
- `500`: Server error

---

### 3. Generate Report

Generate comprehensive business analysis report.

**Endpoint:** `POST /generate-report`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "format": "pdf"
}
```

**Supported Formats:**
- `pdf`: PDF document
- `docx`: Microsoft Word document
- `json`: JSON data

**Response:**
```json
{
  "report_id": "uuid-string",
  "session_id": "uuid-string",
  "format": "pdf",
  "file_size": 2048576,
  "generation_timestamp": "2024-01-15T10:30:00Z",
  "download_url": "/api/ai/business-analysis/download/report-id"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid format or incomplete session
- `401`: Unauthorized
- `403`: Access denied
- `404`: Session not found
- `500`: Server error

---

### 4. Download Report

Download generated report file.

**Endpoint:** `GET /download/{report_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
- Binary file stream (PDF, DOCX, or JSON)
- Content-Type header set appropriately
- Content-Disposition header with filename

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `403`: Access denied
- `404`: Report not found
- `503`: Database unavailable

---

### 5. List User Sessions

Get list of user's analysis sessions.

**Endpoint:** `GET /sessions`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (optional): Maximum sessions to return (default: 10)

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "uuid-string",
      "state": "COMPLETE",
      "created_at": "2024-01-15T10:00:00Z",
      "business_idea_summary": "Food Delivery in Mumbai",
      "budget_summary": "INR 2,500,000"
    }
  ],
  "total_count": 1
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `500`: Server error

---

### 6. Resume Session

Resume an interrupted session.

**Endpoint:** `PUT /sessions/{session_id}/resume`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "state": "BUDGET_COLLECTION",
  "message": "Session resumed successfully...",
  "conversation_history": [
    {
      "role": "assistant",
      "content": "Hello! I'm your AI...",
      "timestamp": "2024-01-15T10:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `403`: Access denied
- `404`: Session not found or expired
- `500`: Server error

---

### 7. Delete Session

Permanently delete a session.

**Endpoint:** `DELETE /sessions/{session_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `404`: Session not found
- `500`: Server error

---

### 8. Get Analysis Status

Get current status and progress of analysis.

**Endpoint:** `GET /sessions/{session_id}/status`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "in_progress",
  "progress_percentage": 60,
  "current_step": "Collecting budget information",
  "result": null
}
```

**Status Values:**
- `in_progress`: Analysis ongoing
- `completed`: Analysis complete
- `failed`: Analysis failed

**Status Codes:**
- `200`: Success
- `401`: Unauthorized
- `403`: Access denied
- `404`: Session not found
- `500`: Server error

---

## Conversation States

The conversation follows a state machine:

1. **GREETING**: Initial state
2. **BUSINESS_IDEA_COLLECTION**: Collecting business details
3. **BUSINESS_IDEA_CONFIRMATION**: Confirming business idea
4. **BUDGET_COLLECTION**: Collecting budget information
5. **BUDGET_CONFIRMATION**: Confirming budget
6. **ANALYSIS_IN_PROGRESS**: Conducting analysis
7. **ANALYSIS_COMPLETE**: Analysis finished
8. **REPORT_GENERATION**: Generating report
9. **COMPLETE**: Session complete

## Data Models

### BusinessIdea

```json
{
  "description": "string",
  "industry": "string",
  "target_market": "string",
  "product_service_type": "string",
  "geographic_location": "string",
  "key_features": ["string"],
  "unique_value_proposition": "string"
}
```

### Budget

```json
{
  "amount": 50000.0,
  "currency": "USD",
  "confidence": 1.0
}
```

### MarketResearch

```json
{
  "competitors": [
    {
      "name": "string",
      "domain": "string",
      "description": "string",
      "strengths": ["string"],
      "weaknesses": ["string"],
      "market_position": "string",
      "pricing_strategy": "string"
    }
  ],
  "market_size": {
    "value": "$10B",
    "confidence_interval": "$8B-$12B",
    "confidence_level": "High",
    "source": "string"
  },
  "trends": [
    {
      "title": "string",
      "description": "string",
      "relevance_score": 0.8,
      "impact": "High"
    }
  ],
  "target_audience": {
    "age_range": "25-45",
    "income_level": "Medium",
    "geographic_distribution": ["string"],
    "behavioral_characteristics": ["string"],
    "pain_points": ["string"]
  }
}
```

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Missing or invalid token
- `403`: Forbidden - Access denied to resource
- `404`: Not Found - Resource doesn't exist
- `500`: Internal Server Error - Server-side issue
- `503`: Service Unavailable - External service down

## Rate Limiting

- **Rate Limit**: 100 requests per minute per user
- **Burst**: 20 requests per second
- **Headers**: 
  - `X-RateLimit-Limit`: Total limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Security

### Data Encryption

- Business idea descriptions encrypted with AES-256
- All data transmitted over HTTPS
- JWT tokens for authentication

### Access Control

- User-specific session access
- Session expiration (24 hours)
- Automatic cleanup of expired data

### Best Practices

1. **Store tokens securely**: Never expose in client-side code
2. **Use HTTPS**: Always use secure connections
3. **Handle errors gracefully**: Implement retry logic
4. **Respect rate limits**: Implement backoff strategies
5. **Validate input**: Sanitize user input before sending

## Code Examples

### Python

```python
import requests

BASE_URL = "https://api.astramark.com/api/ai/business-analysis"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Start session
response = requests.post(f"{BASE_URL}/start", headers=headers)
session_data = response.json()
session_id = session_data["session_id"]

# Send message
response = requests.post(
    f"{BASE_URL}/chat",
    headers=headers,
    json={
        "session_id": session_id,
        "message": "I want to start a SaaS business"
    }
)
chat_response = response.json()

# Generate report
response = requests.post(
    f"{BASE_URL}/generate-report",
    headers=headers,
    json={
        "session_id": session_id,
        "format": "pdf"
    }
)
report_data = response.json()

# Download report
response = requests.get(
    f"{BASE_URL}/download/{report_data['report_id']}",
    headers=headers
)
with open("report.pdf", "wb") as f:
    f.write(response.content)
```

### JavaScript

```javascript
const BASE_URL = "https://api.astramark.com/api/ai/business-analysis";
const TOKEN = "your_jwt_token";

const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// Start session
const startResponse = await fetch(`${BASE_URL}/start`, {
  method: "POST",
  headers
});
const sessionData = await startResponse.json();
const sessionId = sessionData.session_id;

// Send message
const chatResponse = await fetch(`${BASE_URL}/chat`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    session_id: sessionId,
    message: "I want to start a SaaS business"
  })
});
const chatData = await chatResponse.json();

// Generate report
const reportResponse = await fetch(`${BASE_URL}/generate-report`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    session_id: sessionId,
    format: "pdf"
  })
});
const reportData = await reportResponse.json();

// Download report
const downloadResponse = await fetch(
  `${BASE_URL}/download/${reportData.report_id}`,
  { headers }
);
const blob = await downloadResponse.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "report.pdf";
a.click();
```

## Support

- **Documentation**: https://docs.astramark.com
- **API Status**: https://status.astramark.com
- **Support Email**: api-support@astramark.com
- **GitHub Issues**: https://github.com/astramark/api/issues

## Changelog

### v1.0.0 (2024-01-15)
- Initial API release
- All core endpoints implemented
- Multi-format report generation
- Session management
- Error handling and fallbacks
