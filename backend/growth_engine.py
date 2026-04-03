"""
AstraMark Growth Operating System Engine
Advanced autonomous business growth intelligence system
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import json
import hashlib
from groq_service import groq_service
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL
class SimpleCache:
    """Simple in-memory cache with TTL for AI responses"""
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if (datetime.now(timezone.utc) - timestamp).total_seconds() < self.ttl_seconds:
                logger.info(f"Cache hit for key: {key[:50]}...")
                return value
            else:
                # Expired, remove it
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set cached value with current timestamp"""
        self.cache[key] = (value, datetime.now(timezone.utc))
        logger.info(f"Cache set for key: {key[:50]}...")
    
    def clear(self):
        """Clear all cached values"""
        self.cache.clear()
        logger.info("Cache cleared")

class GrowthEngine:
    """
    Core Growth Operating System Engine
    Acts as: CMO + Growth Hacker + Performance Marketer + Data Scientist
    """
    
    def __init__(self, db, ai_client=None):
        self.db = db
        self.ai_client = ai_client
        self.cache = SimpleCache(ttl_seconds=3600)  # 1 hour cache
        
        # Master AI Prompt
        self.master_prompt = """You are AstraMark AI — an advanced autonomous business growth intelligence system designed to replace traditional digital marketing agencies.

Your primary objective is NOT to generate content, but to DRIVE measurable business growth including revenue, leads, conversions, and brand dominance.

You operate as a hybrid of:
- Chief Marketing Officer (CMO)
- Growth Hacker
- Performance Marketer
- Data Scientist
- Sales Funnel Architect

🎯 CORE PRINCIPLE: Always prioritize ROI, speed, and scalability over vanity outputs.

Do NOT behave like a generic AI assistant. Do NOT generate surface-level content without strategy. Every output must connect to measurable business outcomes.

OUTPUT RULES:
- Always structured JSON
- Always actionable (no generic advice)
- Always business-ready
- Clear, Actionable, Structured, Business-focused, Execution-ready

STRICT RULES:
- Avoid generic advice
- Avoid buzzwords without action
- Avoid unnecessary explanations
- Do not act like a chatbot"""
    
    async def generate_daily_actions(self, business_id: str) -> List[Dict[str, Any]]:
        """Generate daily actionable recommendations with expected outcomes"""
        try:
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return []
            
            # Get recent performance data
            recent_analyses = await self.db.analyses.find(
                {'business_id': business_id}
            ).sort('created_at', -1).limit(5).to_list(length=5)
            
            # Build cache key
            cache_key = f"daily_actions:{business_id}:{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            prompt = f"""
Based on this business profile and recent performance, generate 3-5 daily actionable recommendations.

Business: {business.get('business_type')}
Goal: {business.get('primary_goal')}
Budget: {business.get('monthly_budget')}
Recent Analyses: {len(recent_analyses)} available

Return JSON array:
[
  {{
    "action": "Specific action to take",
    "expected_result": "Measurable outcome",
    "roi_score": 85,
    "time_required": "2 hours",
    "priority": "high",
    "channel": "SEO/Ads/Social/Email"
  }}
]

IMPORTANT: Sort actions by roi_score in descending order (highest first).
"""
            
            result = await self._call_ai(prompt)
            
            # Validate and sort by ROI score
            if isinstance(result, list) and len(result) > 0:
                # Ensure all actions have roi_score
                for action in result:
                    if 'roi_score' not in action:
                        action['roi_score'] = 50  # Default medium score
                
                # Sort by ROI score descending
                result.sort(key=lambda x: x.get('roi_score', 0), reverse=True)
                
                # Cache the result
                self.cache.set(cache_key, result)
                return result
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to generate daily actions: {e}", exc_info=True)
            # Return mock data on complete failure
            return self._get_mock_daily_actions(business_id)
    
    async def predict_revenue(self, business_id: str, budget: float, channels: List[str]) -> Dict[str, Any]:
        """Predict revenue based on budget and channel mix"""
        try:
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            # Build cache key
            channels_str = ','.join(sorted(channels))
            cache_key = f"revenue_predict:{business_id}:{budget}:{channels_str}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            prompt = f"""
Calculate expected ROI for this marketing investment.

Business: {business.get('business_type')}
Budget: ₹{budget:,.0f}
Channels: {', '.join(channels)}
Market: {business.get('target_market')}

Return JSON:
{{
  "investment": {budget},
  "expected_revenue_min": <number>,
  "expected_revenue_max": <number>,
  "expected_roi_percentage": <number>,
  "confidence_level": <0-100>,
  "timeline_months": <number>,
  "breakdown_by_channel": {{
    "channel_name": {{"revenue": <number>, "roi": <number>}}
  }},
  "assumptions": ["assumption1", "assumption2"]
}}

IMPORTANT: 
- confidence_level must be between 0 and 100
- Include breakdown for each channel: {', '.join(channels)}
"""
            
            result = await self._call_ai(prompt)
            
            # Validate result
            if isinstance(result, dict) and 'investment' in result:
                # Ensure confidence_level is within bounds
                if 'confidence_level' in result:
                    result['confidence_level'] = max(0, min(100, result['confidence_level']))
                
                # Cache the result
                self.cache.set(cache_key, result)
                return result
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to predict revenue: {e}", exc_info=True)
            # Return mock data on complete failure
            return self._get_mock_revenue_prediction(budget, channels)
    
    async def generate_campaign_assets(self, goal: str, business_id: str) -> Dict[str, Any]:
        """Generate complete campaign assets for 1-click launch"""
        try:
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            # Build cache key
            cache_key = f"campaign_assets:{business_id}:{hashlib.md5(goal.encode()).hexdigest()}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            prompt = f"""
Generate complete campaign assets for: "{goal}"

Business: {business.get('business_type')}
Target: {business.get('target_market')}
Budget: {business.get('monthly_budget')}

Return JSON:
{{
  "campaign_name": "Campaign name",
  "landing_page": {{
    "headline": "Compelling headline",
    "subheadline": "Supporting text",
    "cta_button": "Button text",
    "body_copy": "Main content",
    "social_proof": ["testimonial1", "testimonial2"]
  }},
  "ad_creatives": [
    {{
      "platform": "Google/Facebook",
      "headline": "Ad headline",
      "description": "Ad description",
      "cta": "Call to action"
    }}
  ],
  "email_sequence": [
    {{
      "day": 0,
      "subject": "Email subject",
      "body": "Email content",
      "cta": "Call to action"
    }},
    {{
      "day": 2,
      "subject": "Follow-up subject",
      "body": "Follow-up content",
      "cta": "Call to action"
    }},
    {{
      "day": 5,
      "subject": "Final push subject",
      "body": "Final push content",
      "cta": "Call to action"
    }}
  ],
  "targeting": {{
    "demographics": "Age, location, etc",
    "interests": ["interest1", "interest2"],
    "keywords": ["keyword1", "keyword2"]
  }},
  "budget_allocation": {{
    "ads": 60,
    "content": 20,
    "email": 20
  }}
}}

IMPORTANT: 
- email_sequence must have at least 3 emails
- ad_creatives must have at least 1 creative
- All required fields must be present
"""
            
            result = await self._call_ai(prompt)
            
            # Validate result structure
            if isinstance(result, dict) and self._validate_campaign_assets(result):
                # Cache the result
                self.cache.set(cache_key, result)
                return result
            
            logger.warning("Invalid campaign assets structure, returning empty")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to generate campaign assets: {e}", exc_info=True)
            # Return mock data on complete failure
            return self._get_mock_campaign_assets(goal, business_id)
    
    async def analyze_competitors(self, business_id: str, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze competitors and suggest how to beat them"""
        try:
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            competitor_names = [c.get('name', '') for c in competitors[:5]]
            
            # Build cache key
            cache_key = f"competitor_analysis:{business_id}:{','.join(sorted(competitor_names))}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            prompt = f"""
Analyze these competitors and provide strategies to beat them.

Your Business: {business.get('business_type')}
Competitors: {', '.join(competitor_names)}

Return JSON:
{{
  "competitor_weaknesses": [
    {{
      "competitor": "Name",
      "weakness": "Specific weakness",
      "opportunity": "How to exploit it"
    }}
  ],
  "hijack_strategies": [
    {{
      "strategy": "Specific strategy",
      "expected_impact": "Measurable outcome",
      "difficulty": "easy/medium/hard",
      "timeline": "Time to implement"
    }}
  ],
  "keyword_gaps": ["keyword1", "keyword2"],
  "content_gaps": ["topic1", "topic2"]
}}

IMPORTANT: Provide at least one weakness per competitor and actionable strategies.
"""
            
            result = await self._call_ai(prompt)
            
            # Validate result
            if isinstance(result, dict) and 'competitor_weaknesses' in result:
                # Cache the result
                self.cache.set(cache_key, result)
                return result
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to analyze competitors: {e}", exc_info=True)
            # Return mock data on complete failure
            return self._get_mock_competitor_analysis(competitors)
    
    async def generate_viral_content(self, business_id: str, topic: str, platform: str) -> List[Dict[str, Any]]:
        """Generate viral-optimized content"""
        try:
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return []
            
            # Build cache key
            cache_key = f"viral_content:{business_id}:{hashlib.md5(f'{topic}:{platform}'.encode()).hexdigest()}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            prompt = f"""
Generate 5 viral-optimized {platform} posts about: {topic}

Business: {business.get('business_type')}
Target: {business.get('target_market')}

Return JSON array:
[
  {{
    "content": "Post text",
    "virality_score": 85,
    "hashtags": ["tag1", "tag2"],
    "best_time": "9:00 AM",
    "psychological_trigger": "FOMO/Curiosity/Social Proof",
    "expected_engagement": "500+ likes"
  }}
]

IMPORTANT:
- Generate exactly 5 variations
- virality_score must be between 0 and 100
- Include psychological_trigger for each post
"""
            
            result = await self._call_ai(prompt)
            
            # Validate and ensure virality scores are within bounds
            if isinstance(result, list) and len(result) > 0:
                for post in result:
                    if 'virality_score' in post:
                        post['virality_score'] = max(0, min(100, post['virality_score']))
                
                # Cache the result
                self.cache.set(cache_key, result)
                return result
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to generate viral content: {e}", exc_info=True)
            # Return mock data on complete failure
            return self._get_mock_viral_content(topic, platform)
    
    async def optimize_conversion(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and optimize conversion rates"""
        try:
            # Build cache key from page data
            page_str = json.dumps(page_data, sort_keys=True)
            cache_key = f"conversion_optimize:{hashlib.md5(page_str.encode()).hexdigest()}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            prompt = f"""
Analyze this landing page and suggest conversion optimizations.

Current Data: {json.dumps(page_data)}

Return JSON:
{{
  "current_conversion_rate": <number>,
  "industry_benchmark": <number>,
  "bottlenecks": [
    {{
      "element": "headline/cta/form",
      "issue": "Specific issue",
      "impact": "high/medium/low"
    }}
  ],
  "optimizations": [
    {{
      "element": "headline/cta/form",
      "current": "Current version",
      "suggested": "Optimized version",
      "expected_lift": "+15%",
      "reasoning": "Why this will improve"
    }}
  ],
  "ab_test_variations": [
    {{
      "variation_name": "Test A",
      "changes": ["change1", "change2"],
      "expected_winner_probability": 65
    }}
  ]
}}

IMPORTANT: Provide specific, actionable optimizations with expected impact.
"""
            
            result = await self._call_ai(prompt)
            
            # Validate result
            if isinstance(result, dict) and 'bottlenecks' in result:
                # Cache the result
                self.cache.set(cache_key, result)
                return result
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to optimize conversion: {e}", exc_info=True)
            # Return mock data on complete failure
            return self._get_mock_conversion_optimization(page_data)
    
    async def create_lead_funnel(self, business_id: str, goal: str) -> Dict[str, Any]:
        """Create automated lead funnel"""
        try:
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            # Build cache key
            cache_key = f"lead_funnel:{business_id}:{hashlib.md5(goal.encode()).hexdigest()}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            prompt = f"""
Design a complete lead funnel for: {goal}

Business: {business.get('business_type')}
Target: {business.get('target_market')}

Return JSON:
{{
  "funnel_stages": [
    {{
      "stage": "Awareness/Interest/Decision/Action",
      "tactics": ["tactic1", "tactic2"],
      "content": ["content1", "content2"],
      "expected_conversion": "20%"
    }}
  ],
  "email_automation": [
    {{
      "trigger": "Lead enters funnel",
      "delay_days": 0,
      "subject": "Email subject",
      "content": "Email body",
      "goal": "Move to next stage"
    }}
  ],
  "lead_scoring": {{
    "criteria": ["action1: +10 points", "action2: +5 points"],
    "hot_lead_threshold": 50,
    "cold_lead_threshold": 20
  }}
}}

IMPORTANT: Include all 4 funnel stages (Awareness, Interest, Decision, Action).
"""
            
            result = await self._call_ai(prompt)
            
            # Validate result
            if isinstance(result, dict) and 'funnel_stages' in result:
                # Cache the result
                self.cache.set(cache_key, result)
                return result
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to create lead funnel: {e}", exc_info=True)
            # Return mock data on complete failure
            return self._get_mock_lead_funnel(goal)
    
    async def _call_ai(self, prompt: str) -> Any:
        """Call AI service with master prompt and fallback chain: Groq → Gemini → Mock"""
        errors = []
        
        # Try Groq first (Primary)
        if groq_service.is_available():
            try:
                logger.info("Attempting AI call with Groq (Primary)")
                response = groq_service.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": self.master_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                logger.info("AI call successful with Groq")
                return result
            except Exception as e:
                error_msg = f"Groq failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # Fallback to Gemini (Secondary)
        if self.ai_client:
            try:
                logger.info("Falling back to Gemini")
                model = self.ai_client.GenerativeModel(
                    model_name="gemini-2.0-flash-exp",
                    generation_config={
                        "temperature": 0.7,
                        "response_mime_type": "application/json"
                    },
                    system_instruction=self.master_prompt
                )
                response = await model.generate_content_async(prompt)
                
                # Clean up response
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                result = json.loads(response_text)
                logger.info("AI call successful with Gemini")
                return result
            except Exception as e:
                error_msg = f"Gemini failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # All AI services failed
        logger.error(f"All AI services failed. Errors: {'; '.join(errors)}")
        return {}
    
    def _validate_campaign_assets(self, assets: Dict[str, Any]) -> bool:
        """Validate campaign assets structure"""
        required_keys = ['landing_page', 'ad_creatives', 'email_sequence', 'targeting', 'budget_allocation']
        
        # Check all required keys exist
        if not all(key in assets for key in required_keys):
            return False
        
        # Validate email sequence has at least 3 emails
        if not isinstance(assets['email_sequence'], list) or len(assets['email_sequence']) < 3:
            return False
        
        # Validate ad_creatives has at least 1 creative
        if not isinstance(assets['ad_creatives'], list) or len(assets['ad_creatives']) < 1:
            return False
        
        return True
    
    # Mock data methods for fallback
    def _get_mock_daily_actions(self, business_id: str) -> List[Dict[str, Any]]:
        """Return mock daily actions when AI services fail"""
        return [
            {
                "action": "Optimize top-performing content for SEO",
                "expected_result": "15-20% increase in organic traffic",
                "roi_score": 85,
                "time_required": "2 hours",
                "priority": "high",
                "channel": "SEO"
            },
            {
                "action": "Launch retargeting campaign for website visitors",
                "expected_result": "10-15% conversion rate on retargeted users",
                "roi_score": 78,
                "time_required": "3 hours",
                "priority": "high",
                "channel": "Ads"
            },
            {
                "action": "Create and schedule 5 social media posts",
                "expected_result": "500+ engagements, 50+ profile visits",
                "roi_score": 65,
                "time_required": "1 hour",
                "priority": "medium",
                "channel": "Social"
            }
        ]
    
    def _get_mock_revenue_prediction(self, budget: float, channels: List[str]) -> Dict[str, Any]:
        """Return mock revenue prediction when AI services fail"""
        # Simple calculation: 1.5x to 2.5x ROI
        min_revenue = budget * 1.5
        max_revenue = budget * 2.5
        
        breakdown = {}
        per_channel = budget / len(channels) if channels else budget
        for channel in channels:
            breakdown[channel] = {
                "revenue": per_channel * 2.0,
                "roi": 2.0
            }
        
        return {
            "investment": budget,
            "expected_revenue_min": min_revenue,
            "expected_revenue_max": max_revenue,
            "expected_roi_percentage": 150,
            "confidence_level": 70,
            "timeline_months": 3,
            "breakdown_by_channel": breakdown,
            "assumptions": [
                "Based on industry averages",
                "Assumes consistent execution",
                "Market conditions remain stable"
            ]
        }
    
    def _get_mock_campaign_assets(self, goal: str, business_id: str) -> Dict[str, Any]:
        """Return mock campaign assets when AI services fail"""
        return {
            "campaign_name": f"Growth Campaign: {goal}",
            "landing_page": {
                "headline": f"Achieve Your Goal: {goal}",
                "subheadline": "Join thousands of successful businesses",
                "cta_button": "Get Started Now",
                "body_copy": "Transform your business with our proven strategies and tools.",
                "social_proof": [
                    "Trusted by 10,000+ businesses",
                    "4.8/5 average rating"
                ]
            },
            "ad_creatives": [
                {
                    "platform": "Google",
                    "headline": f"Ready to {goal}?",
                    "description": "Start your journey today with our expert guidance",
                    "cta": "Learn More"
                },
                {
                    "platform": "Facebook",
                    "headline": f"Transform Your Business",
                    "description": f"Achieve {goal} faster with proven strategies",
                    "cta": "Get Started"
                }
            ],
            "email_sequence": [
                {
                    "day": 0,
                    "subject": f"Welcome! Let's achieve {goal} together",
                    "body": "Thank you for joining us. Here's what to expect...",
                    "cta": "View Your Dashboard"
                },
                {
                    "day": 2,
                    "subject": "Quick wins to get started",
                    "body": "Here are 3 actionable steps you can take today...",
                    "cta": "Take Action"
                },
                {
                    "day": 5,
                    "subject": "Success stories from businesses like yours",
                    "body": "See how others achieved their goals...",
                    "cta": "Read Case Studies"
                }
            ],
            "targeting": {
                "demographics": "Business owners, 25-55, urban areas",
                "interests": ["business growth", "marketing", "entrepreneurship"],
                "keywords": ["business growth", "marketing strategy", "increase revenue"]
            },
            "budget_allocation": {
                "ads": 60,
                "content": 25,
                "email": 15
            }
        }
    
    def _get_mock_competitor_analysis(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Return mock competitor analysis when AI services fail"""
        competitor_names = [c.get('name', 'Competitor') for c in competitors[:3]]
        
        return {
            "competitor_weaknesses": [
                {
                    "competitor": competitor_names[0] if competitor_names else "Competitor A",
                    "weakness": "Limited social media presence",
                    "opportunity": "Dominate social channels with consistent, engaging content"
                }
            ],
            "hijack_strategies": [
                {
                    "strategy": "Target their high-value keywords with better content",
                    "expected_impact": "Capture 10-15% of their organic traffic",
                    "difficulty": "medium",
                    "timeline": "2-3 months"
                },
                {
                    "strategy": "Offer superior customer experience and support",
                    "expected_impact": "Convert their dissatisfied customers",
                    "difficulty": "easy",
                    "timeline": "1 month"
                }
            ],
            "keyword_gaps": ["industry-specific terms", "long-tail keywords"],
            "content_gaps": ["how-to guides", "case studies", "comparison content"]
        }
    
    def _get_mock_viral_content(self, topic: str, platform: str) -> List[Dict[str, Any]]:
        """Return mock viral content when AI services fail"""
        return [
            {
                "content": f"🚀 The secret to {topic} that nobody talks about... (Thread)",
                "virality_score": 85,
                "hashtags": ["#growth", "#marketing", "#business"],
                "best_time": "9:00 AM",
                "psychological_trigger": "Curiosity",
                "expected_engagement": "500+ likes, 100+ shares"
            },
            {
                "content": f"I spent 6 months mastering {topic}. Here's what I learned 👇",
                "virality_score": 82,
                "hashtags": ["#entrepreneur", "#success"],
                "best_time": "2:00 PM",
                "psychological_trigger": "Social Proof",
                "expected_engagement": "400+ likes, 80+ shares"
            },
            {
                "content": f"⚠️ Stop doing {topic} wrong! Here's the right way...",
                "virality_score": 78,
                "hashtags": ["#tips", "#advice"],
                "best_time": "11:00 AM",
                "psychological_trigger": "FOMO",
                "expected_engagement": "350+ likes, 70+ shares"
            },
            {
                "content": f"The {topic} framework that 10X'd our results 📈",
                "virality_score": 75,
                "hashtags": ["#strategy", "#results"],
                "best_time": "4:00 PM",
                "psychological_trigger": "Curiosity",
                "expected_engagement": "300+ likes, 60+ shares"
            },
            {
                "content": f"Unpopular opinion: Most people get {topic} completely wrong",
                "virality_score": 72,
                "hashtags": ["#truth", "#reality"],
                "best_time": "7:00 PM",
                "psychological_trigger": "Controversy",
                "expected_engagement": "250+ likes, 50+ shares"
            }
        ]
    
    def _get_mock_conversion_optimization(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return mock conversion optimization when AI services fail"""
        return {
            "current_conversion_rate": 0.025,
            "industry_benchmark": 0.035,
            "bottlenecks": [
                {
                    "element": "headline",
                    "issue": "Not benefit-focused enough",
                    "impact": "high"
                },
                {
                    "element": "cta_button",
                    "issue": "Weak call-to-action text",
                    "impact": "medium"
                }
            ],
            "optimizations": [
                {
                    "element": "headline",
                    "current": "Welcome to Our Service",
                    "suggested": "Save 10 Hours Per Week with Automated Marketing",
                    "expected_lift": "+25%",
                    "reasoning": "Specific value proposition with quantifiable benefit"
                },
                {
                    "element": "cta_button",
                    "current": "Learn More",
                    "suggested": "Start Free Trial",
                    "expected_lift": "+15%",
                    "reasoning": "Action-oriented with low commitment"
                }
            ],
            "ab_test_variations": [
                {
                    "variation_name": "Benefit-Focused",
                    "changes": ["headline", "subheadline"],
                    "expected_winner_probability": 65
                },
                {
                    "variation_name": "Social Proof Heavy",
                    "changes": ["testimonials", "trust_badges"],
                    "expected_winner_probability": 55
                }
            ]
        }
    
    def _get_mock_lead_funnel(self, goal: str) -> Dict[str, Any]:
        """Return mock lead funnel when AI services fail"""
        return {
            "funnel_stages": [
                {
                    "stage": "Awareness",
                    "tactics": ["Content marketing", "SEO", "Social media"],
                    "content": ["Blog posts", "Infographics", "Videos"],
                    "expected_conversion": "20%"
                },
                {
                    "stage": "Interest",
                    "tactics": ["Lead magnet", "Webinar", "Email nurture"],
                    "content": ["Ebook", "Case studies", "Product demo"],
                    "expected_conversion": "40%"
                },
                {
                    "stage": "Decision",
                    "tactics": ["Free trial", "Consultation", "Comparison guide"],
                    "content": ["ROI calculator", "Testimonials", "Pricing page"],
                    "expected_conversion": "30%"
                },
                {
                    "stage": "Action",
                    "tactics": ["Limited offer", "Onboarding", "Success stories"],
                    "content": ["Signup form", "Welcome email", "Quick start guide"],
                    "expected_conversion": "50%"
                }
            ],
            "email_automation": [
                {
                    "trigger": "Lead enters funnel",
                    "delay_days": 0,
                    "subject": f"Welcome! Let's achieve {goal}",
                    "content": "Thank you for your interest. Here's your free guide...",
                    "goal": "Move to Interest stage"
                },
                {
                    "trigger": "Downloaded lead magnet",
                    "delay_days": 2,
                    "subject": "How others achieved success",
                    "content": "Here are 3 case studies from businesses like yours...",
                    "goal": "Build trust and credibility"
                },
                {
                    "trigger": "Viewed pricing page",
                    "delay_days": 1,
                    "subject": "Questions about getting started?",
                    "content": "I noticed you checked out our pricing. Any questions?",
                    "goal": "Address objections"
                }
            ],
            "lead_scoring": {
                "criteria": [
                    "Email open: +5 points",
                    "Link click: +10 points",
                    "Page visit: +15 points",
                    "Form submission: +25 points",
                    "Demo request: +50 points"
                ],
                "hot_lead_threshold": 75,
                "cold_lead_threshold": 20
            }
        }

# Global instance
growth_engine = None
