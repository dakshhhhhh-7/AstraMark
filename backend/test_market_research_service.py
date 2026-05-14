"""
Unit tests for MarketResearchService
Tests market data aggregation, caching, and analysis
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch

from market_research_service import (
    MarketResearchService, MarketResearchResult, Competitor,
    MarketSize, Trend, TargetAudience
)


@pytest.fixture
def mock_services():
    """Mock external services"""
    serp = Mock()
    serp.search_competitors = AsyncMock(return_value={'competitors': []})
    serp.get_market_trends = AsyncMock(return_value={'trends': []})
    
    apify = Mock()
    apify.search_competitors = AsyncMock(return_value={'competitors': []})
    apify.get_market_trends = AsyncMock(return_value={'trends': []})
    
    real_market = Mock()
    real_market.search_competitors = AsyncMock(return_value={'competitors': []})
    real_market.get_market_trends = AsyncMock(return_value={'trends': []})
    
    groq = Mock()
    groq.is_available = Mock(return_value=True)
    groq.generate_analysis = AsyncMock()
    
    return serp, apify, real_market, groq


@pytest.fixture
def mock_db():
    """Mock MongoDB database"""
    db = Mock()
    db.market_research_cache = Mock()
    db.market_research_cache.find_one = AsyncMock(return_value=None)
    db.market_research_cache.update_one = AsyncMock()
    db.market_research_cache.delete_one = AsyncMock()
    return db


@pytest.fixture
def service(mock_services, mock_db):
    """Create MarketResearchService instance"""
    serp, apify, real_market, groq = mock_services
    return MarketResearchService(serp, apify, real_market, groq, mock_db)


@pytest.mark.asyncio
async def test_research_market_with_cache(service, mock_db):
    """Test market research with cached data"""
    cached_data = {
        "cache_key": "test_key",
        "data": {
            "competitors": [],
            "market_size": {
                "value": "$10B",
                "confidence_interval": "$8B-$12B",
                "confidence_level": "High",
                "source": "cached"
            },
            "trends": [],
            "target_audience": {
                "age_range": "25-45",
                "income_level": "Medium",
                "geographic_distribution": ["US"],
                "behavioral_characteristics": [],
                "pain_points": []
            },
            "research_timestamp": datetime.now(timezone.utc).isoformat(),
            "data_sources": ["cache"]
        },
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=12)
    }
    
    mock_db.market_research_cache.find_one.return_value = cached_data
    
    result = await service.research_market(
        business_type="SaaS",
        industry="Technology",
        target_market="SMBs",
        geographic_location="US"
    )
    
    assert result is not None
    assert result.market_size.value == "$10B"


@pytest.mark.asyncio
async def test_find_competitors_minimum_count(service, mock_services):
    """Test that at least 3 competitors are returned"""
    serp, apify, real_market, groq = mock_services
    
    # Mock empty responses from all sources
    serp.search_competitors.return_value = {'competitors': []}
    apify.search_competitors.return_value = {'competitors': []}
    real_market.search_competitors.return_value = {'competitors': []}
    
    competitors = await service.find_competitors("SaaS", "SMBs", limit=10)
    
    assert len(competitors) >= 3
    assert all(isinstance(c, Competitor) for c in competitors)


@pytest.mark.asyncio
async def test_find_competitors_deduplication(service, mock_services):
    """Test competitor deduplication by domain"""
    serp, apify, real_market, groq = mock_services
    
    # Mock duplicate competitors from different sources
    serp.search_competitors.return_value = {
        'competitors': [
            {'name': 'Competitor A', 'domain': 'competitor-a.com', 'description': 'Test'}
        ]
    }
    apify.search_competitors.return_value = {
        'competitors': [
            {'name': 'Competitor A', 'domain': 'www.competitor-a.com', 'description': 'Test'}
        ]
    }
    real_market.search_competitors.return_value = {'competitors': []}
    
    groq.generate_analysis.return_value = {
        'strengths': ['Strong brand'],
        'weaknesses': ['High price'],
        'market_position': 'Leader',
        'pricing_strategy': 'Premium'
    }
    
    competitors = await service.find_competitors("SaaS", "SMBs", limit=10)
    
    # Should have deduplicated to 1 unique competitor + 2 fallback
    assert len(competitors) == 3


@pytest.mark.asyncio
async def test_estimate_market_size_with_ai(service, mock_services):
    """Test market size estimation using AI"""
    serp, apify, real_market, groq = mock_services
    
    groq.generate_analysis.return_value = {
        'value': '$50B',
        'confidence_interval': '$45B-$55B',
        'confidence_level': 'High',
        'methodology': 'Industry reports and growth trends'
    }
    
    market_size = await service.estimate_market_size("Technology", "Global", "USD")
    
    assert market_size.value == '$50B'
    assert market_size.confidence_level == 'High'
    assert market_size.source == 'groq_ai_analysis'


@pytest.mark.asyncio
async def test_estimate_market_size_fallback(service, mock_services):
    """Test market size estimation fallback"""
    serp, apify, real_market, groq = mock_services
    
    groq.is_available.return_value = False
    
    market_size = await service.estimate_market_size("Technology", "US", "USD")
    
    assert market_size is not None
    assert market_size.source == 'rule_based_estimation'
    assert '$' in market_size.value


@pytest.mark.asyncio
async def test_extract_trends_minimum_count(service, mock_services):
    """Test that at least 5 trends are returned"""
    serp, apify, real_market, groq = mock_services
    
    # Mock minimal trend data
    serp.get_market_trends.return_value = {
        'trends': [
            {'title': 'AI Integration', 'description': 'Growing AI adoption'}
        ]
    }
    
    trends = await service.extract_trends("Technology", count=5)
    
    assert len(trends) >= 5
    assert all(isinstance(t, Trend) for t in trends)


@pytest.mark.asyncio
async def test_identify_target_audience_with_ai(service, mock_services):
    """Test target audience identification using AI"""
    serp, apify, real_market, groq = mock_services
    
    groq.generate_analysis.return_value = {
        'age_range': '25-40',
        'income_level': 'High',
        'geographic_distribution': ['Urban areas', 'Tech hubs'],
        'behavioral_characteristics': ['Early adopters', 'Tech-savvy'],
        'pain_points': ['Time management', 'Efficiency'],
        'buying_triggers': ['ROI', 'Ease of use'],
        'estimated_size': '10M users'
    }
    
    audience = await service.identify_target_audience("SaaS", "Professionals", "US")
    
    assert audience.age_range == '25-40'
    assert audience.income_level == 'High'
    assert len(audience.behavioral_characteristics) > 0


@pytest.mark.asyncio
async def test_cache_research_data(service, mock_db):
    """Test caching of research data"""
    result = MarketResearchResult(
        competitors=[],
        market_size=MarketSize(
            value="$10B",
            confidence_interval="$8B-$12B",
            confidence_level="High",
            source="test"
        ),
        trends=[],
        target_audience=TargetAudience(
            age_range="25-45",
            income_level="Medium",
            geographic_distribution=["US"],
            behavioral_characteristics=[],
            pain_points=[]
        ),
        data_sources=["test"]
    )
    
    await service.cache_research("test_key", result, ttl_hours=24)
    
    mock_db.market_research_cache.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_timeout_handling(service, mock_services):
    """Test timeout handling for external services"""
    serp, apify, real_market, groq = mock_services
    
    # Mock timeout
    async def timeout_func(*args, **kwargs):
        await asyncio.sleep(35)  # Longer than 30 second timeout
        return {'competitors': []}
    
    serp.search_competitors = timeout_func
    
    result = await service.research_market(
        business_type="SaaS",
        industry="Technology",
        target_market="SMBs",
        geographic_location="US"
    )
    
    # Should complete with fallback data despite timeout
    assert result is not None
    assert len(result.competitors) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
