# Competitor Hijacking Engine Documentation

## Overview

The Competitor Hijacking Engine is a real-time competitor monitoring and counter-strategy generation system that tracks competitor activities and identifies opportunities to outperform them.

## Features

### 1. Competitor Monitoring
- **Add Competitors**: Track competitor websites by URL
- **Real-time Scanning**: Uses APIFY for web scraping competitor data
- **Change Detection**: Monitors website changes and new campaign launches
- **Scheduled Jobs**: Automatic monitoring every 24h (websites) and 6h (ads)

### 2. Metrics Estimation
- Estimated traffic volumes
- Estimated ad spend
- Top keywords tracking
- Domain authority scoring
- Active campaign counting

### 3. Weakness Analysis
- Landing page analysis for conversion bottlenecks
- Identifies specific weaknesses (headlines, CTAs, forms, etc.)
- Confidence scoring for each weakness
- Opportunity identification

### 4. Counter-Strategy Generation
- AI-powered strategy recommendations
- Expected impact estimation
- Difficulty and timeline assessment
- Actionable implementation steps

### 5. Scheduled Monitoring
- Website monitoring: Every 24 hours
- Ad campaign monitoring: Every 6 hours
- Automatic change detection and alerts
- Background job execution using APScheduler

## Architecture

### Core Components

1. **CompetitorHijackingEngine**: Main class handling all competitor operations
2. **APIFY Integration**: Web scraping for real competitor data
3. **Growth Engine Integration**: AI-powered analysis and strategy generation
4. **APScheduler**: Background job scheduling for automated monitoring

### Database Schema

```javascript
// competitors collection
{
  id: "uuid",
  business_id: "uuid",
  name: "Competitor Name",
  domain: "competitor.com",
  url: "https://competitor.com",
  monitoring_since: "ISO8601",
  last_scan: "ISO8601",
  metrics: {
    estimated_traffic: "50K/month",
    estimated_ad_spend: "$5K/month",
    active_campaigns: 2,
    top_keywords: ["keyword1", "keyword2"],
    domain_authority: 55
  },
  changes_detected: [
    {
      type: "website_change|new_ad_campaign",
      detected_at: "ISO8601",
      description: "Description of change",
      impact: "high|medium|low",
      details: {...}
    }
  ],
  weaknesses: [
    {
      element: "headline|cta|form",
      issue: "Specific issue",
      opportunity: "How to exploit",
      confidence: 85
    }
  ],
  strategies: [
    {
      strategy: "Specific strategy",
      expected_impact: "Measurable outcome",
      difficulty: "easy|medium|hard",
      timeline: "Time to implement"
    }
  ],
  website_snapshot: "HTML content",
  ad_campaigns_snapshot: [...]
}
```

## API Methods

### add_competitor(business_id: str, competitor_url: str) -> str
Adds a new competitor to monitor.

**Parameters:**
- `business_id`: ID of the business
- `competitor_url`: URL of competitor website

**Returns:** Competitor ID

**Example:**
```python
competitor_id = await engine.add_competitor(
    'business_123',
    'https://competitor.com'
)
```

### monitor_competitors(business_id: str) -> List[Dict]
Gets all monitored competitors for a business.

**Parameters:**
- `business_id`: ID of the business

**Returns:** List of competitor objects

### detect_changes(competitor_id: str) -> List[Dict]
Detects changes in competitor's website and campaigns.

**Parameters:**
- `competitor_id`: ID of the competitor

**Returns:** List of detected changes

### analyze_landing_page(competitor_id: str, url: str) -> Dict
Analyzes competitor landing page for weaknesses.

**Parameters:**
- `competitor_id`: ID of the competitor
- `url`: URL of landing page to analyze

**Returns:** Analysis with weaknesses

### estimate_metrics(competitor_id: str) -> Dict
Estimates competitor metrics (traffic, ad spend, keywords).

**Parameters:**
- `competitor_id`: ID of the competitor

**Returns:** Estimated metrics

### suggest_counter_strategies(business_id: str, competitor_id: str) -> List[Dict]
Generates counter-strategies to beat a competitor.

**Parameters:**
- `business_id`: ID of the business
- `competitor_id`: ID of the competitor

**Returns:** List of counter-strategies

### start_monitoring() -> None
Starts scheduled monitoring jobs.

### stop_monitoring() -> None
Stops scheduled monitoring jobs.

## Usage Example

```python
from competitor_hijacking_engine import CompetitorHijackingEngine
from growth_engine import GrowthEngine

# Initialize
db = get_database()
growth_engine = GrowthEngine(db, ai_client)
engine = CompetitorHijackingEngine(db, growth_engine)

# Add competitor
competitor_id = await engine.add_competitor(
    business_id='business_123',
    competitor_url='https://competitor.com'
)

# Get all competitors
competitors = await engine.monitor_competitors('business_123')

# Detect changes
changes = await engine.detect_changes(competitor_id)

# Analyze landing page
analysis = await engine.analyze_landing_page(
    competitor_id,
    'https://competitor.com/landing'
)

# Get metrics
metrics = await engine.estimate_metrics(competitor_id)

# Generate strategies
strategies = await engine.suggest_counter_strategies(
    'business_123',
    competitor_id
)

# Start automated monitoring
await engine.start_monitoring()
```

## Testing

### Unit Tests
- 18 unit tests covering all core functionality
- Located in: `backend/test_competitor_hijacking_engine.py`
- Run: `pytest backend/test_competitor_hijacking_engine.py -v`

### Integration Tests
- 5 integration tests covering complete workflows
- Located in: `backend/test_competitor_hijacking_integration.py`
- Run: `pytest backend/test_competitor_hijacking_integration.py -v`

### Test Coverage
- Engine initialization
- Competitor addition and management
- Change detection (website and campaigns)
- Landing page analysis
- Metrics estimation
- Counter-strategy generation
- Scheduled monitoring
- Error handling

## Requirements Validation

### Requirement 6.1: Website Monitoring ✓
- Monitors competitor websites every 24 hours
- Detects content changes and updates

### Requirement 6.2: Ad Campaign Tracking ✓
- Tracks competitor ad campaigns
- Monitors for new campaign launches

### Requirement 6.3: Change Notifications ✓
- Detects changes within monitoring cycles
- Stores change history with timestamps

### Requirement 6.4: Landing Page Analysis ✓
- Analyzes competitor landing pages
- Identifies conversion weaknesses

### Requirement 6.5: Counter-Strategy Generation ✓
- Generates actionable strategies
- Provides expected impact and timeline

### Requirement 6.6: Traffic Estimation ✓
- Estimates competitor traffic volumes
- Tracks traffic trends

### Requirement 6.7: Ad Spend Estimation ✓
- Estimates competitor ad spend
- Monitors spending patterns

### Requirement 6.8: Keyword Tracking ✓
- Identifies competitor keywords
- Tracks keyword rankings

### Requirement 6.9: Multi-Competitor Support ✓
- Tracks at least 5 competitors per business
- Scales to monitor many competitors

## Future Enhancements

1. **Real Ad Library Integration**
   - Facebook Ad Library API
   - Google Ads Transparency Center
   - LinkedIn Ad Library

2. **Advanced Traffic Estimation**
   - SimilarWeb API integration
   - SEMrush API integration
   - Ahrefs API integration

3. **Enhanced Keyword Tracking**
   - Real-time ranking updates
   - Keyword gap analysis
   - Search volume trends

4. **Notification System**
   - Email alerts for critical changes
   - Slack/Discord webhooks
   - In-app notifications

5. **Competitive Intelligence Dashboard**
   - Visual competitor comparison
   - Trend charts and graphs
   - Strategy effectiveness tracking

## Dependencies

- **APScheduler**: Background job scheduling
- **APIFY**: Web scraping and data collection
- **Growth Engine**: AI-powered analysis
- **MongoDB**: Data persistence

## Performance Considerations

- **Caching**: Competitor data cached to reduce API calls
- **Rate Limiting**: Delays between competitor scans to avoid overload
- **Async Operations**: All I/O operations are asynchronous
- **Error Recovery**: Graceful handling of scan failures

## Security Considerations

- **Rate Limiting**: Respects robots.txt and rate limits
- **Data Privacy**: Stores only publicly available data
- **API Security**: Secure storage of API credentials
- **Access Control**: Business-level data isolation
