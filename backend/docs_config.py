"""
API Documentation Configuration
"""

# OpenAPI metadata
OPENAPI_METADATA = {
    "title": "AstraMark AI Marketing API",
    "description": """
    ## AstraMark AI Marketing Intelligence Platform API
    
    AstraMark is an AI-powered marketing platform that generates comprehensive marketing strategies, 
    competitor analysis, and business insights using advanced AI models.
    
    ### Features
    - **AI-Powered Analysis**: Generate marketing strategies using Gemini 2.0 Flash
    - **Market Intelligence**: Live competitor data and market trends
    - **Content Generation**: Pitch decks, content calendars, email sequences
    - **Blockchain Verification**: Timestamp analyses on Polygon blockchain
    - **Subscription Management**: Stripe-powered billing and plan management
    
    ### Authentication
    This API uses JWT Bearer tokens for authentication. Register an account and obtain tokens via the auth endpoints.
    
    ### Rate Limiting
    - Free tier: 5 requests per minute
    - Pro tier: 30 requests per minute
    - Growth tier: 100 requests per minute
    
    ### Support
    For API support, contact: support@astramark.ai
    """,
    "version": "1.0.0",
    "contact": {
        "name": "AstraMark Support",
        "email": "support@astramark.ai",
        "url": "https://astramark.ai/support"
    },
    "license_info": {
        "name": "Commercial License",
        "url": "https://astramark.ai/license"
    },
    "servers": [
        {
            "url": "https://api.astramark.ai",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.astramark.ai", 
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8001",
            "description": "Development server"
        }
    ]
}

# API Tags for organization
TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "User registration, login, and token management"
    },
    {
        "name": "Analysis",
        "description": "AI-powered business and marketing analysis"
    },
    {
        "name": "Content Generation", 
        "description": "Generate pitch decks, content calendars, and email sequences"
    },
    {
        "name": "Market Intelligence",
        "description": "Live market data, competitor insights, and signals"
    },
    {
        "name": "Payments",
        "description": "Subscription management and billing"
    },
    {
        "name": "Export",
        "description": "Export reports and data in various formats"
    },
    {
        "name": "Health",
        "description": "System health and monitoring endpoints"
    }
]