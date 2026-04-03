"""
Lead Funnel Automator
Creates and manages automated lead funnels with email sequences and scoring
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import json
import uuid
from groq_service import groq_service
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Funnel stages
FUNNEL_STAGES = ['Awareness', 'Interest', 'Decision', 'Action']

# Lead scoring criteria
SCORING_CRITERIA = {
    'email_open': 5,
    'link_click': 10,
    'page_visit': 15,
    'form_submission': 25,
    'demo_request': 50,
    'pricing_page_view': 30,
    'case_study_download': 20
}

# Lead status thresholds
HOT_LEAD_THRESHOLD = 75
COLD_LEAD_THRESHOLD = 20

class LeadFunnelAutomator:
    """Automated lead funnel management with scoring and segmentation"""
    
    def __init__(self, db, ai_client=None):
        self.db = db
        self.ai_client = ai_client
        
        # Master prompt for funnel creation
        self.funnel_prompt = """You are a sales funnel architect specializing in:
- Lead generation and nurturing
- Email marketing automation
- Behavioral segmentation
- Conversion optimization
- Customer journey mapping

Your goal is to create effective lead funnels that guide prospects from awareness to conversion.

Always return structured JSON with complete funnel stages and automation rules."""
    
    async def create_funnel(self, business_id: str, goal: str) -> Dict[str, Any]:
        """Create automated lead funnel"""
        try:
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            prompt = f"""
Design a complete lead funnel for: {goal}

Business: {business.get('business_type')}
Target Market: {business.get('target_market')}
Budget: {business.get('monthly_budget')}

Return JSON:
{{
  "funnel_name": "Funnel name",
  "goal": "{goal}",
  "funnel_stages": [
    {{
      "stage": "Awareness|Interest|Decision|Action",
      "tactics": ["tactic1", "tactic2"],
      "content": ["content1", "content2"],
      "expected_conversion": "20%"
    }}
  ],
  "email_automation": [
    {{
      "trigger": "Lead enters funnel|Downloaded lead magnet|Viewed pricing",
      "delay_days": 0,
      "subject": "Email subject",
      "content": "Email body with personalization",
      "goal": "Move to next stage"
    }}
  ],
  "lead_scoring": {{
    "criteria": ["action: +points", "action: +points"],
    "hot_lead_threshold": 75,
    "cold_lead_threshold": 20
  }},
  "segmentation_rules": [
    {{
      "segment_name": "High Intent",
      "criteria": "score > 50 AND viewed pricing",
      "actions": ["Send demo offer", "Notify sales team"]
    }}
  ]
}}

IMPORTANT: Include all 4 funnel stages (Awareness, Interest, Decision, Action).
"""
            
            result = await self._call_ai(prompt)
            
            # Validate and enhance result
            if isinstance(result, dict) and 'funnel_stages' in result:
                funnel_id = str(uuid.uuid4())
                
                # Create funnel record
                funnel = {
                    'id': funnel_id,
                    'business_id': business_id,
                    'funnel_name': result.get('funnel_name', f'Funnel: {goal}'),
                    'goal': goal,
                    'funnel_stages': result.get('funnel_stages', []),
                    'email_automation': result.get('email_automation', []),
                    'lead_scoring': result.get('lead_scoring', {
                        'criteria': list(SCORING_CRITERIA.items()),
                        'hot_lead_threshold': HOT_LEAD_THRESHOLD,
                        'cold_lead_threshold': COLD_LEAD_THRESHOLD
                    }),
                    'segmentation_rules': result.get('segmentation_rules', []),
                    'status': 'active',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'stats': {
                        'total_leads': 0,
                        'active_leads': 0,
                        'converted_leads': 0,
                        'conversion_rate': 0
                    }
                }
                
                # Save to database
                await self.db.lead_funnels.insert_one(funnel.copy())
                
                logger.info(f"Lead funnel {funnel_id} created for business {business_id}")
                
                # Return without MongoDB ObjectId
                if '_id' in funnel:
                    del funnel['_id']
                
                return funnel
            
            # Fallback to mock funnel if AI returns incomplete result
            return self._get_mock_funnel(goal, business_id)
            
        except Exception as e:
            logger.error(f"Failed to create funnel: {e}", exc_info=True)
            return self._get_mock_funnel(goal, business_id)
    
    async def add_lead(self, funnel_id: str, lead_data: Dict[str, Any]) -> str:
        """Add lead to funnel"""
        try:
            # Get funnel
            funnel = await self.db.lead_funnels.find_one({'id': funnel_id})
            if not funnel:
                logger.error(f"Funnel {funnel_id} not found")
                raise Exception(f"Funnel {funnel_id} not found")
            
            lead_id = str(uuid.uuid4())
            
            # Create lead record
            lead = {
                'id': lead_id,
                'funnel_id': funnel_id,
                'business_id': funnel.get('business_id'),
                'email': lead_data.get('email'),
                'name': lead_data.get('name'),
                'company': lead_data.get('company'),
                'current_stage': 'Awareness',
                'score': 0,
                'status': 'active',
                'entered_at': datetime.now(timezone.utc).isoformat(),
                'last_activity': datetime.now(timezone.utc).isoformat(),
                'activities': [],
                'segment': 'new',
                'converted': False
            }
            
            # Save to database
            await self.db.leads.insert_one(lead.copy())
            
            # Update funnel stats
            await self.db.lead_funnels.update_one(
                {'id': funnel_id},
                {
                    '$inc': {
                        'stats.total_leads': 1,
                        'stats.active_leads': 1
                    }
                }
            )
            
            # Trigger welcome email automation
            await self._trigger_automation(lead_id, 'Lead enters funnel')
            
            logger.info(f"Lead {lead_id} added to funnel {funnel_id}")
            return lead_id
            
        except Exception as e:
            logger.error(f"Failed to add lead: {e}")
            raise
    
    async def segment_leads(self, funnel_id: str) -> Dict[str, List[str]]:
        """Segment leads based on behavior and demographics"""
        try:
            # Get all leads in funnel
            leads = await self.db.leads.find({'funnel_id': funnel_id}).to_list(length=1000)
            
            segments = {
                'high_intent': [],
                'low_intent': [],
                'nurture': [],
                'hot': [],
                'cold': []
            }
            
            for lead in leads:
                lead_id = lead.get('id')
                score = lead.get('score', 0)
                stage = lead.get('current_stage', 'Awareness')
                
                # Score-based segmentation
                if score >= HOT_LEAD_THRESHOLD:
                    segments['hot'].append(lead_id)
                    segments['high_intent'].append(lead_id)
                elif score <= COLD_LEAD_THRESHOLD:
                    segments['cold'].append(lead_id)
                    segments['low_intent'].append(lead_id)
                else:
                    segments['nurture'].append(lead_id)
                
                # Stage-based segmentation
                if stage in ['Decision', 'Action']:
                    if lead_id not in segments['high_intent']:
                        segments['high_intent'].append(lead_id)
            
            return segments
            
        except Exception as e:
            logger.error(f"Failed to segment leads: {e}")
            return {}
    
    async def send_sequence(self, lead_id: str, sequence_id: str) -> bool:
        """Send email sequence to lead"""
        try:
            # Get lead
            lead = await self.db.leads.find_one({'id': lead_id})
            if not lead:
                logger.error(f"Lead {lead_id} not found")
                return False
            
            # Get funnel
            funnel_id = lead.get('funnel_id')
            funnel = await self.db.lead_funnels.find_one({'id': funnel_id})
            if not funnel:
                logger.error(f"Funnel {funnel_id} not found")
                return False
            
            # Get email automation sequence
            email_automation = funnel.get('email_automation', [])
            
            # Schedule emails
            for email in email_automation:
                delay_days = email.get('delay_days', 0)
                send_at = datetime.now(timezone.utc) + timedelta(days=delay_days)
                
                # Create scheduled email record
                scheduled_email = {
                    'id': str(uuid.uuid4()),
                    'lead_id': lead_id,
                    'funnel_id': funnel_id,
                    'subject': email.get('subject'),
                    'content': email.get('content'),
                    'trigger': email.get('trigger'),
                    'scheduled_at': send_at.isoformat(),
                    'status': 'scheduled',
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
                
                await self.db.scheduled_emails.insert_one(scheduled_email.copy())
            
            logger.info(f"Email sequence scheduled for lead {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send sequence: {e}")
            return False
    
    async def score_lead(self, lead_id: str, activity: str, points: Optional[int] = None) -> int:
        """Update lead score based on activity"""
        try:
            # Get lead
            lead = await self.db.leads.find_one({'id': lead_id})
            if not lead:
                logger.error(f"Lead {lead_id} not found")
                return 0
            
            # Calculate points
            if points is None:
                points = SCORING_CRITERIA.get(activity, 0)
            
            # Update score
            new_score = lead.get('score', 0) + points
            
            # Record activity
            activity_record = {
                'type': activity,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'points': points
            }
            
            # Update lead
            await self.db.leads.update_one(
                {'id': lead_id},
                {
                    '$set': {
                        'score': new_score,
                        'last_activity': datetime.now(timezone.utc).isoformat()
                    },
                    '$push': {
                        'activities': activity_record
                    }
                }
            )
            
            # Check if lead became hot
            if new_score >= HOT_LEAD_THRESHOLD and lead.get('score', 0) < HOT_LEAD_THRESHOLD:
                await self._notify_hot_lead(lead_id)
            
            logger.info(f"Lead {lead_id} scored {points} points for {activity}, new score: {new_score}")
            return new_score
            
        except Exception as e:
            logger.error(f"Failed to score lead: {e}")
            return 0
    
    async def move_stage(self, lead_id: str, new_stage: str) -> bool:
        """Move lead to new funnel stage"""
        try:
            if new_stage not in FUNNEL_STAGES:
                logger.error(f"Invalid stage: {new_stage}")
                return False
            
            # Update lead stage
            result = await self.db.leads.update_one(
                {'id': lead_id},
                {
                    '$set': {
                        'current_stage': new_stage,
                        'last_activity': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Lead {lead_id} moved to {new_stage} stage")
                
                # Trigger stage-specific automation
                await self._trigger_stage_automation(lead_id, new_stage)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to move stage: {e}")
            return False
    
    async def reengage_cold_leads(self, funnel_id: str) -> int:
        """Re-engage cold leads with targeted campaigns"""
        try:
            # Find cold leads
            cold_leads = await self.db.leads.find({
                'funnel_id': funnel_id,
                'score': {'$lte': COLD_LEAD_THRESHOLD},
                'status': 'active'
            }).to_list(length=1000)
            
            reengaged_count = 0
            
            for lead in cold_leads:
                lead_id = lead.get('id')
                
                # Send re-engagement email
                reengagement_email = {
                    'id': str(uuid.uuid4()),
                    'lead_id': lead_id,
                    'funnel_id': funnel_id,
                    'subject': "We miss you! Here's something special...",
                    'content': "Re-engagement email content with special offer",
                    'trigger': 'cold_lead_reengagement',
                    'scheduled_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'scheduled',
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
                
                await self.db.scheduled_emails.insert_one(reengagement_email.copy())
                reengaged_count += 1
            
            logger.info(f"Re-engaged {reengaged_count} cold leads in funnel {funnel_id}")
            return reengaged_count
            
        except Exception as e:
            logger.error(f"Failed to re-engage cold leads: {e}")
            return 0
    
    async def _trigger_automation(self, lead_id: str, trigger: str) -> None:
        """Trigger email automation based on event"""
        try:
            # Get lead and funnel
            lead = await self.db.leads.find_one({'id': lead_id})
            if not lead:
                return
            
            funnel = await self.db.lead_funnels.find_one({'id': lead.get('funnel_id')})
            if not funnel:
                return
            
            # Find matching automation
            email_automation = funnel.get('email_automation', [])
            for email in email_automation:
                if email.get('trigger') == trigger:
                    delay_days = email.get('delay_days', 0)
                    send_at = datetime.now(timezone.utc) + timedelta(days=delay_days)
                    
                    # Schedule email
                    scheduled_email = {
                        'id': str(uuid.uuid4()),
                        'lead_id': lead_id,
                        'funnel_id': lead.get('funnel_id'),
                        'subject': email.get('subject'),
                        'content': email.get('content'),
                        'trigger': trigger,
                        'scheduled_at': send_at.isoformat(),
                        'status': 'scheduled',
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    await self.db.scheduled_emails.insert_one(scheduled_email.copy())
                    logger.info(f"Automation triggered for lead {lead_id}: {trigger}")
                    
        except Exception as e:
            logger.error(f"Failed to trigger automation: {e}")
    
    async def _trigger_stage_automation(self, lead_id: str, stage: str) -> None:
        """Trigger automation when lead moves to new stage"""
        # Trigger automation based on stage
        stage_triggers = {
            'Awareness': 'Lead enters funnel',
            'Interest': 'Downloaded lead magnet',
            'Decision': 'Viewed pricing page',
            'Action': 'Demo request'
        }
        
        trigger = stage_triggers.get(stage)
        if trigger:
            await self._trigger_automation(lead_id, trigger)
    
    async def _notify_hot_lead(self, lead_id: str) -> None:
        """Notify sales team about hot lead"""
        try:
            lead = await self.db.leads.find_one({'id': lead_id})
            if not lead:
                return
            
            # Create notification
            notification = {
                'id': str(uuid.uuid4()),
                'type': 'hot_lead',
                'lead_id': lead_id,
                'business_id': lead.get('business_id'),
                'message': f"Hot lead alert: {lead.get('name', lead.get('email'))} scored {lead.get('score')} points",
                'created_at': datetime.now(timezone.utc).isoformat(),
                'read': False
            }
            
            await self.db.notifications.insert_one(notification.copy())
            logger.info(f"Hot lead notification created for lead {lead_id}")
            
        except Exception as e:
            logger.error(f"Failed to notify hot lead: {e}")
    
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
                        {"role": "system", "content": self.funnel_prompt},
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
                    system_instruction=self.funnel_prompt
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
    
    def _get_mock_funnel(self, goal: str, business_id: str) -> Dict[str, Any]:
        """Return mock funnel when AI services fail"""
        funnel_id = str(uuid.uuid4())
        
        return {
            'id': funnel_id,
            'business_id': business_id,
            'funnel_name': f'Lead Funnel: {goal}',
            'goal': goal,
            'funnel_stages': [
                {
                    'stage': 'Awareness',
                    'tactics': ['Content marketing', 'SEO', 'Social media'],
                    'content': ['Blog posts', 'Infographics', 'Videos'],
                    'expected_conversion': '20%'
                },
                {
                    'stage': 'Interest',
                    'tactics': ['Lead magnet', 'Webinar', 'Email nurture'],
                    'content': ['Ebook', 'Case studies', 'Product demo'],
                    'expected_conversion': '40%'
                },
                {
                    'stage': 'Decision',
                    'tactics': ['Free trial', 'Consultation', 'Comparison guide'],
                    'content': ['ROI calculator', 'Testimonials', 'Pricing page'],
                    'expected_conversion': '30%'
                },
                {
                    'stage': 'Action',
                    'tactics': ['Limited offer', 'Onboarding', 'Success stories'],
                    'content': ['Signup form', 'Welcome email', 'Quick start guide'],
                    'expected_conversion': '50%'
                }
            ],
            'email_automation': [
                {
                    'trigger': 'Lead enters funnel',
                    'delay_days': 0,
                    'subject': f"Welcome! Let's achieve {goal}",
                    'content': "Thank you for your interest. Here's your free guide...",
                    'goal': 'Move to Interest stage'
                },
                {
                    'trigger': 'Downloaded lead magnet',
                    'delay_days': 2,
                    'subject': 'How others achieved success',
                    'content': "Here are 3 case studies from businesses like yours...",
                    'goal': 'Build trust and credibility'
                },
                {
                    'trigger': 'Viewed pricing page',
                    'delay_days': 1,
                    'subject': 'Questions about getting started?',
                    'content': "I noticed you checked out our pricing. Any questions?",
                    'goal': 'Address objections'
                }
            ],
            'lead_scoring': {
                'criteria': [
                    'Email open: +5 points',
                    'Link click: +10 points',
                    'Page visit: +15 points',
                    'Form submission: +25 points',
                    'Demo request: +50 points'
                ],
                'hot_lead_threshold': HOT_LEAD_THRESHOLD,
                'cold_lead_threshold': COLD_LEAD_THRESHOLD
            },
            'segmentation_rules': [
                {
                    'segment_name': 'High Intent',
                    'criteria': 'score > 50 AND viewed pricing',
                    'actions': ['Send demo offer', 'Notify sales team']
                }
            ],
            'status': 'active',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'stats': {
                'total_leads': 0,
                'active_leads': 0,
                'converted_leads': 0,
                'conversion_rate': 0
            }
        }

# Global instance
lead_funnel_automator = None
