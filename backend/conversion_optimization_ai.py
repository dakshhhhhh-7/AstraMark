"""
Conversion Optimization AI
Analyzes landing pages and automatically optimizes conversion rates
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import uuid
from groq_service import groq_service
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Industry benchmark conversion rates by type
INDUSTRY_BENCHMARKS = {
    'SaaS': 0.03,
    'E-commerce': 0.025,
    'B2B': 0.02,
    'Agency': 0.015,
    'default': 0.025
}

# Optimization elements
OPTIMIZATION_ELEMENTS = [
    'headline',
    'subheadline',
    'cta_button',
    'form_fields',
    'social_proof',
    'page_layout',
    'loading_speed',
    'mobile_responsiveness'
]

class ConversionOptimizationAI:
    """AI-driven conversion rate optimization"""
    
    def __init__(self, db, ai_client=None):
        self.db = db
        self.ai_client = ai_client
        
        # Master prompt for conversion optimization
        self.optimization_prompt = """You are a conversion rate optimization expert with deep expertise in:
- Landing page psychology
- A/B testing methodology
- User experience design
- Persuasive copywriting
- Data-driven optimization

Your goal is to identify conversion bottlenecks and provide actionable optimizations that increase conversion rates.

Always return structured JSON with specific, measurable recommendations."""
    
    async def analyze_page(self, page_url: str, business_id: str) -> Dict[str, Any]:
        """Analyze landing page and identify optimization opportunities"""
        try:
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            # Get page data (in production, this would scrape the page)
            page_data = await self._get_page_data(page_url)
            
            # Get industry benchmark
            business_type = business.get('business_type', 'default')
            benchmark = INDUSTRY_BENCHMARKS.get(business_type, INDUSTRY_BENCHMARKS['default'])
            
            prompt = f"""
Analyze this landing page and provide conversion optimization recommendations:

Page URL: {page_url}
Business Type: {business_type}
Industry Benchmark: {benchmark * 100}%
Page Data: {json.dumps(page_data)}

Return JSON:
{{
  "current_conversion_rate": <number>,
  "industry_benchmark": {benchmark},
  "bottlenecks": [
    {{
      "element": "headline|cta_button|form|social_proof|layout",
      "issue": "Specific issue description",
      "impact": "high|medium|low",
      "confidence": <0-100>
    }}
  ],
  "optimizations": [
    {{
      "element": "headline|cta_button|form|social_proof|layout",
      "current": "Current version",
      "suggested": "Optimized version",
      "expected_lift": "+25%",
      "reasoning": "Why this will improve conversions"
    }}
  ],
  "ab_test_variations": [
    {{
      "variation_name": "Test Name",
      "changes": ["change1", "change2"],
      "expected_winner_probability": <0-100>
    }}
  ]
}}

IMPORTANT: Provide specific, actionable optimizations with expected impact.
"""
            
            result = await self._call_ai(prompt)
            
            # Validate and enhance result
            if isinstance(result, dict):
                # Ensure benchmark is set
                if 'industry_benchmark' not in result:
                    result['industry_benchmark'] = benchmark
                
                # Validate confidence scores
                if 'bottlenecks' in result:
                    for bottleneck in result['bottlenecks']:
                        if 'confidence' in bottleneck:
                            bottleneck['confidence'] = max(0, min(100, bottleneck['confidence']))
                
                # Validate winner probabilities
                if 'ab_test_variations' in result:
                    for variation in result['ab_test_variations']:
                        if 'expected_winner_probability' in variation:
                            variation['expected_winner_probability'] = max(0, min(100, variation['expected_winner_probability']))
                
                # Check if result has required fields, otherwise fallback
                if 'bottlenecks' in result and 'optimizations' in result:
                    return result
            
            # Fallback to mock data if AI returns incomplete result
            return self._get_mock_analysis(page_url, business_id)
            
        except Exception as e:
            logger.error(f"Failed to analyze page: {e}", exc_info=True)
            return self._get_mock_analysis(page_url, business_id)
    
    async def identify_bottlenecks(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific conversion bottlenecks"""
        try:
            bottlenecks = []
            
            # Check headline
            if 'headline' in page_data:
                headline = page_data['headline']
                if len(headline) > 100:
                    bottlenecks.append({
                        'element': 'headline',
                        'issue': 'Headline too long, loses impact',
                        'impact': 'high',
                        'confidence': 85
                    })
                elif not any(word in headline.lower() for word in ['save', 'get', 'increase', 'reduce', 'improve']):
                    bottlenecks.append({
                        'element': 'headline',
                        'issue': 'Headline not benefit-focused',
                        'impact': 'high',
                        'confidence': 80
                    })
            
            # Check CTA button
            if 'cta_button' in page_data:
                cta = page_data['cta_button']
                weak_ctas = ['submit', 'click here', 'learn more', 'continue']
                if any(weak in cta.lower() for weak in weak_ctas):
                    bottlenecks.append({
                        'element': 'cta_button',
                        'issue': 'Weak call-to-action text',
                        'impact': 'medium',
                        'confidence': 75
                    })
            
            # Check form fields
            if 'form_fields' in page_data:
                fields = page_data['form_fields']
                if isinstance(fields, list) and len(fields) > 5:
                    bottlenecks.append({
                        'element': 'form_fields',
                        'issue': 'Too many form fields, increases friction',
                        'impact': 'high',
                        'confidence': 90
                    })
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Failed to identify bottlenecks: {e}")
            return []
    
    async def generate_variations(self, element: str, current: str, count: int = 3) -> List[Dict[str, Any]]:
        """Generate A/B test variations for an element"""
        try:
            prompt = f"""
Generate {count} A/B test variations for this {element}:

Current: {current}

Return JSON array:
[
  {{
    "variation": "Variation text",
    "reasoning": "Why this might perform better",
    "expected_lift": "+15%"
  }}
]

Each variation should:
- Be significantly different from the original
- Apply conversion optimization principles
- Be testable and measurable
"""
            
            result = await self._call_ai(prompt)
            
            if isinstance(result, list) and len(result) > 0:
                return result
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to generate variations: {e}")
            return []
    
    async def run_ab_test(self, page_id: str, variations: List[Dict[str, Any]]) -> str:
        """Start an A/B test with variations"""
        try:
            test_id = str(uuid.uuid4())
            
            # Create A/B test record
            ab_test = {
                'id': test_id,
                'page_id': page_id,
                'variations': variations,
                'status': 'running',
                'started_at': datetime.now(timezone.utc).isoformat(),
                'traffic_split': self._calculate_traffic_split(len(variations)),
                'results': {
                    'control': {'visitors': 0, 'conversions': 0, 'rate': 0},
                    'variations': [{
                        'name': v.get('variation_name', f'Variation {i+1}'),
                        'visitors': 0,
                        'conversions': 0,
                        'rate': 0
                    } for i, v in enumerate(variations)]
                },
                'winner': None,
                'statistical_significance': 0
            }
            
            # Save to database
            await self.db.ab_tests.insert_one(ab_test.copy())
            
            logger.info(f"A/B test {test_id} started for page {page_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"Failed to start A/B test: {e}")
            raise
    
    async def implement_winner(self, test_id: str) -> bool:
        """Automatically implement winning variation after statistical significance"""
        try:
            # Get A/B test
            ab_test = await self.db.ab_tests.find_one({'id': test_id})
            if not ab_test:
                logger.error(f"A/B test {test_id} not found")
                return False
            
            # Check statistical significance
            if ab_test.get('statistical_significance', 0) < 95:
                logger.warning(f"A/B test {test_id} has not reached statistical significance")
                return False
            
            # Get winner
            winner = ab_test.get('winner')
            if not winner:
                logger.error(f"No winner determined for A/B test {test_id}")
                return False
            
            # Implement winner (in production, this would update the actual page)
            page_id = ab_test.get('page_id')
            
            # Update page with winning variation
            await self.db.pages.update_one(
                {'id': page_id},
                {
                    '$set': {
                        'current_version': winner,
                        'updated_at': datetime.now(timezone.utc).isoformat(),
                        'updated_by': 'conversion_ai'
                    }
                }
            )
            
            # Mark test as completed
            await self.db.ab_tests.update_one(
                {'id': test_id},
                {
                    '$set': {
                        'status': 'completed',
                        'completed_at': datetime.now(timezone.utc).isoformat(),
                        'implemented': True
                    }
                }
            )
            
            logger.info(f"Winner implemented for A/B test {test_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to implement winner: {e}")
            return False
    
    async def track_conversion_rate(self, page_id: str, traffic_source: Optional[str] = None) -> float:
        """Track conversion rate for a page"""
        try:
            # Get page analytics
            query = {'page_id': page_id}
            if traffic_source:
                query['traffic_source'] = traffic_source
            
            analytics = await self.db.page_analytics.find_one(query)
            
            if not analytics:
                return 0.0
            
            visitors = analytics.get('visitors', 0)
            conversions = analytics.get('conversions', 0)
            
            if visitors == 0:
                return 0.0
            
            return conversions / visitors
            
        except Exception as e:
            logger.error(f"Failed to track conversion rate: {e}")
            return 0.0
    
    def _calculate_traffic_split(self, num_variations: int) -> Dict[str, float]:
        """Calculate traffic split for A/B test"""
        # Equal split between control and variations
        total_groups = num_variations + 1  # +1 for control
        split_percentage = 100 / total_groups
        
        return {
            'control': split_percentage,
            'variations': [split_percentage] * num_variations
        }
    
    async def _get_page_data(self, page_url: str) -> Dict[str, Any]:
        """Get page data (mock for now, would scrape in production)"""
        # In production, this would use a web scraping service
        return {
            'url': page_url,
            'headline': 'Welcome to Our Service',
            'subheadline': 'Get started today',
            'cta_button': 'Learn More',
            'form_fields': ['name', 'email', 'company', 'phone', 'message'],
            'social_proof': ['Trusted by 1000+ companies'],
            'has_testimonials': False,
            'loading_speed': 3.5,  # seconds
            'mobile_responsive': True
        }
    
    async def _call_ai(self, prompt: str) -> Any:
        """Call AI service with fallback chain: Groq → Gemini → Mock"""
        errors = []
        
        # Try Groq first (Primary)
        if groq_service.is_available():
            try:
                logger.info("Attempting AI call with Groq (Primary)")
                response = groq_service.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": self.optimization_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                logger.info("AI call successful with Groq")
                
                # Extract array if wrapped in object
                if isinstance(result, dict) and 'variations' in result:
                    return result['variations']
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
                    system_instruction=self.optimization_prompt
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
                
                # Extract array if wrapped in object
                if isinstance(result, dict) and 'variations' in result:
                    return result['variations']
                return result
            except Exception as e:
                error_msg = f"Gemini failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # All AI services failed
        logger.error(f"All AI services failed. Errors: {'; '.join(errors)}")
        return {}
    
    def _get_mock_analysis(self, page_url: str, business_id: str) -> Dict[str, Any]:
        """Return mock analysis when AI services fail"""
        return {
            "current_conversion_rate": 0.025,
            "industry_benchmark": 0.035,
            "bottlenecks": [
                {
                    "element": "headline",
                    "issue": "Not benefit-focused enough",
                    "impact": "high",
                    "confidence": 85
                },
                {
                    "element": "cta_button",
                    "issue": "Weak call-to-action text",
                    "impact": "medium",
                    "confidence": 75
                },
                {
                    "element": "form_fields",
                    "issue": "Too many fields increase friction",
                    "impact": "high",
                    "confidence": 90
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
                },
                {
                    "element": "form_fields",
                    "current": "5 fields",
                    "suggested": "3 fields (name, email, company)",
                    "expected_lift": "+20%",
                    "reasoning": "Reduce friction by removing unnecessary fields"
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

# Global instance
conversion_optimization_ai = None
