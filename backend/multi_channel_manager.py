"""
Multi-Channel Manager
Unified management of SEO, paid ads, social media, and email marketing
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import json

logger = logging.getLogger(__name__)


class MultiChannelManager:
    """
    Unified management of marketing channels:
    - SEO optimization and keyword tracking
    - Google Ads and Facebook Ads management
    - Social media scheduling (LinkedIn, Twitter, Instagram)
    - Email marketing integration (SendGrid/Mailchimp)
    - Cross-channel attribution tracking
    - Budget reallocation based on performance
    """
    
    def __init__(self, db, config=None):
        self.db = db
        self.config = config or {}
        
        # Channel performance thresholds
        self.roi_threshold = 1.5  # Minimum acceptable ROI
        self.underperformance_threshold = 0.8  # 80% of average ROI
        
        # Budget reallocation settings
        self.min_budget_percentage = 10  # Minimum 10% per channel
        self.max_budget_percentage = 60  # Maximum 60% per channel
    
    # ==================== SEO Management ====================
    
    async def track_keywords(self, business_id: str) -> List[Dict[str, Any]]:
        """Track keyword rankings and performance for SEO"""
        try:
            # Get business profile for target keywords
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return []
            
            # Get existing keyword tracking data
            keyword_data = await self.db.seo_keywords.find(
                {'business_id': business_id}
            ).sort('last_updated', -1).to_list(length=100)
            
            if not keyword_data:
                # Initialize with mock data for new businesses
                return self._get_mock_keyword_tracking(business_id)
            
            return keyword_data
            
        except Exception as e:
            logger.error(f"Failed to track keywords: {e}")
            return []
    
    async def generate_seo_content(self, business_id: str, keywords: List[str]) -> Dict[str, Any]:
        """Generate SEO-optimized content recommendations"""
        try:
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                return {}
            
            # Generate content recommendations
            content_recommendations = {
                'business_id': business_id,
                'keywords': keywords,
                'content_pieces': [
                    {
                        'type': 'blog_post',
                        'title': f"How to {keywords[0] if keywords else 'grow your business'}",
                        'target_keyword': keywords[0] if keywords else 'business growth',
                        'word_count': 1500,
                        'priority': 'high',
                        'estimated_traffic': '500-1000 visits/month'
                    },
                    {
                        'type': 'landing_page',
                        'title': f"Best {keywords[1] if len(keywords) > 1 else 'solutions'} for your needs",
                        'target_keyword': keywords[1] if len(keywords) > 1 else 'solutions',
                        'word_count': 800,
                        'priority': 'medium',
                        'estimated_traffic': '200-500 visits/month'
                    }
                ],
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Save recommendations
            await self.db.seo_content_recommendations.insert_one(content_recommendations.copy())
            
            return content_recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate SEO content: {e}")
            return {}
    
    # ==================== Paid Ads Management ====================
    
    async def create_google_ad(self, campaign_id: str, ad_data: Dict[str, Any]) -> str:
        """Create a Google Ads campaign"""
        try:
            ad_id = f"google_ad_{uuid.uuid4().hex[:12]}"
            
            google_ad = {
                'id': ad_id,
                'campaign_id': campaign_id,
                'platform': 'google_ads',
                'headline': ad_data.get('headline', ''),
                'description': ad_data.get('description', ''),
                'target_url': ad_data.get('target_url', ''),
                'keywords': ad_data.get('keywords', []),
                'daily_budget': ad_data.get('daily_budget', 0),
                'status': 'active',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'performance': {
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'spend': 0,
                    'ctr': 0,
                    'cpc': 0
                }
            }
            
            # Save to database
            await self.db.google_ads.insert_one(google_ad.copy())
            
            logger.info(f"Created Google Ad: {ad_id}")
            return ad_id
            
        except Exception as e:
            logger.error(f"Failed to create Google Ad: {e}")
            raise Exception(f"Google Ads creation failed: {str(e)}")
    
    async def create_facebook_ad(self, campaign_id: str, ad_data: Dict[str, Any]) -> str:
        """Create a Facebook Ads campaign"""
        try:
            ad_id = f"facebook_ad_{uuid.uuid4().hex[:12]}"
            
            facebook_ad = {
                'id': ad_id,
                'campaign_id': campaign_id,
                'platform': 'facebook_ads',
                'headline': ad_data.get('headline', ''),
                'description': ad_data.get('description', ''),
                'image_url': ad_data.get('image_url', ''),
                'target_url': ad_data.get('target_url', ''),
                'targeting': ad_data.get('targeting', {}),
                'daily_budget': ad_data.get('daily_budget', 0),
                'status': 'active',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'performance': {
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'spend': 0,
                    'ctr': 0,
                    'cpc': 0
                }
            }
            
            # Save to database
            await self.db.facebook_ads.insert_one(facebook_ad.copy())
            
            logger.info(f"Created Facebook Ad: {ad_id}")
            return ad_id
            
        except Exception as e:
            logger.error(f"Failed to create Facebook Ad: {e}")
            raise Exception(f"Facebook Ads creation failed: {str(e)}")
    
    async def update_ad_budget(self, ad_id: str, new_budget: float) -> bool:
        """Update ad budget for Google or Facebook ads"""
        try:
            # Try Google Ads first
            result = await self.db.google_ads.update_one(
                {'id': ad_id},
                {
                    '$set': {
                        'daily_budget': new_budget,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated Google Ad budget: {ad_id} -> ${new_budget}")
                return True
            
            # Try Facebook Ads
            result = await self.db.facebook_ads.update_one(
                {'id': ad_id},
                {
                    '$set': {
                        'daily_budget': new_budget,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated Facebook Ad budget: {ad_id} -> ${new_budget}")
                return True
            
            logger.warning(f"Ad not found: {ad_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to update ad budget: {e}")
            return False
    
    # ==================== Social Media Management ====================
    
    async def schedule_post(self, platform: str, content: Dict[str, Any], schedule_time: datetime) -> str:
        """Schedule a social media post"""
        try:
            post_id = f"social_post_{uuid.uuid4().hex[:12]}"
            
            social_post = {
                'id': post_id,
                'platform': platform.lower(),
                'content': content.get('text', ''),
                'image_url': content.get('image_url'),
                'hashtags': content.get('hashtags', []),
                'schedule_time': schedule_time.isoformat(),
                'status': 'scheduled',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'published_at': None,
                'performance': {
                    'likes': 0,
                    'shares': 0,
                    'comments': 0,
                    'reach': 0,
                    'engagement_rate': 0
                }
            }
            
            # Save to database
            await self.db.social_posts.insert_one(social_post.copy())
            
            logger.info(f"Scheduled {platform} post: {post_id} for {schedule_time}")
            return post_id
            
        except Exception as e:
            logger.error(f"Failed to schedule post: {e}")
            raise Exception(f"Social media scheduling failed: {str(e)}")
    
    async def publish_post(self, post_id: str) -> bool:
        """Publish a scheduled social media post"""
        try:
            result = await self.db.social_posts.update_one(
                {'id': post_id, 'status': 'scheduled'},
                {
                    '$set': {
                        'status': 'published',
                        'published_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Published social post: {post_id}")
                return True
            
            logger.warning(f"Post not found or already published: {post_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to publish post: {e}")
            return False
    
    # ==================== Email Marketing ====================
    
    async def send_email_sequence(self, lead_id: str, sequence: List[Dict[str, Any]]) -> bool:
        """Send automated email sequence to a lead"""
        try:
            # Get lead information
            lead = await self.db.leads.find_one({'id': lead_id})
            if not lead:
                logger.warning(f"Lead not found: {lead_id}")
                return False
            
            # Create email sequence record
            sequence_id = f"email_seq_{uuid.uuid4().hex[:12]}"
            
            email_sequence_record = {
                'id': sequence_id,
                'lead_id': lead_id,
                'lead_email': lead.get('email'),
                'sequence': sequence,
                'status': 'active',
                'current_step': 0,
                'started_at': datetime.now(timezone.utc).isoformat(),
                'emails_sent': 0,
                'emails_opened': 0,
                'emails_clicked': 0
            }
            
            # Save sequence
            await self.db.email_sequences.insert_one(email_sequence_record.copy())
            
            logger.info(f"Started email sequence {sequence_id} for lead {lead_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email sequence: {e}")
            return False
    
    async def track_email_engagement(self, email_id: str) -> Dict[str, Any]:
        """Track email engagement metrics"""
        try:
            email = await self.db.email_sequences.find_one({'id': email_id})
            if not email:
                return {}
            
            engagement = {
                'email_id': email_id,
                'emails_sent': email.get('emails_sent', 0),
                'emails_opened': email.get('emails_opened', 0),
                'emails_clicked': email.get('emails_clicked', 0),
                'open_rate': (email.get('emails_opened', 0) / max(email.get('emails_sent', 1), 1)) * 100,
                'click_rate': (email.get('emails_clicked', 0) / max(email.get('emails_sent', 1), 1)) * 100
            }
            
            return engagement
            
        except Exception as e:
            logger.error(f"Failed to track email engagement: {e}")
            return {}
    
    # ==================== Attribution Tracking ====================
    
    async def track_conversion(self, conversion_data: Dict[str, Any]) -> None:
        """Track a conversion event with attribution data"""
        try:
            conversion_id = f"conversion_{uuid.uuid4().hex[:12]}"
            
            conversion = {
                'id': conversion_id,
                'business_id': conversion_data.get('business_id'),
                'campaign_id': conversion_data.get('campaign_id'),
                'lead_id': conversion_data.get('lead_id'),
                'conversion_type': conversion_data.get('type', 'purchase'),
                'value': conversion_data.get('value', 0),
                'touchpoints': conversion_data.get('touchpoints', []),
                'converted_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Save conversion
            await self.db.conversions.insert_one(conversion.copy())
            
            logger.info(f"Tracked conversion: {conversion_id}")
            
        except Exception as e:
            logger.error(f"Failed to track conversion: {e}")
    
    async def calculate_attribution(self, conversion_id: str) -> Dict[str, Any]:
        """Calculate multi-touch attribution for a conversion"""
        try:
            conversion = await self.db.conversions.find_one({'id': conversion_id})
            if not conversion:
                return {}
            
            touchpoints = conversion.get('touchpoints', [])
            if not touchpoints:
                return {'attribution_model': 'none', 'channel_credits': {}}
            
            # Multi-touch attribution (linear model)
            credit_per_touchpoint = 1.0 / len(touchpoints)
            channel_credits = {}
            
            for touchpoint in touchpoints:
                channel = touchpoint.get('channel', 'unknown')
                if channel not in channel_credits:
                    channel_credits[channel] = 0
                channel_credits[channel] += credit_per_touchpoint
            
            attribution = {
                'conversion_id': conversion_id,
                'attribution_model': 'linear',
                'total_touchpoints': len(touchpoints),
                'channel_credits': channel_credits,
                'conversion_value': conversion.get('value', 0),
                'calculated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Save attribution
            await self.db.attributions.insert_one(attribution.copy())
            
            return attribution
            
        except Exception as e:
            logger.error(f"Failed to calculate attribution: {e}")
            return {}
    
    # ==================== Budget Optimization ====================
    
    async def reallocate_budget(self, business_id: str, total_budget: float) -> Dict[str, float]:
        """Reallocate budget across channels based on performance"""
        try:
            # Get channel performance data
            channel_performance = await self._get_channel_performance(business_id)
            
            if not channel_performance:
                # Equal distribution if no performance data
                return self._equal_budget_distribution(total_budget)
            
            # Calculate average ROI
            rois = [perf['roi'] for perf in channel_performance.values() if perf['roi'] > 0]
            avg_roi = sum(rois) / len(rois) if rois else 1.0
            
            # Identify underperforming channels
            underperforming = {
                channel: perf for channel, perf in channel_performance.items()
                if perf['roi'] < avg_roi * self.underperformance_threshold
            }
            
            # Calculate new budget allocation
            new_allocation = {}
            remaining_budget = total_budget
            
            # First, allocate minimum budget to all channels
            for channel in channel_performance.keys():
                min_budget = total_budget * (self.min_budget_percentage / 100)
                new_allocation[channel] = min_budget
                remaining_budget -= min_budget
            
            # Distribute remaining budget based on ROI performance
            total_roi = sum(perf['roi'] for perf in channel_performance.values())
            
            if total_roi > 0:
                # First pass: distribute based on ROI
                temp_allocation = {}
                for channel, perf in channel_performance.items():
                    # Higher ROI gets more budget
                    roi_share = perf['roi'] / total_roi
                    additional_budget = remaining_budget * roi_share
                    temp_allocation[channel] = new_allocation[channel] + additional_budget
                
                # Second pass: cap at maximum and redistribute excess
                max_budget = total_budget * (self.max_budget_percentage / 100)
                excess_budget = 0
                
                for channel in temp_allocation.keys():
                    if temp_allocation[channel] > max_budget:
                        excess_budget += temp_allocation[channel] - max_budget
                        temp_allocation[channel] = max_budget
                
                # Redistribute excess to channels below max
                if excess_budget > 0:
                    eligible_channels = [ch for ch in temp_allocation.keys() if temp_allocation[ch] < max_budget]
                    if eligible_channels:
                        excess_per_channel = excess_budget / len(eligible_channels)
                        for channel in eligible_channels:
                            temp_allocation[channel] = min(temp_allocation[channel] + excess_per_channel, max_budget)
                
                new_allocation = temp_allocation
            
            # Log reallocation
            logger.info(f"Budget reallocated for business {business_id}: {new_allocation}")
            
            # Save reallocation record
            await self.db.budget_reallocations.insert_one({
                'business_id': business_id,
                'total_budget': total_budget,
                'allocation': new_allocation,
                'avg_roi': avg_roi,
                'underperforming_channels': list(underperforming.keys()),
                'reallocated_at': datetime.now(timezone.utc).isoformat()
            })
            
            return new_allocation
            
        except Exception as e:
            logger.error(f"Failed to reallocate budget: {e}")
            return self._equal_budget_distribution(total_budget)
    
    async def _get_channel_performance(self, business_id: str) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all channels"""
        try:
            # Get campaigns for this business
            campaigns = await self.db.campaigns.find(
                {'business_id': business_id, 'status': 'active'}
            ).to_list(length=100)
            
            if not campaigns:
                return {}
            
            # Aggregate performance by channel
            channel_performance = {}
            
            for campaign in campaigns:
                for channel in campaign.get('channels', []):
                    if channel not in channel_performance:
                        channel_performance[channel] = {
                            'spend': 0,
                            'revenue': 0,
                            'roi': 0,
                            'conversions': 0
                        }
                    
                    perf = campaign.get('performance', {})
                    channel_performance[channel]['spend'] += perf.get('spend', 0)
                    channel_performance[channel]['revenue'] += perf.get('revenue', 0)
                    channel_performance[channel]['conversions'] += perf.get('conversions', 0)
            
            # Calculate ROI for each channel
            for channel, perf in channel_performance.items():
                if perf['spend'] > 0:
                    perf['roi'] = perf['revenue'] / perf['spend']
                else:
                    perf['roi'] = 0
            
            return channel_performance
            
        except Exception as e:
            logger.error(f"Failed to get channel performance: {e}")
            return {}
    
    def _equal_budget_distribution(self, total_budget: float) -> Dict[str, float]:
        """Distribute budget equally across all channels"""
        channels = ['SEO', 'Google Ads', 'Facebook Ads', 'Social Media', 'Email']
        budget_per_channel = total_budget / len(channels)
        return {channel: budget_per_channel for channel in channels}
    
    # ==================== Mock Data Helpers ====================
    
    def _get_mock_keyword_tracking(self, business_id: str) -> List[Dict[str, Any]]:
        """Generate mock keyword tracking data"""
        return [
            {
                'business_id': business_id,
                'keyword': 'marketing automation',
                'position': 12,
                'search_volume': 5400,
                'difficulty': 65,
                'trend': 'up',
                'last_updated': datetime.now(timezone.utc).isoformat()
            },
            {
                'business_id': business_id,
                'keyword': 'growth hacking',
                'position': 8,
                'search_volume': 3200,
                'difficulty': 58,
                'trend': 'stable',
                'last_updated': datetime.now(timezone.utc).isoformat()
            },
            {
                'business_id': business_id,
                'keyword': 'digital marketing strategy',
                'position': 15,
                'search_volume': 8100,
                'difficulty': 72,
                'trend': 'up',
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        ]


# Global instance
multi_channel_manager = None
