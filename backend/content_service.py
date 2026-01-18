"""
Content Generation Service
Creates pitch decks, email sequences, and content calendars
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import google.generativeai as genai

logger = logging.getLogger(__name__)

class ContentGenerationService:
    def __init__(self, gemini_model):
        self.model = gemini_model
    
    async def generate_pitch_deck(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete pitch deck based on analysis"""
        prompt = f"""
        Based on this business analysis, create a comprehensive pitch deck outline:
        
        Business Overview: {analysis.get('overview', '')}
        Market Size: {analysis.get('market_analysis', {}).get('market_size', '')}
        Target Personas: {[p.get('name', '') for p in analysis.get('user_personas', [])]}
        Revenue Projection: {analysis.get('revenue_projection', {}).get('max_monthly', '')}
        
        Create a pitch deck with the following slides (return as JSON):
        {{
            "slides": [
                {{
                    "slide_number": 1,
                    "title": "Problem",
                    "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
                    "speaker_notes": "What to say during this slide"
                }},
                // Include: Problem, Solution, Market Opportunity, Business Model, 
                // Traction, Competition, Team, Financials, Ask
            ]
        }}
        
        Return ONLY valid JSON.
        """
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
            
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            import json
            pitch_deck = json.loads(response.text.strip())
            
            return {
                'pitch_deck': pitch_deck,
                'total_slides': len(pitch_deck.get('slides', [])),
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Pitch deck generation failed: {e}")
            return self._get_mock_pitch_deck(analysis)
    
    async def generate_content_calendar(
        self, 
        analysis: Dict[str, Any], 
        duration_weeks: int = 4
    ) -> Dict[str, Any]:
        """Generate a content calendar for multiple channels"""
        strategies = analysis.get('strategies', [])
        
        prompt = f"""
        Create a {duration_weeks}-week content calendar based on these marketing strategies:
        
        {self._format_strategies(strategies)}
        
        Return a JSON content calendar with daily posts across all channels:
        {{
            "weeks": [
                {{
                    "week_number": 1,
                    "days": [
                        {{
                            "day": "Monday",
                            "date": "2026-01-13",
                            "posts": [
                                {{
                                    "channel": "LinkedIn",
                                    "content_type": "Article",
                                    "topic": "...",
                                    "caption": "...",
                                    "hashtags": ["#marketing", "#ai"],
                                    "time": "09:00 AM"
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        
        Return ONLY valid JSON.
        """
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.8,
                response_mime_type="application/json"
            )
            
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            import json
            calendar = json.loads(response.text.strip())
            
            return {
                'content_calendar': calendar,
                'duration_weeks': duration_weeks,
                'total_posts': self._count_posts(calendar),
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Content calendar generation failed: {e}")
            return self._get_mock_content_calendar(duration_weeks)
    
    async def generate_email_sequence(
        self, 
        analysis: Dict[str, Any], 
        sequence_type: str = "onboarding"
    ) -> Dict[str, Any]:
        """Generate an email drip campaign sequence"""
        personas = analysis.get('user_personas', [])
        
        prompt = f"""
        Create a {sequence_type} email sequence for these user personas:
        
        {self._format_personas(personas)}
        
        Generate a 5-email sequence with:
        {{
            "sequence_name": "{sequence_type.title()} Sequence",
            "emails": [
                {{
                    "email_number": 1,
                    "send_delay_days": 0,
                    "subject_line": "...",
                    "preview_text": "...",
                    "body": "Full email body with personalization tags",
                    "cta": "Call to action button text",
                    "cta_link": "https://example.com/action"
                }}
            ]
        }}
        
        Return ONLY valid JSON.
        """
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
            
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            import json
            sequence = json.loads(response.text.strip())
            
            return {
                'email_sequence': sequence,
                'total_emails': len(sequence.get('emails', [])),
                'sequence_type': sequence_type,
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Email sequence generation failed: {e}")
            return self._get_mock_email_sequence(sequence_type)
    
    async def generate_social_posts(
        self, 
        strategy: Dict[str, Any], 
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate ready-to-post social media content"""
        channel = strategy.get('channel', 'Social Media')
        content_ideas = strategy.get('content_ideas', [])
        
        prompt = f"""
        Generate {count} ready-to-post {channel} posts based on these content ideas:
        
        {chr(10).join([f"- {idea}" for idea in content_ideas])}
        
        Return JSON array of posts:
        {{
            "posts": [
                {{
                    "post_number": 1,
                    "caption": "Engaging post caption with emojis",
                    "hashtags": ["#tag1", "#tag2", "#tag3"],
                    "best_time": "Tuesday 10:00 AM",
                    "content_type": "Image/Video/Carousel",
                    "image_description": "Description for image generation"
                }}
            ]
        }}
        
        Return ONLY valid JSON.
        """
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.9,
                response_mime_type="application/json"
            )
            
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            import json
            posts_data = json.loads(response.text.strip())
            
            return posts_data.get('posts', [])
        except Exception as e:
            logger.error(f"Social posts generation failed: {e}")
            return []
    
    def _format_strategies(self, strategies: List[Dict]) -> str:
        """Format strategies for prompt"""
        return "\n".join([
            f"- {s.get('channel', '')}: {s.get('strategy', '')}"
            for s in strategies
        ])
    
    def _format_personas(self, personas: List[Dict]) -> str:
        """Format personas for prompt"""
        return "\n".join([
            f"- {p.get('name', '')}: {p.get('demographics', '')}"
            for p in personas
        ])
    
    def _count_posts(self, calendar: Dict) -> int:
        """Count total posts in calendar"""
        total = 0
        for week in calendar.get('weeks', []):
            for day in week.get('days', []):
                total += len(day.get('posts', []))
        return total
    
    def _get_mock_pitch_deck(self, analysis: Dict) -> Dict[str, Any]:
        """Return mock pitch deck"""
        return {
            'pitch_deck': {
                'slides': [
                    {
                        'slide_number': 1,
                        'title': 'Problem',
                        'content': [
                            'Market inefficiency identified',
                            'Customer pain points unaddressed',
                            'Opportunity for disruption'
                        ],
                        'speaker_notes': 'Start with the problem to hook investors'
                    },
                    {
                        'slide_number': 2,
                        'title': 'Solution',
                        'content': [
                            'AI-powered platform',
                            'Automated insights',
                            '10x faster than competitors'
                        ],
                        'speaker_notes': 'Explain how we solve the problem uniquely'
                    }
                ]
            },
            'total_slides': 2,
            'generated_at': datetime.utcnow().isoformat(),
            'data_source': 'mock'
        }
    
    def _get_mock_content_calendar(self, weeks: int) -> Dict[str, Any]:
        """Return mock content calendar"""
        return {
            'content_calendar': {
                'weeks': [
                    {
                        'week_number': 1,
                        'days': [
                            {
                                'day': 'Monday',
                                'date': '2026-01-13',
                                'posts': [
                                    {
                                        'channel': 'LinkedIn',
                                        'content_type': 'Article',
                                        'topic': 'AI Marketing Trends 2026',
                                        'caption': 'The future of marketing is here...',
                                        'hashtags': ['#AIMarketing', '#DigitalTransformation'],
                                        'time': '09:00 AM'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            'duration_weeks': weeks,
            'total_posts': 1,
            'generated_at': datetime.utcnow().isoformat(),
            'data_source': 'mock'
        }
    
    def _get_mock_email_sequence(self, sequence_type: str) -> Dict[str, Any]:
        """Return mock email sequence"""
        return {
            'email_sequence': {
                'sequence_name': f'{sequence_type.title()} Sequence',
                'emails': [
                    {
                        'email_number': 1,
                        'send_delay_days': 0,
                        'subject_line': 'Welcome to AstraMark!',
                        'preview_text': 'Get started with AI-powered marketing',
                        'body': 'Welcome email body...',
                        'cta': 'Get Started',
                        'cta_link': 'https://astramark.com/start'
                    }
                ]
            },
            'total_emails': 1,
            'sequence_type': sequence_type,
            'generated_at': datetime.utcnow().isoformat(),
            'data_source': 'mock'
        }
