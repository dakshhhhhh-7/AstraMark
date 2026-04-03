"""
Predictive Revenue System
Forecasts revenue and ROI before campaign launch
"""
import logging
import uuid
import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import statistics

logger = logging.getLogger(__name__)

class PredictiveRevenueSystem:
    """
    Predictive Revenue System
    Calculates expected ROI and forecasts revenue with confidence intervals
    """
    
    def __init__(self, db, growth_engine):
        self.db = db
        self.growth_engine = growth_engine
        
        # Industry benchmarks for different channels (default values)
        self.channel_benchmarks = {
            'google_ads': {
                'avg_cpc': 1.5,
                'avg_conversion_rate': 0.03,
                'avg_roi': 2.0,
                'confidence_factor': 0.85
            },
            'google ads': {
                'avg_cpc': 1.5,
                'avg_conversion_rate': 0.03,
                'avg_roi': 2.0,
                'confidence_factor': 0.85
            },
            'facebook_ads': {
                'avg_cpc': 1.2,
                'avg_conversion_rate': 0.025,
                'avg_roi': 1.8,
                'confidence_factor': 0.80
            },
            'facebook ads': {
                'avg_cpc': 1.2,
                'avg_conversion_rate': 0.025,
                'avg_roi': 1.8,
                'confidence_factor': 0.80
            },
            'email': {
                'avg_cpc': 0.1,
                'avg_conversion_rate': 0.05,
                'avg_roi': 3.5,
                'confidence_factor': 0.90
            },
            'seo': {
                'avg_cpc': 0.5,
                'avg_conversion_rate': 0.04,
                'avg_roi': 2.5,
                'confidence_factor': 0.75
            },
            'social': {
                'avg_cpc': 0.8,
                'avg_conversion_rate': 0.02,
                'avg_roi': 1.5,
                'confidence_factor': 0.70
            },
            'social media': {
                'avg_cpc': 0.8,
                'avg_conversion_rate': 0.02,
                'avg_roi': 1.5,
                'confidence_factor': 0.70
            }
        }
        
        # Default average order value (can be customized per business)
        self.default_aov = 50
    
    async def calculate_roi(self, business_id: str, budget: float, channels: List[str]) -> Dict[str, Any]:
        """
        Calculate expected ROI for proposed campaigns
        
        **Validates: Requirements 5.1, 5.2, 5.4**
        """
        try:
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            # Get historical campaign data for this business
            historical_campaigns = await self.db.campaigns.find({
                'business_id': business_id,
                'status': {'$in': ['completed', 'active']}
            }).to_list(length=50)
            
            # Normalize channel names
            normalized_channels = [self._normalize_channel_name(ch) for ch in channels]
            
            # Calculate per-channel projections
            breakdown_by_channel = {}
            total_expected_revenue = 0
            total_confidence_scores = []
            assumptions = []
            
            # Distribute budget across channels (equal distribution for now)
            budget_per_channel = budget / len(normalized_channels) if normalized_channels else budget
            
            for channel in normalized_channels:
                channel_projection = await self._calculate_channel_roi(
                    business_id,
                    channel,
                    budget_per_channel,
                    historical_campaigns,
                    business
                )
                
                breakdown_by_channel[channel] = {
                    'revenue': channel_projection['revenue'],
                    'roi': channel_projection['roi']
                }
                
                total_expected_revenue += channel_projection['revenue']
                total_confidence_scores.append(channel_projection['confidence'])
                assumptions.extend(channel_projection['assumptions'])
            
            # Calculate overall confidence level
            avg_confidence = statistics.mean(total_confidence_scores) if total_confidence_scores else 70
            confidence_level = max(0, min(100, int(avg_confidence)))
            
            # Calculate revenue range with confidence intervals
            # Use ±20% for min/max range
            expected_revenue_min = total_expected_revenue * 0.8
            expected_revenue_max = total_expected_revenue * 1.2
            
            # Calculate ROI percentage
            expected_roi_percentage = ((total_expected_revenue - budget) / budget * 100) if budget > 0 else 0
            
            # Estimate timeline (3-6 months typical)
            timeline_months = self._estimate_timeline(budget, normalized_channels)
            
            projection = {
                'investment': budget,
                'expected_revenue_min': expected_revenue_min,
                'expected_revenue_max': expected_revenue_max,
                'expected_roi_percentage': expected_roi_percentage,
                'confidence_level': confidence_level,
                'timeline_months': timeline_months,
                'breakdown_by_channel': breakdown_by_channel,
                'assumptions': list(set(assumptions))  # Remove duplicates
            }
            
            # Save projection to database
            projection_record = {
                'id': str(uuid.uuid4()),
                'business_id': business_id,
                **projection,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            await self.db.revenue_projections.insert_one(projection_record.copy())
            
            logger.info(f"ROI calculation complete for business {business_id}: {expected_roi_percentage:.1f}% expected ROI")
            return projection
            
        except Exception as e:
            logger.error(f"Failed to calculate ROI for business {business_id}: {e}", exc_info=True)
            return {}
    
    async def project_revenue(self, business_id: str, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Project revenue for a specific campaign configuration
        
        **Validates: Requirements 5.2, 5.3**
        """
        try:
            budget = campaign_config.get('budget', 0)
            channels = campaign_config.get('channels', [])
            
            # Use calculate_roi for the projection
            projection = await self.calculate_roi(business_id, budget, channels)
            
            if not projection:
                return {}
            
            # Add formatted display text
            projection['display_text'] = f"Spend ₹{budget:,.0f} → Expected ₹{projection['expected_revenue_min']:,.0f}-₹{projection['expected_revenue_max']:,.0f} return"
            
            return projection
            
        except Exception as e:
            logger.error(f"Failed to project revenue for business {business_id}: {e}", exc_info=True)
            return {}
    
    async def forecast_growth(self, business_id: str, months: int) -> List[Dict[str, Any]]:
        """
        Forecast monthly revenue growth
        
        **Validates: Requirements 5.5, 5.6, 5.7**
        """
        try:
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return []
            
            # Get historical campaign data
            historical_campaigns = await self.db.campaigns.find({
                'business_id': business_id,
                'status': {'$in': ['completed', 'active']}
            }).sort('created_at', -1).to_list(length=50)
            
            # Calculate baseline monthly revenue from recent campaigns
            baseline_revenue = 0
            if historical_campaigns:
                recent_revenue = sum(c.get('performance', {}).get('revenue', 0) for c in historical_campaigns[:3])
                baseline_revenue = recent_revenue / 3 if len(historical_campaigns) >= 3 else recent_revenue
            else:
                # Use business budget as baseline if no historical data
                baseline_revenue = business.get('monthly_budget', 10000) * 1.5
            
            # Calculate growth rate based on historical performance
            growth_rate = await self._calculate_growth_rate(historical_campaigns)
            
            # Generate monthly forecasts
            forecasts = []
            current_revenue = baseline_revenue
            
            for month in range(1, months + 1):
                # Apply growth rate with some variance
                current_revenue = current_revenue * (1 + growth_rate)
                
                # Add seasonal adjustment (simplified)
                seasonal_factor = self._get_seasonal_factor(month)
                adjusted_revenue = current_revenue * seasonal_factor
                
                forecast = {
                    'month': month,
                    'date': (datetime.now(timezone.utc) + timedelta(days=30 * month)).strftime('%Y-%m'),
                    'projected_revenue': adjusted_revenue,
                    'growth_rate': growth_rate * 100,
                    'confidence': max(50, 90 - (month * 5))  # Confidence decreases over time
                }
                
                forecasts.append(forecast)
            
            logger.info(f"Generated {len(forecasts)} month forecast for business {business_id}")
            return forecasts
            
        except Exception as e:
            logger.error(f"Failed to forecast growth for business {business_id}: {e}", exc_info=True)
            return []
    
    async def calculate_timeline(self, business_id: str, target_revenue: float) -> Dict[str, Any]:
        """
        Calculate timeline to reach revenue goal
        
        **Validates: Requirements 5.8**
        """
        try:
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                logger.warning(f"Business not found: {business_id}")
                return {}
            
            # Get current revenue baseline
            historical_campaigns = await self.db.campaigns.find({
                'business_id': business_id,
                'status': {'$in': ['completed', 'active']}
            }).sort('created_at', -1).to_list(length=10)
            
            current_revenue = 0
            if historical_campaigns:
                recent_revenue = sum(c.get('performance', {}).get('revenue', 0) for c in historical_campaigns[:3])
                current_revenue = recent_revenue / 3 if len(historical_campaigns) >= 3 else recent_revenue
            else:
                # Assume starting from zero if no historical data
                current_revenue = 0
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(historical_campaigns)
            
            # If already at or above target
            if current_revenue >= target_revenue:
                return {
                    'target_revenue': target_revenue,
                    'current_revenue': current_revenue,
                    'timeline_months': 0,
                    'status': 'already_achieved',
                    'message': 'Target revenue already achieved'
                }
            
            # Calculate months needed to reach target
            # Using compound growth formula: target = current * (1 + rate)^months
            # Solving for months: months = log(target/current) / log(1 + rate)
            if growth_rate > 0 and current_revenue > 0:
                months_needed = math.log(target_revenue / current_revenue) / math.log(1 + growth_rate)
                timeline_months = max(1, int(math.ceil(months_needed)))
            else:
                # If no growth rate or starting from zero, use conservative estimate
                monthly_budget = business.get('monthly_budget', 10000)
                estimated_monthly_revenue = monthly_budget * 1.5  # Assume 1.5x ROI
                timeline_months = max(1, int(math.ceil(target_revenue / estimated_monthly_revenue)))
            
            # Cap at reasonable maximum (24 months)
            timeline_months = min(timeline_months, 24)
            
            # Calculate milestones
            milestones = []
            revenue_gap = target_revenue - current_revenue
            milestone_interval = timeline_months // 4 if timeline_months >= 4 else 1
            
            for i in range(1, 5):
                milestone_month = milestone_interval * i
                if milestone_month <= timeline_months:
                    milestone_revenue = current_revenue + (revenue_gap * (i / 4))
                    milestones.append({
                        'month': milestone_month,
                        'revenue': milestone_revenue,
                        'percentage_complete': (i / 4) * 100
                    })
            
            timeline = {
                'target_revenue': target_revenue,
                'current_revenue': current_revenue,
                'revenue_gap': revenue_gap,
                'timeline_months': timeline_months,
                'estimated_completion_date': (datetime.now(timezone.utc) + timedelta(days=30 * timeline_months)).strftime('%Y-%m-%d'),
                'growth_rate_required': growth_rate * 100,
                'milestones': milestones,
                'confidence': 75 if historical_campaigns else 60
            }
            
            logger.info(f"Timeline calculation complete for business {business_id}: {timeline_months} months to reach ₹{target_revenue:,.0f}")
            return timeline
            
        except Exception as e:
            logger.error(f"Failed to calculate timeline for business {business_id}: {e}", exc_info=True)
            return {}
    
    async def _calculate_channel_roi(
        self,
        business_id: str,
        channel: str,
        budget: float,
        historical_campaigns: List[Dict[str, Any]],
        business: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate ROI projection for a specific channel"""
        try:
            # Get channel benchmark
            benchmark = self.channel_benchmarks.get(channel.lower(), {
                'avg_cpc': 1.0,
                'avg_conversion_rate': 0.03,
                'avg_roi': 2.0,
                'confidence_factor': 0.70
            })
            
            # Check if we have historical data for this channel
            channel_campaigns = [
                c for c in historical_campaigns
                if channel.lower() in [ch.lower() for ch in c.get('channels', [])]
            ]
            
            if channel_campaigns:
                # Use historical performance
                avg_roi = statistics.mean([
                    c.get('performance', {}).get('roi', benchmark['avg_roi'])
                    for c in channel_campaigns
                ])
                confidence = min(95, 70 + len(channel_campaigns) * 5)
            else:
                # Use industry benchmark
                avg_roi = benchmark['avg_roi']
                confidence = benchmark['confidence_factor'] * 100
            
            # Calculate projected revenue
            projected_revenue = budget * avg_roi
            
            # Get average order value
            aov = business.get('average_order_value', self.default_aov)
            
            # Calculate assumptions
            avg_cpc = benchmark['avg_cpc']
            conversion_rate = benchmark['avg_conversion_rate']
            estimated_clicks = budget / avg_cpc if avg_cpc > 0 else 0
            estimated_conversions = estimated_clicks * conversion_rate
            
            assumptions = [
                f"Average CPC: ₹{avg_cpc:.2f}",
                f"Conversion rate: {conversion_rate * 100:.1f}%",
                f"Average order value: ₹{aov:.0f}",
                f"Estimated clicks: {estimated_clicks:.0f}",
                f"Estimated conversions: {estimated_conversions:.0f}"
            ]
            
            return {
                'revenue': projected_revenue,
                'roi': avg_roi,
                'confidence': confidence,
                'assumptions': assumptions
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate channel ROI: {e}")
            # Return conservative estimate
            return {
                'revenue': budget * 1.5,
                'roi': 1.5,
                'confidence': 60,
                'assumptions': ["Based on conservative industry estimates"]
            }
    
    async def _calculate_growth_rate(self, historical_campaigns: List[Dict[str, Any]]) -> float:
        """Calculate historical growth rate from campaigns"""
        try:
            if len(historical_campaigns) < 2:
                # Default growth rate if insufficient data
                return 0.10  # 10% monthly growth
            
            # Calculate revenue trend from recent campaigns
            revenues = [c.get('performance', {}).get('revenue', 0) for c in historical_campaigns[:6]]
            revenues = [r for r in revenues if r > 0]  # Filter out zero revenues
            
            if len(revenues) < 2:
                return 0.10
            
            # Calculate average growth rate between consecutive campaigns
            growth_rates = []
            for i in range(len(revenues) - 1):
                if revenues[i] > 0:
                    rate = (revenues[i] - revenues[i + 1]) / revenues[i + 1]
                    growth_rates.append(rate)
            
            if growth_rates:
                avg_growth = statistics.mean(growth_rates)
                # Cap growth rate at reasonable bounds (-10% to +30%)
                return max(-0.10, min(0.30, avg_growth))
            
            return 0.10
            
        except Exception as e:
            logger.error(f"Failed to calculate growth rate: {e}")
            return 0.10
    
    def _estimate_timeline(self, budget: float, channels: List[str]) -> int:
        """Estimate timeline in months based on budget and channels"""
        try:
            # Base timeline on budget size
            if budget < 5000:
                base_months = 6
            elif budget < 20000:
                base_months = 4
            else:
                base_months = 3
            
            # Adjust based on number of channels (more channels = faster results)
            channel_factor = max(0.7, 1 - (len(channels) * 0.1))
            
            timeline = int(base_months * channel_factor)
            return max(1, min(12, timeline))  # Between 1 and 12 months
            
        except Exception as e:
            logger.error(f"Failed to estimate timeline: {e}")
            return 3
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal adjustment factor for a given month"""
        # Simplified seasonal factors (1.0 = average)
        # In reality, this would be industry and region specific
        seasonal_factors = {
            1: 0.95,   # January - post-holiday slowdown
            2: 0.98,   # February
            3: 1.02,   # March - Q1 end push
            4: 1.00,   # April
            5: 1.03,   # May
            6: 1.05,   # June - mid-year push
            7: 0.97,   # July - summer slowdown
            8: 0.96,   # August
            9: 1.02,   # September - back to business
            10: 1.04,  # October - Q4 start
            11: 1.08,  # November - holiday season
            12: 1.10   # December - year-end push
        }
        
        # Get month in cycle (1-12)
        month_in_year = ((month - 1) % 12) + 1
        return seasonal_factors.get(month_in_year, 1.0)
    
    def _normalize_channel_name(self, channel: str) -> str:
        """Normalize channel name to match benchmark keys"""
        channel_lower = channel.lower().strip()
        
        # Map common variations to standard names
        channel_map = {
            'google': 'google_ads',
            'googleads': 'google_ads',
            'google ads': 'google_ads',
            'facebook': 'facebook_ads',
            'facebookads': 'facebook_ads',
            'facebook ads': 'facebook_ads',
            'meta': 'facebook_ads',
            'social media': 'social',
            'socialmedia': 'social'
        }
        
        return channel_map.get(channel_lower, channel_lower)


# Global instance
predictive_revenue_system = None
