"""
Viral Content Engine
Generates viral-optimized content with psychological triggers and virality scoring
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, time
import json
import hashlib
from groq_service import groq_service
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Viral patterns and psychological triggers
VIRAL_PATTERNS = {
    'FOMO': [
        "Only {time} left...",
        "Limited spots available...",
        "Don't miss out on...",
        "Last chance to..."
    ],
    'Curiosity': [
        "The one thing nobody tells you about...",
        "What happened next will surprise you...",
        "The secret to...",
        "You won't believe..."
    ],
    'Social Proof': [
        "{number}+ businesses use this...",
        "Trusted by industry leaders...",
        "Join {number} successful...",
        "Recommended by experts..."
    ],
    'Controversy': [
        "Unpopular opinion:",
        "Everyone is wrong about...",
        "Stop doing {topic} wrong...",
        "The truth about..."
    ],
    'Storytelling': [
        "I spent {time} learning...",
        "Here's what happened when...",
        "My journey to...",
        "How I went from..."
    ],
    'Data-Driven': [
        "{percentage}% of people don't know...",
        "Studies show...",
        "The data reveals...",
        "{number} proven ways to..."
    ]
}

# Platform-specific optimal posting times (24-hour format)
OPTIMAL_POSTING_TIMES = {
    'LinkedIn': [(9, 0), (12, 0), (17, 0)],  # 9 AM, 12 PM, 5 PM
    'Twitter': [(8, 0), (12, 0), (18, 0)],   # 8 AM, 12 PM, 6 PM
    'Instagram': [(11, 0), (14, 0), (19, 0)], # 11 AM, 2 PM, 7 PM
    'TikTok': [(7, 0), (16, 0), (21, 0)],    # 7 AM, 4 PM, 9 PM
    'Facebook': [(9, 0), (13, 0), (19, 0)]   # 9 AM, 1 PM, 7 PM
}

class ViralContentEngine:
    """Generate viral-optimized content with psychological triggers"""
    
    def __init__(self, db, ai_client=None):
        self.db = db
        self.ai_client = ai_client
        
        # Master prompt for viral content
        self.viral_prompt = """You are a viral content strategist specializing in creating highly engaging social media content.

Your goal is to create content that:
- Captures attention immediately
- Triggers emotional responses
- Encourages sharing and engagement
- Uses proven psychological patterns
- Optimized for specific platforms

Always return structured JSON with virality scores and psychological triggers."""
    
    async def generate_posts(
        self, 
        business_id: str, 
        topic: str, 
        platform: str, 
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate viral-optimized posts for a specific platform"""
        try:
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return []
            
            prompt = f"""
Generate {count} viral-optimized {platform} posts about: {topic}

Business: {business.get('business_type')}
Target Audience: {business.get('target_market')}

Return JSON array:
[
  {{
    "content": "Post text with emojis and formatting",
    "virality_score": 85,
    "hashtags": ["#tag1", "#tag2", "#tag3"],
    "best_time": "9:00 AM",
    "psychological_trigger": "FOMO|Curiosity|Social Proof|Controversy|Storytelling|Data-Driven",
    "expected_engagement": "500+ likes, 50+ shares",
    "content_type": "text|image_caption|video_script",
    "platform_specific_tips": "Platform-specific optimization advice"
  }}
]

IMPORTANT:
- Generate exactly {count} variations
- virality_score must be between 0 and 100
- Include psychological_trigger for each post
- Optimize for {platform} format and audience
- Use emojis and formatting appropriate for {platform}
"""
            
            result = await self._call_ai(prompt)
            
            # Validate and ensure virality scores are within bounds
            if isinstance(result, list) and len(result) > 0:
                for post in result:
                    if 'virality_score' in post:
                        post['virality_score'] = max(0, min(100, post['virality_score']))
                    else:
                        post['virality_score'] = 50  # Default medium score
                    
                    # Ensure required fields
                    if 'psychological_trigger' not in post:
                        post['psychological_trigger'] = 'Curiosity'
                    if 'hashtags' not in post:
                        post['hashtags'] = []
                    if 'best_time' not in post:
                        post['best_time'] = self.suggest_posting_time(business_id, platform)
                
                return result
            
            # Fallback to mock data if AI returns empty
            return self._get_mock_viral_posts(topic, platform, count)
            
        except Exception as e:
            logger.error(f"Failed to generate viral posts: {e}", exc_info=True)
            return self._get_mock_viral_posts(topic, platform, count)
    
    def score_virality(self, content: str, platform: str) -> int:
        """Calculate virality score for content"""
        try:
            score = 50  # Base score
            
            # Check for psychological triggers
            content_lower = content.lower()
            for trigger, patterns in VIRAL_PATTERNS.items():
                for pattern in patterns:
                    pattern_check = pattern.split('{')[0].lower().strip()
                    if pattern_check and pattern_check in content_lower:
                        score += 10
                        break
            
            # Check for emojis
            emoji_count = sum(1 for char in content if ord(char) > 127000)
            score += min(emoji_count * 2, 10)
            
            # Check for hashtags
            hashtag_count = content.count('#')
            score += min(hashtag_count * 3, 10)
            
            # Check for questions
            if '?' in content:
                score += 5
            
            # Check for numbers/data
            if any(char.isdigit() for char in content):
                score += 5
            
            # Platform-specific adjustments
            if platform.lower() == 'twitter' and len(content) <= 280:
                score += 5
            elif platform.lower() == 'linkedin' and len(content) > 500:
                score += 5
            elif platform.lower() == 'tiktok' and 'video' in content.lower():
                score += 10
            
            # Clamp to 0-100
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Failed to score virality: {e}")
            return 50
    
    def suggest_posting_time(self, business_id: str, platform: str) -> str:
        """Suggest optimal posting time for platform"""
        try:
            # Get platform-specific times
            times = OPTIMAL_POSTING_TIMES.get(platform, [(9, 0), (14, 0), (19, 0)])
            
            # For now, return the first optimal time
            # In production, this would analyze audience behavior
            hour, minute = times[0]
            return f"{hour:02d}:{minute:02d}"
            
        except Exception as e:
            logger.error(f"Failed to suggest posting time: {e}")
            return "09:00"
    
    def apply_viral_patterns(self, content: str, pattern: str) -> str:
        """Apply viral pattern to content"""
        try:
            if pattern not in VIRAL_PATTERNS:
                return content
            
            patterns = VIRAL_PATTERNS[pattern]
            # Use first pattern as prefix
            enhanced = f"{patterns[0]} {content}"
            return enhanced
            
        except Exception as e:
            logger.error(f"Failed to apply viral pattern: {e}")
            return content
    
    async def generate_variations(self, content: str, count: int = 3) -> List[str]:
        """Generate variations of content for A/B testing"""
        try:
            prompt = f"""
Generate {count} variations of this content for A/B testing:

Original: {content}

Return JSON array of {count} different variations:
[
  "Variation 1 text",
  "Variation 2 text",
  "Variation 3 text"
]

Each variation should:
- Maintain the core message
- Use different wording and structure
- Apply different psychological triggers
- Be optimized for engagement
"""
            
            result = await self._call_ai(prompt)
            
            if isinstance(result, list) and len(result) > 0:
                return result
            
            # Fallback to original if AI fails
            return [content]
            
        except Exception as e:
            logger.error(f"Failed to generate variations: {e}")
            return [content]  # Return original if generation fails
    
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
                        {"role": "system", "content": self.viral_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.9,  # Higher temperature for creativity
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                logger.info("AI call successful with Groq")
                
                # Extract array if wrapped in object
                if isinstance(result, dict) and 'posts' in result:
                    return result['posts']
                elif isinstance(result, dict) and 'variations' in result:
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
                        "temperature": 0.9,
                        "response_mime_type": "application/json"
                    },
                    system_instruction=self.viral_prompt
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
                if isinstance(result, dict) and 'posts' in result:
                    return result['posts']
                elif isinstance(result, dict) and 'variations' in result:
                    return result['variations']
                return result
            except Exception as e:
                error_msg = f"Gemini failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # All AI services failed
        logger.error(f"All AI services failed. Errors: {'; '.join(errors)}")
        return []
    
    def _get_mock_viral_posts(self, topic: str, platform: str, count: int) -> List[Dict[str, Any]]:
        """Return mock viral posts when AI services fail"""
        mock_posts = [
            {
                "content": f"🚀 The secret to {topic} that nobody talks about... (Thread)",
                "virality_score": 85,
                "hashtags": ["#growth", "#marketing", "#business"],
                "best_time": "09:00",
                "psychological_trigger": "Curiosity",
                "expected_engagement": "500+ likes, 100+ shares",
                "content_type": "text",
                "platform_specific_tips": f"Optimized for {platform} audience"
            },
            {
                "content": f"I spent 6 months mastering {topic}. Here's what I learned 👇",
                "virality_score": 82,
                "hashtags": ["#entrepreneur", "#success"],
                "best_time": "14:00",
                "psychological_trigger": "Storytelling",
                "expected_engagement": "400+ likes, 80+ shares",
                "content_type": "text",
                "platform_specific_tips": f"Use thread format on {platform}"
            },
            {
                "content": f"⚠️ Stop doing {topic} wrong! Here's the right way...",
                "virality_score": 78,
                "hashtags": ["#tips", "#advice"],
                "best_time": "11:00",
                "psychological_trigger": "Controversy",
                "expected_engagement": "350+ likes, 70+ shares",
                "content_type": "text",
                "platform_specific_tips": "Add visual content for better engagement"
            },
            {
                "content": f"The {topic} framework that 10X'd our results 📈",
                "virality_score": 75,
                "hashtags": ["#strategy", "#results"],
                "best_time": "16:00",
                "psychological_trigger": "Data-Driven",
                "expected_engagement": "300+ likes, 60+ shares",
                "content_type": "text",
                "platform_specific_tips": "Include case study or data visualization"
            },
            {
                "content": f"Unpopular opinion: Most people get {topic} completely wrong",
                "virality_score": 72,
                "hashtags": ["#truth", "#reality"],
                "best_time": "19:00",
                "psychological_trigger": "Controversy",
                "expected_engagement": "250+ likes, 50+ shares",
                "content_type": "text",
                "platform_specific_tips": "Expect debate in comments"
            }
        ]
        
        return mock_posts[:count]

# Global instance
viral_content_engine = None
