"""
Groq AI Service - Fallback for Gemini
"""
import json
import logging
from typing import Dict, Any, Optional
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)

class GroqService:
    """Groq AI service for chat completions"""
    
    def __init__(self):
        self.client = None
        if settings.groq_api_key:
            try:
                # Initialize Groq client with minimal parameters for compatibility
                self.client = Groq(api_key=settings.groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
        else:
            logger.warning("GROQ_API_KEY not found")
    
    def is_available(self) -> bool:
        """Check if Groq service is available"""
        return self.client is not None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        reraise=True
    )
    async def generate_analysis(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate analysis using Groq"""
        if not self.is_available():
            raise Exception("Groq service not available")
        
        try:
            # Enhanced prompt to ensure proper JSON format
            enhanced_user_prompt = f"""
{user_prompt}

CRITICAL FORMATTING REQUIREMENTS:
- ALL string fields must be single strings, NOT arrays
- market_analysis.entry_barriers must be a single descriptive string
- market_analysis.market_size must be a single string
- market_analysis.growth_rate must be a single string
- Arrays are only allowed for: opportunities, risks, strengths, weaknesses, pain_points, buying_triggers, objections, content_ideas
- Return ONLY valid JSON, no markdown formatting
"""
            
            # Use Llama 3.3 70B model for best results
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON response
            try:
                analysis_data = json.loads(response_text)
                
                # Additional validation and cleanup
                if 'market_analysis' in analysis_data:
                    ma = analysis_data['market_analysis']
                    # Ensure string fields are strings
                    for field in ['market_size', 'growth_rate', 'entry_barriers']:
                        if isinstance(ma.get(field), list):
                            ma[field] = ', '.join(ma[field])
                        elif ma.get(field) is None:
                            ma[field] = "Not specified"
                
                logger.info("Groq analysis generated successfully")
                return analysis_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Groq JSON response: {e}")
                logger.error(f"Raw response: {response_text[:500]}...")
                raise Exception(f"Invalid JSON response from Groq: {str(e)}")
                
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise Exception(f"Groq analysis failed: {str(e)}")
    
    def get_available_models(self) -> list:
        """Get list of available Groq models"""
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile", 
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]

# Global Groq service instance
groq_service = GroqService()