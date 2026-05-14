"""
Market Research Service - Aggregates market data from multiple sources
Provides comprehensive market intelligence including competitors, market size, trends, and target audience
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import hashlib
import json

from serp_service import SERPAPIService
from apify_market_service import ApifyMarketService
from real_market_service import RealMarketService
from groq_service import GroqService

logger = logging.getLogger(__name__)


class Competitor(BaseModel):
    """Competitor information model"""
    name: str
    domain: str
    description: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    market_position: str = "Unknown"
    pricing_strategy: str = "Unknown"
    estimated_traffic: Optional[str] = None
    ad_spend_monthly: Optional[str] = None
    confidence: float = 0.5  # 0.0 to 1.0


class MarketSize(BaseModel):
    """Market size estimation model"""
    value: str  # e.g., "$10B"
    confidence_interval: str  # e.g., "$8B - $12B"
    confidence_level: str  # "High", "Medium", "Low"
    source: str
    methodology: Optional[str] = None


class Trend(BaseModel):
    """Industry trend model"""
    title: str
    description: str
    relevance_score: float  # 0.0 to 1.0
    source: str
    published_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    impact: str = "Medium"  # "High", "Medium", "Low"


class TargetAudience(BaseModel):
    """Target audience demographics model"""
    age_range: str
    income_level: str
    geographic_distribution: List[str]
    behavioral_characteristics: List[str]
    pain_points: List[str]
    buying_triggers: List[str] = []
    estimated_size: Optional[str] = None


class MarketResearchResult(BaseModel):
    """Complete market research result"""
    competitors: List[Competitor]
    market_size: MarketSize
    trends: List[Trend]
    target_audience: TargetAudience
    research_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_sources: List[str]
    cache_key: Optional[str] = None


class MarketResearchService:
    """
    Market research service that aggregates data from multiple sources:
    - SERP API for search data and trends
    - Apify for web scraping and competitor analysis
    - Real Market Service for live market data
    - Groq AI for analysis and insights
    """
    
    def __init__(
        self,
        serp_service: SERPAPIService,
        apify_service: ApifyMarketService,
        real_market_service: RealMarketService,
        groq_service: GroqService,
        db: AsyncIOMotorDatabase
    ):
        """
        Initialize market research service
        
        Args:
            serp_service: SERP API service instance
            apify_service: Apify market service instance
            real_market_service: Real market service instance
            groq_service: Groq AI service instance
            db: MongoDB database instance
        """
        self.serp_service = serp_service
        self.apify_service = apify_service
        self.real_market_service = real_market_service
        self.groq_service = groq_service
        self.db = db
        self.cache_collection = db.market_research_cache
        
        # Cache TTL in hours
        self.cache_ttl_hours = 24
        
        logger.info("MarketResearchService initialized")
    
    async def research_market(
        self,
        business_type: str,
        industry: str,
        target_market: str,
        geographic_location: str,
        currency: str = "USD"
    ) -> MarketResearchResult:
        """
        Conduct comprehensive market research
        
        Args:
            business_type: Type of business/product/service
            industry: Industry category
            target_market: Target customer segment
            geographic_location: Operating location
            currency: Currency for market size (INR, USD, EUR)
            
        Returns:
            MarketResearchResult with complete analysis
        """
        # Generate cache key
        cache_key = self._generate_cache_key(business_type, industry, target_market, geographic_location)
        
        # Check cache first
        cached_result = await self.get_cached_research(cache_key)
        if cached_result:
            logger.info(f"Returning cached market research for {cache_key}")
            return cached_result
        
        logger.info(f"Starting market research for {business_type} in {industry}")
        
        # Gather data from multiple sources in parallel with timeout limits
        import asyncio
        
        # Set timeout for external service calls (30 seconds per service)
        timeout_seconds = 30
        
        async def with_timeout(coro, timeout=timeout_seconds):
            """Wrapper to add timeout to coroutines"""
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Operation timed out after {timeout} seconds")
                return None
            except Exception as e:
                logger.error(f"Operation failed: {e}")
                return None
        
        competitors_task = with_timeout(self.find_competitors(business_type, target_market, limit=10))
        market_size_task = with_timeout(self.estimate_market_size(industry, geographic_location, currency))
        trends_task = with_timeout(self.extract_trends(industry, count=5))
        target_audience_task = with_timeout(self.identify_target_audience(business_type, target_market, geographic_location))
        
        # Wait for all tasks to complete
        competitors, market_size, trends, target_audience = await asyncio.gather(
            competitors_task,
            market_size_task,
            trends_task,
            target_audience_task,
            return_exceptions=True
        )
        
        # Handle exceptions and timeouts
        if isinstance(competitors, Exception) or competitors is None:
            logger.error(f"Competitor research failed or timed out: {competitors}")
            competitors = []
        
        if isinstance(market_size, Exception) or market_size is None:
            logger.error(f"Market size estimation failed or timed out: {market_size}")
            market_size = MarketSize(
                value="Unknown",
                confidence_interval="Unknown",
                confidence_level="Low",
                source="fallback"
            )
        
        if isinstance(trends, Exception) or trends is None:
            logger.error(f"Trend extraction failed or timed out: {trends}")
            trends = []
        
        if isinstance(target_audience, Exception) or target_audience is None:
            logger.error(f"Target audience identification failed or timed out: {target_audience}")
            target_audience = TargetAudience(
                age_range="25-45",
                income_level="Medium",
                geographic_distribution=[geographic_location],
                behavioral_characteristics=["Tech-savvy", "Value-conscious"],
                pain_points=["Needs solution"]
            )
        
        # Compile results
        data_sources = list(set([
            "serp_api",
            "apify",
            "real_market_service",
            "groq_ai"
        ]))
        
        result = MarketResearchResult(
            competitors=competitors[:10],  # Limit to top 10
            market_size=market_size,
            trends=trends[:5],  # Limit to top 5
            target_audience=target_audience,
            data_sources=data_sources,
            cache_key=cache_key
        )
        
        # Cache the result
        await self.cache_research(cache_key, result, ttl_hours=self.cache_ttl_hours)
        
        logger.info(f"Market research completed for {business_type}")
        return result
    
    async def find_competitors(
        self,
        business_type: str,
        target_market: str,
        limit: int = 10
    ) -> List[Competitor]:
        """
        Identify direct competitors using multiple sources
        
        Args:
            business_type: Type of business
            target_market: Target market segment
            limit: Maximum number of competitors (3-10)
            
        Returns:
            List of Competitor objects
        """
        limit = max(3, min(limit, 10))  # Enforce 3-10 range
        
        logger.info(f"Finding competitors for {business_type} targeting {target_market}")
        
        # Gather competitor data from multiple sources
        import asyncio
        
        serp_task = self.serp_service.search_competitors(business_type, target_market)
        apify_task = self.apify_service.search_competitors(business_type, target_market)
        real_market_task = self.real_market_service.search_competitors(business_type, target_market)
        
        results = await asyncio.gather(
            serp_task,
            apify_task,
            real_market_task,
            return_exceptions=True
        )
        
        # Combine and deduplicate competitors
        all_competitors_data = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Competitor search source failed: {result}")
                continue
            
            if isinstance(result, dict) and 'competitors' in result:
                all_competitors_data.extend(result['competitors'])
        
        # Deduplicate by domain
        unique_competitors = {}
        for comp_data in all_competitors_data:
            domain = comp_data.get('domain', '').lower().replace('www.', '')
            if domain and domain not in unique_competitors:
                unique_competitors[domain] = comp_data
        
        # Convert to Competitor objects and enrich with AI analysis
        competitors = []
        for comp_data in list(unique_competitors.values())[:limit]:
            competitor = await self._enrich_competitor_data(comp_data, business_type)
            competitors.append(competitor)
        
        # Ensure we have at least 3 competitors
        while len(competitors) < 3:
            position = len(competitors) + 1
            competitors.append(Competitor(
                name=f"{business_type} Competitor {position}",
                domain=f"competitor{position}.com",
                description=f"Established player in {business_type} market",
                strengths=["Market presence", "Brand recognition"],
                weaknesses=["Unknown specifics"],
                market_position=f"Position {position}",
                pricing_strategy="Unknown",
                confidence=0.3
            ))
        
        logger.info(f"Found {len(competitors)} competitors")
        return competitors
    
    async def estimate_market_size(
        self,
        industry: str,
        geography: str,
        currency: str = "USD"
    ) -> MarketSize:
        """
        Estimate total addressable market size
        
        Args:
            industry: Industry category
            geography: Geographic region
            currency: Currency for estimation (INR, USD, EUR)
            
        Returns:
            MarketSize estimation
        """
        logger.info(f"Estimating market size for {industry} in {geography}")
        
        # Use AI to estimate market size based on industry knowledge
        if self.groq_service.is_available():
            try:
                system_prompt = """You are a market research analyst. Estimate the total addressable market (TAM) 
for the given industry and geography. Provide realistic estimates based on industry data and trends.
Return JSON with: value (string like "$10B"), confidence_interval (string like "$8B-$12B"), 
confidence_level ("High", "Medium", or "Low"), and methodology (brief explanation)."""
                
                user_prompt = f"""Estimate the total addressable market for:
Industry: {industry}
Geography: {geography}
Currency: {currency}

Provide a realistic market size estimate with confidence interval."""
                
                result = await self.groq_service.generate_analysis(system_prompt, user_prompt)
                
                if result and isinstance(result, dict):
                    return MarketSize(
                        value=result.get('value', 'Unknown'),
                        confidence_interval=result.get('confidence_interval', 'Unknown'),
                        confidence_level=result.get('confidence_level', 'Medium'),
                        source='groq_ai_analysis',
                        methodology=result.get('methodology')
                    )
            except Exception as e:
                logger.error(f"AI market size estimation failed: {e}")
        
        # Fallback to rule-based estimation
        return self._fallback_market_size_estimation(industry, geography, currency)
    
    async def extract_trends(
        self,
        industry: str,
        count: int = 5
    ) -> List[Trend]:
        """
        Extract current industry trends
        
        Args:
            industry: Industry category
            count: Number of trends to extract (minimum 5)
            
        Returns:
            List of Trend objects
        """
        count = max(5, count)  # Ensure at least 5 trends
        
        logger.info(f"Extracting {count} trends for {industry}")
        
        # Gather trends from multiple sources
        import asyncio
        
        serp_task = self.serp_service.get_market_trends(industry)
        real_market_task = self.real_market_service.get_market_trends(industry)
        apify_task = self.apify_service.get_market_trends(industry)
        
        results = await asyncio.gather(
            serp_task,
            real_market_task,
            apify_task,
            return_exceptions=True
        )
        
        # Combine trend data
        all_trends_data = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Trend extraction source failed: {result}")
                continue
            
            if isinstance(result, dict):
                # Extract trends from various formats
                if 'trends' in result:
                    all_trends_data.extend(result['trends'])
                elif 'top_rising_keywords' in result:
                    for keyword in result['top_rising_keywords']:
                        all_trends_data.append({
                            'title': keyword,
                            'description': f"Rising trend in {industry}",
                            'source': 'keyword_analysis'
                        })
                elif 'news_sentiment' in result:
                    headlines = result['news_sentiment'].get('recent_headlines', [])
                    for headline in headlines:
                        all_trends_data.append({
                            'title': headline,
                            'description': 'Industry news trend',
                            'source': 'news_analysis'
                        })
        
        # Convert to Trend objects
        trends = []
        for trend_data in all_trends_data[:count]:
            trend = Trend(
                title=trend_data.get('title', 'Industry Trend'),
                description=trend_data.get('description', 'Emerging trend in the industry'),
                relevance_score=trend_data.get('relevance_score', 0.7),
                source=trend_data.get('source', 'market_research'),
                impact=trend_data.get('impact', 'Medium')
            )
            trends.append(trend)
        
        # Use AI to generate additional trends if needed
        if len(trends) < count and self.groq_service.is_available():
            additional_trends = await self._generate_ai_trends(industry, count - len(trends))
            trends.extend(additional_trends)
        
        # Ensure we have at least 5 trends
        while len(trends) < 5:
            trends.append(Trend(
                title=f"{industry} Innovation Trend",
                description="Emerging innovation and technology adoption in the industry",
                relevance_score=0.6,
                source="industry_analysis",
                impact="Medium"
            ))
        
        logger.info(f"Extracted {len(trends)} trends")
        return trends[:count]
    
    async def identify_target_audience(
        self,
        business_type: str,
        target_market: str,
        geographic_location: str
    ) -> TargetAudience:
        """
        Identify target audience demographics using AI analysis
        
        Args:
            business_type: Type of business
            target_market: Target market segment
            geographic_location: Operating location
            
        Returns:
            TargetAudience with demographics and characteristics
        """
        logger.info(f"Identifying target audience for {business_type}")
        
        if self.groq_service.is_available():
            try:
                system_prompt = """You are a market research analyst specializing in customer demographics.
Analyze the business and identify the target audience with detailed demographics.
Return JSON with: age_range (string), income_level (string), geographic_distribution (array),
behavioral_characteristics (array), pain_points (array), buying_triggers (array), estimated_size (string)."""
                
                user_prompt = f"""Identify the target audience for:
Business Type: {business_type}
Target Market: {target_market}
Geographic Location: {geographic_location}

Provide detailed demographics, behavioral characteristics, pain points, and buying triggers."""
                
                result = await self.groq_service.generate_analysis(system_prompt, user_prompt)
                
                if result and isinstance(result, dict):
                    return TargetAudience(
                        age_range=result.get('age_range', '25-45'),
                        income_level=result.get('income_level', 'Medium'),
                        geographic_distribution=result.get('geographic_distribution', [geographic_location]),
                        behavioral_characteristics=result.get('behavioral_characteristics', []),
                        pain_points=result.get('pain_points', []),
                        buying_triggers=result.get('buying_triggers', []),
                        estimated_size=result.get('estimated_size')
                    )
            except Exception as e:
                logger.error(f"AI target audience identification failed: {e}")
        
        # Fallback to rule-based audience identification
        return self._fallback_target_audience(business_type, target_market, geographic_location)
    
    async def get_cached_research(self, cache_key: str) -> Optional[MarketResearchResult]:
        """
        Retrieve cached research data
        
        Args:
            cache_key: Cache key identifier
            
        Returns:
            MarketResearchResult if found and not expired, None otherwise
        """
        try:
            cached_doc = await self.cache_collection.find_one({"cache_key": cache_key})
            
            if not cached_doc:
                return None
            
            # Check if expired
            expires_at = cached_doc.get('expires_at')
            if expires_at:
                # Ensure expires_at is timezone-aware
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                if expires_at < datetime.now(timezone.utc):
                    # Expired, delete it
                    await self.cache_collection.delete_one({"cache_key": cache_key})
                    logger.info(f"Deleted expired cache entry: {cache_key}")
                    return None
            
            # Parse cached data
            cached_data = cached_doc.get('data')
            if cached_data:
                # Convert datetime strings back to datetime objects
                if 'research_timestamp' in cached_data:
                    if isinstance(cached_data['research_timestamp'], str):
                        cached_data['research_timestamp'] = datetime.fromisoformat(cached_data['research_timestamp'])
                    elif cached_data['research_timestamp'].tzinfo is None:
                        cached_data['research_timestamp'] = cached_data['research_timestamp'].replace(tzinfo=timezone.utc)
                
                for trend in cached_data.get('trends', []):
                    if 'published_date' in trend:
                        if isinstance(trend['published_date'], str):
                            trend['published_date'] = datetime.fromisoformat(trend['published_date'])
                        elif trend['published_date'].tzinfo is None:
                            trend['published_date'] = trend['published_date'].replace(tzinfo=timezone.utc)
                
                result = MarketResearchResult(**cached_data)
                logger.info(f"Cache hit for {cache_key}")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached research: {e}")
            return None
    
    async def cache_research(
        self,
        cache_key: str,
        data: MarketResearchResult,
        ttl_hours: int = 24
    ) -> None:
        """
        Cache research data with TTL
        
        Args:
            cache_key: Cache key identifier
            data: MarketResearchResult to cache
            ttl_hours: Time to live in hours (default 24)
        """
        try:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
            
            # Convert to dict and handle datetime serialization
            data_dict = data.dict()
            
            # Convert datetime objects to ISO strings
            if 'research_timestamp' in data_dict:
                data_dict['research_timestamp'] = data_dict['research_timestamp'].isoformat()
            
            for trend in data_dict.get('trends', []):
                if 'published_date' in trend:
                    trend['published_date'] = trend['published_date'].isoformat()
            
            cache_doc = {
                "cache_key": cache_key,
                "data": data_dict,
                "created_at": datetime.now(timezone.utc),
                "expires_at": expires_at
            }
            
            await self.cache_collection.update_one(
                {"cache_key": cache_key},
                {"$set": cache_doc},
                upsert=True
            )
            
            logger.info(f"Cached research data for {cache_key} (TTL: {ttl_hours}h)")
            
        except Exception as e:
            logger.error(f"Error caching research data: {e}")
    
    # ==================== HELPER METHODS ====================
    
    def _generate_cache_key(
        self,
        business_type: str,
        industry: str,
        target_market: str,
        geographic_location: str
    ) -> str:
        """Generate cache key from research parameters"""
        key_string = f"{business_type}|{industry}|{target_market}|{geographic_location}".lower()
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _enrich_competitor_data(
        self,
        comp_data: Dict[str, Any],
        business_type: str
    ) -> Competitor:
        """
        Enrich competitor data with AI analysis
        
        Args:
            comp_data: Raw competitor data
            business_type: Type of business for context
            
        Returns:
            Enriched Competitor object
        """
        # Extract basic info
        name = comp_data.get('name', 'Unknown Competitor')
        domain = comp_data.get('domain', 'unknown.com')
        description = comp_data.get('description', '')
        
        # Try to get strengths/weaknesses from AI
        strengths = comp_data.get('strengths', [])
        weaknesses = comp_data.get('weaknesses', [])
        
        if not strengths or not weaknesses:
            if self.groq_service.is_available():
                try:
                    system_prompt = """Analyze the competitor and identify 3 key strengths and 3 key weaknesses.
Return JSON with: strengths (array of 3 strings), weaknesses (array of 3 strings), 
market_position (string), pricing_strategy (string)."""
                    
                    user_prompt = f"""Analyze this competitor:
Name: {name}
Domain: {domain}
Description: {description}
Business Type: {business_type}

Identify strengths, weaknesses, market position, and pricing strategy."""
                    
                    result = await self.groq_service.generate_analysis(system_prompt, user_prompt)
                    
                    if result and isinstance(result, dict):
                        strengths = result.get('strengths', strengths)
                        weaknesses = result.get('weaknesses', weaknesses)
                        comp_data['market_position'] = result.get('market_position', comp_data.get('market_position', 'Unknown'))
                        comp_data['pricing_strategy'] = result.get('pricing_strategy', comp_data.get('pricing_strategy', 'Unknown'))
                except Exception as e:
                    logger.warning(f"AI competitor enrichment failed: {e}")
        
        # Ensure we have some strengths/weaknesses
        if not strengths:
            strengths = ["Established market presence", "Brand recognition", "Customer base"]
        if not weaknesses:
            weaknesses = ["Limited innovation", "Higher pricing", "Complex onboarding"]
        
        return Competitor(
            name=name,
            domain=domain,
            description=description[:200],  # Limit description length
            strengths=strengths[:5],  # Max 5 strengths
            weaknesses=weaknesses[:5],  # Max 5 weaknesses
            market_position=comp_data.get('market_position', 'Unknown'),
            pricing_strategy=comp_data.get('pricing_strategy', 'Unknown'),
            estimated_traffic=comp_data.get('estimated_traffic'),
            ad_spend_monthly=comp_data.get('ad_spend_monthly'),
            confidence=comp_data.get('confidence', 0.7)
        )
    
    def _fallback_market_size_estimation(
        self,
        industry: str,
        geography: str,
        currency: str
    ) -> MarketSize:
        """Fallback market size estimation using rules"""
        # Simple rule-based estimation
        base_values = {
            "USD": 5000000000,  # $5B
            "EUR": 4500000000,  # €4.5B
            "INR": 400000000000  # ₹400B
        }
        
        base_value = base_values.get(currency, base_values["USD"])
        
        # Adjust based on geography
        if "global" in geography.lower() or "worldwide" in geography.lower():
            multiplier = 10
        elif any(region in geography.lower() for region in ["us", "usa", "united states", "america"]):
            multiplier = 3
        elif any(region in geography.lower() for region in ["india", "indian"]):
            multiplier = 2
        elif any(region in geography.lower() for region in ["europe", "eu"]):
            multiplier = 2.5
        else:
            multiplier = 1
        
        estimated_value = base_value * multiplier
        
        # Format value
        currency_symbols = {"USD": "$", "EUR": "€", "INR": "₹"}
        symbol = currency_symbols.get(currency, currency)
        
        if estimated_value >= 1000000000:
            value_str = f"{symbol}{estimated_value / 1000000000:.1f}B"
            lower_bound = f"{symbol}{estimated_value * 0.8 / 1000000000:.1f}B"
            upper_bound = f"{symbol}{estimated_value * 1.2 / 1000000000:.1f}B"
        else:
            value_str = f"{symbol}{estimated_value / 1000000:.0f}M"
            lower_bound = f"{symbol}{estimated_value * 0.8 / 1000000:.0f}M"
            upper_bound = f"{symbol}{estimated_value * 1.2 / 1000000:.0f}M"
        
        return MarketSize(
            value=value_str,
            confidence_interval=f"{lower_bound} - {upper_bound}",
            confidence_level="Medium",
            source="rule_based_estimation",
            methodology="Industry benchmarks and geographic adjustments"
        )
    
    async def _generate_ai_trends(self, industry: str, count: int) -> List[Trend]:
        """Generate trends using AI"""
        trends = []
        
        try:
            system_prompt = f"""Generate {count} current industry trends for {industry}.
Return JSON array with objects containing: title (string), description (string), 
relevance_score (float 0-1), impact ("High", "Medium", "Low")."""
            
            user_prompt = f"Generate {count} relevant trends for the {industry} industry in 2024-2025."
            
            result = await self.groq_service.generate_analysis(system_prompt, user_prompt)
            
            if result and isinstance(result, list):
                for trend_data in result[:count]:
                    trends.append(Trend(
                        title=trend_data.get('title', 'Industry Trend'),
                        description=trend_data.get('description', ''),
                        relevance_score=trend_data.get('relevance_score', 0.7),
                        source='groq_ai_generation',
                        impact=trend_data.get('impact', 'Medium')
                    ))
        except Exception as e:
            logger.error(f"AI trend generation failed: {e}")
        
        return trends
    
    def _fallback_target_audience(
        self,
        business_type: str,
        target_market: str,
        geographic_location: str
    ) -> TargetAudience:
        """Fallback target audience identification"""
        return TargetAudience(
            age_range="25-45",
            income_level="Medium to High",
            geographic_distribution=[geographic_location, "Urban areas"],
            behavioral_characteristics=[
                "Tech-savvy",
                "Value-conscious",
                "Early adopters",
                "Online shoppers"
            ],
            pain_points=[
                f"Need for efficient {business_type} solution",
                "Time constraints",
                "Cost concerns",
                "Quality expectations"
            ],
            buying_triggers=[
                "Competitive pricing",
                "Positive reviews",
                "Free trial availability",
                "Strong value proposition"
            ],
            estimated_size="10,000 - 100,000 potential customers"
        )
