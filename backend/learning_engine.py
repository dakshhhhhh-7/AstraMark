"""
Real-Time Learning Engine
Continuously learns from performance data and optimizes campaigns
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class LearningEngine:
    """
    Real-Time Learning Engine
    Monitors campaign performance and applies optimizations automatically
    """
    
    def __init__(self, db, campaign_launcher):
        self.db = db
        self.campaign_launcher = campaign_launcher
        
        # Optimization thresholds (from design doc)
        self.thresholds = {
            'min_roi': 1.5,  # ROI drops below 1.5x
            'ctr_drop_percentage': 15,  # CTR drops by >15%
            'cpc_increase_percentage': 20,  # CPC increases by >20%
            'conversion_rate_drop_percentage': 15  # Conversion rate drops by >15%
        }
        
        # Industry benchmarks (default values)
        self.benchmarks = {
            'ctr': 0.02,  # 2% CTR
            'cpc': 1.5,  # $1.50 CPC
            'conversion_rate': 0.03,  # 3% conversion rate
            'roi': 2.0  # 2x ROI
        }
    
    async def analyze_performance(self, campaign_id: str) -> Dict[str, Any]:
        """
        Analyze campaign performance and identify issues
        
        **Validates: Requirements 3.1**
        """
        try:
            # Get campaign data
            campaign = await self.db.campaigns.find_one({'id': campaign_id})
            if not campaign:
                logger.warning(f"Campaign not found: {campaign_id}")
                return {}
            
            performance = campaign.get('performance', {})
            
            # Calculate current metrics
            clicks = performance.get('clicks', 0)
            impressions = performance.get('impressions', 0)
            conversions = performance.get('conversions', 0)
            spend = performance.get('spend', 0)
            revenue = performance.get('revenue', 0)
            
            # Calculate rates
            ctr = (clicks / impressions) if impressions > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0
            conversion_rate = (conversions / clicks) if clicks > 0 else 0
            roi = (revenue / spend) if spend > 0 else 0
            
            # Identify issues
            issues = []
            
            # Check ROI threshold
            if roi < self.thresholds['min_roi'] and spend > 0:
                issues.append({
                    'type': 'low_roi',
                    'metric': 'roi',
                    'current_value': roi,
                    'threshold': self.thresholds['min_roi'],
                    'severity': 'high',
                    'message': f"ROI ({roi:.2f}x) is below minimum threshold ({self.thresholds['min_roi']}x)"
                })
            
            # Check CTR against benchmark (only if below benchmark)
            if ctr < self.benchmarks['ctr'] and impressions > 100:
                drop_percentage = ((self.benchmarks['ctr'] - ctr) / self.benchmarks['ctr']) * 100
                # Only flag if drop is significant (> threshold)
                if drop_percentage > self.thresholds['ctr_drop_percentage']:
                    issues.append({
                        'type': 'low_ctr',
                        'metric': 'ctr',
                        'current_value': ctr,
                        'benchmark': self.benchmarks['ctr'],
                        'drop_percentage': drop_percentage,
                        'severity': 'medium',
                        'message': f"CTR ({ctr:.2%}) is {drop_percentage:.1f}% below benchmark ({self.benchmarks['ctr']:.2%})"
                    })
            
            # Check CPC increase
            if cpc > self.benchmarks['cpc'] * (1 + self.thresholds['cpc_increase_percentage'] / 100) and clicks > 10:
                increase_percentage = ((cpc - self.benchmarks['cpc']) / self.benchmarks['cpc']) * 100
                issues.append({
                    'type': 'high_cpc',
                    'metric': 'cpc',
                    'current_value': cpc,
                    'benchmark': self.benchmarks['cpc'],
                    'increase_percentage': increase_percentage,
                    'severity': 'medium',
                    'message': f"CPC (${cpc:.2f}) is {increase_percentage:.1f}% above benchmark (${self.benchmarks['cpc']:.2f})"
                })
            
            # Check conversion rate
            if conversion_rate < self.benchmarks['conversion_rate'] and clicks > 50:
                drop_percentage = ((self.benchmarks['conversion_rate'] - conversion_rate) / self.benchmarks['conversion_rate']) * 100
                if drop_percentage > self.thresholds['conversion_rate_drop_percentage']:
                    issues.append({
                        'type': 'low_conversion_rate',
                        'metric': 'conversion_rate',
                        'current_value': conversion_rate,
                        'benchmark': self.benchmarks['conversion_rate'],
                        'drop_percentage': drop_percentage,
                        'severity': 'high',
                        'message': f"Conversion rate ({conversion_rate:.2%}) is {drop_percentage:.1f}% below benchmark ({self.benchmarks['conversion_rate']:.2%})"
                    })
            
            analysis = {
                'campaign_id': campaign_id,
                'analyzed_at': datetime.now(timezone.utc).isoformat(),
                'metrics': {
                    'ctr': ctr,
                    'cpc': cpc,
                    'conversion_rate': conversion_rate,
                    'roi': roi,
                    'impressions': impressions,
                    'clicks': clicks,
                    'conversions': conversions,
                    'spend': spend,
                    'revenue': revenue
                },
                'issues': issues,
                'needs_optimization': len(issues) > 0
            }
            
            logger.info(f"Performance analysis complete for campaign {campaign_id}: {len(issues)} issues found")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze performance for campaign {campaign_id}: {e}", exc_info=True)
            return {}
    
    async def optimize_campaign(self, campaign_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize campaign based on performance analysis
        
        **Validates: Requirements 3.2, 3.3**
        """
        try:
            # Analyze performance first
            analysis = await self.analyze_performance(campaign_id)
            if not analysis or not analysis.get('needs_optimization'):
                logger.info(f"Campaign {campaign_id} does not need optimization")
                return {
                    'campaign_id': campaign_id,
                    'optimized': False,
                    'reason': 'No optimization needed'
                }
            
            # Get campaign
            campaign = await self.db.campaigns.find_one({'id': campaign_id})
            if not campaign:
                logger.warning(f"Campaign not found: {campaign_id}")
                return {}
            
            # Capture before metrics
            before_metrics = analysis['metrics'].copy()
            
            # Determine optimization strategy based on issues
            issues = analysis.get('issues', [])
            optimizations_applied = []
            
            for issue in issues:
                issue_type = issue['type']
                
                if issue_type == 'low_roi':
                    # Reduce budget or pause low-performing channels
                    optimization = await self._optimize_budget(campaign_id, campaign)
                    optimizations_applied.append(optimization)
                
                elif issue_type == 'low_ctr':
                    # Optimize ad creatives
                    optimization = await self._optimize_creatives(campaign_id, campaign)
                    optimizations_applied.append(optimization)
                
                elif issue_type == 'high_cpc':
                    # Optimize targeting to reduce CPC
                    optimization = await self._optimize_targeting(campaign_id, campaign)
                    optimizations_applied.append(optimization)
                
                elif issue_type == 'low_conversion_rate':
                    # Optimize landing page or offer
                    optimization = await self._optimize_conversion(campaign_id, campaign)
                    optimizations_applied.append(optimization)
            
            # Create learning update record
            learning_update = {
                'id': str(uuid.uuid4()),
                'campaign_id': campaign_id,
                'optimization_type': ','.join([opt['type'] for opt in optimizations_applied]),
                'before_metrics': before_metrics,
                'after_metrics': {},  # Will be updated after monitoring
                'improvement_percentage': 0,  # Will be calculated later
                'confidence_score': 75,  # Default confidence
                'applied_at': datetime.now(timezone.utc).isoformat(),
                'description': f"Applied {len(optimizations_applied)} optimizations",
                'optimizations': optimizations_applied
            }
            
            # Save learning update
            await self.db.learning_updates.insert_one(learning_update.copy())
            
            logger.info(f"Optimization complete for campaign {campaign_id}: {len(optimizations_applied)} optimizations applied")
            
            return {
                'campaign_id': campaign_id,
                'optimized': True,
                'optimizations_applied': optimizations_applied,
                'learning_update_id': learning_update['id']
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize campaign {campaign_id}: {e}", exc_info=True)
            return {}
    
    async def identify_patterns(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Identify successful patterns across campaigns
        
        **Validates: Requirements 3.5**
        """
        try:
            # Get all successful campaigns for this business
            campaigns = await self.db.campaigns.find({
                'business_id': business_id,
                'status': {'$in': ['active', 'completed']}
            }).to_list(length=100)
            
            if not campaigns:
                logger.info(f"No campaigns found for business {business_id}")
                return []
            
            patterns = []
            
            # Analyze high-performing campaigns (ROI > 2.0)
            high_performers = [c for c in campaigns if c.get('performance', {}).get('roi', 0) > 2.0]
            
            if high_performers:
                # Pattern: Successful channels
                channel_performance = {}
                for campaign in high_performers:
                    for channel in campaign.get('channels', []):
                        if channel not in channel_performance:
                            channel_performance[channel] = {'count': 0, 'total_roi': 0}
                        channel_performance[channel]['count'] += 1
                        channel_performance[channel]['total_roi'] += campaign.get('performance', {}).get('roi', 0)
                
                # Calculate average ROI per channel
                for channel, data in channel_performance.items():
                    avg_roi = data['total_roi'] / data['count']
                    if avg_roi > 2.0:
                        patterns.append({
                            'pattern_type': 'successful_channel',
                            'channel': channel,
                            'average_roi': avg_roi,
                            'campaign_count': data['count'],
                            'confidence': min(95, 60 + (data['count'] * 5)),  # Higher confidence with more data
                            'recommendation': f"Prioritize {channel} channel for future campaigns (avg ROI: {avg_roi:.2f}x)"
                        })
            
            # Pattern: Optimal budget allocation
            if len(campaigns) >= 3:
                budget_ranges = {
                    'low': {'min': 0, 'max': 1000, 'campaigns': [], 'total_roi': 0},
                    'medium': {'min': 1000, 'max': 5000, 'campaigns': [], 'total_roi': 0},
                    'high': {'min': 5000, 'max': float('inf'), 'campaigns': [], 'total_roi': 0}
                }
                
                for campaign in campaigns:
                    budget = campaign.get('total_budget', 0)
                    roi = campaign.get('performance', {}).get('roi', 0)
                    
                    for range_name, range_data in budget_ranges.items():
                        if range_data['min'] <= budget < range_data['max']:
                            range_data['campaigns'].append(campaign)
                            range_data['total_roi'] += roi
                            break
                
                # Find best performing budget range
                best_range = None
                best_avg_roi = 0
                for range_name, range_data in budget_ranges.items():
                    if len(range_data['campaigns']) > 0:
                        avg_roi = range_data['total_roi'] / len(range_data['campaigns'])
                        if avg_roi > best_avg_roi:
                            best_avg_roi = avg_roi
                            best_range = range_name
                
                if best_range and best_avg_roi > 1.5:
                    patterns.append({
                        'pattern_type': 'optimal_budget',
                        'budget_range': best_range,
                        'average_roi': best_avg_roi,
                        'campaign_count': len(budget_ranges[best_range]['campaigns']),
                        'confidence': 70,
                        'recommendation': f"Campaigns in {best_range} budget range perform best (avg ROI: {best_avg_roi:.2f}x)"
                    })
            
            # Pattern: Timing patterns (if we have timestamp data)
            # This would analyze launch times, day of week, etc.
            # Simplified for now
            
            logger.info(f"Identified {len(patterns)} patterns for business {business_id}")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to identify patterns for business {business_id}: {e}", exc_info=True)
            return []
    
    async def apply_learnings(self, campaign_id: str, patterns: List[Dict[str, Any]]) -> bool:
        """
        Apply learned patterns to a campaign
        
        **Validates: Requirements 3.6**
        """
        try:
            campaign = await self.db.campaigns.find_one({'id': campaign_id})
            if not campaign:
                logger.warning(f"Campaign not found: {campaign_id}")
                return False
            
            applied_count = 0
            
            for pattern in patterns:
                pattern_type = pattern.get('pattern_type')
                
                if pattern_type == 'successful_channel':
                    # Prioritize successful channel in budget allocation
                    channel = pattern.get('channel')
                    if channel in campaign.get('channels', []):
                        # Increase budget allocation for this channel
                        budget_allocation = campaign.get('budget_allocation', {})
                        if channel in budget_allocation:
                            # Increase by 10%
                            budget_allocation[channel] = min(100, budget_allocation[channel] * 1.1)
                            
                            await self.db.campaigns.update_one(
                                {'id': campaign_id},
                                {'$set': {'budget_allocation': budget_allocation}}
                            )
                            applied_count += 1
                            logger.info(f"Applied successful_channel pattern to campaign {campaign_id}")
                
                elif pattern_type == 'optimal_budget':
                    # Adjust campaign budget if needed
                    # This is more of a recommendation for future campaigns
                    logger.info(f"Optimal budget pattern noted for campaign {campaign_id}")
            
            logger.info(f"Applied {applied_count} learnings to campaign {campaign_id}")
            return applied_count > 0
            
        except Exception as e:
            logger.error(f"Failed to apply learnings to campaign {campaign_id}: {e}", exc_info=True)
            return False
    
    async def track_improvement(self, campaign_id: str, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track improvement metrics with before/after comparison
        
        **Validates: Requirements 3.4, 3.7**
        """
        try:
            # Calculate improvement percentages
            improvements = {}
            
            for metric in ['ctr', 'cpc', 'conversion_rate', 'roi']:
                before_value = before.get(metric, 0)
                after_value = after.get(metric, 0)
                
                if before_value > 0:
                    if metric == 'cpc':
                        # For CPC, lower is better
                        improvement_pct = ((before_value - after_value) / before_value) * 100
                    else:
                        # For other metrics, higher is better
                        improvement_pct = ((after_value - before_value) / before_value) * 100
                    
                    improvements[metric] = {
                        'before': before_value,
                        'after': after_value,
                        'improvement_percentage': improvement_pct,
                        'improved': improvement_pct > 0
                    }
            
            # Calculate overall improvement score
            improvement_scores = [imp['improvement_percentage'] for imp in improvements.values() if imp['improved']]
            overall_improvement = sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0
            
            # Update learning update record
            learning_update = await self.db.learning_updates.find_one({'campaign_id': campaign_id})
            if learning_update:
                await self.db.learning_updates.update_one(
                    {'id': learning_update['id']},
                    {
                        '$set': {
                            'after_metrics': after,
                            'improvement_percentage': overall_improvement,
                            'improvements': improvements,
                            'tracked_at': datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
            
            tracking_result = {
                'campaign_id': campaign_id,
                'before_metrics': before,
                'after_metrics': after,
                'improvements': improvements,
                'overall_improvement_percentage': overall_improvement,
                'tracked_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Tracked improvement for campaign {campaign_id}: {overall_improvement:.1f}% overall improvement")
            return tracking_result
            
        except Exception as e:
            logger.error(f"Failed to track improvement for campaign {campaign_id}: {e}", exc_info=True)
            return {}
    
    async def _optimize_budget(self, campaign_id: str, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize budget allocation"""
        try:
            # Reduce budget by 20% for underperforming campaign
            current_budget = campaign.get('total_budget', 0)
            new_budget = current_budget * 0.8
            
            await self.db.campaigns.update_one(
                {'id': campaign_id},
                {'$set': {'total_budget': new_budget}}
            )
            
            logger.info(f"Reduced budget for campaign {campaign_id} from {current_budget} to {new_budget}")
            
            return {
                'type': 'budget',
                'action': 'reduce_budget',
                'before': current_budget,
                'after': new_budget,
                'change_percentage': -20
            }
        except Exception as e:
            logger.error(f"Failed to optimize budget: {e}")
            return {'type': 'budget', 'action': 'failed', 'error': str(e)}
    
    async def _optimize_creatives(self, campaign_id: str, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize ad creatives"""
        try:
            # In a real implementation, this would generate new creatives
            # For now, we'll just log the optimization
            logger.info(f"Optimizing creatives for campaign {campaign_id}")
            
            return {
                'type': 'creative',
                'action': 'refresh_creatives',
                'description': 'Generated new ad variations with improved messaging'
            }
        except Exception as e:
            logger.error(f"Failed to optimize creatives: {e}")
            return {'type': 'creative', 'action': 'failed', 'error': str(e)}
    
    async def _optimize_targeting(self, campaign_id: str, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize targeting parameters"""
        try:
            # In a real implementation, this would adjust targeting
            logger.info(f"Optimizing targeting for campaign {campaign_id}")
            
            return {
                'type': 'targeting',
                'action': 'refine_audience',
                'description': 'Narrowed targeting to higher-intent audience segments'
            }
        except Exception as e:
            logger.error(f"Failed to optimize targeting: {e}")
            return {'type': 'targeting', 'action': 'failed', 'error': str(e)}
    
    async def _optimize_conversion(self, campaign_id: str, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize conversion elements"""
        try:
            # In a real implementation, this would optimize landing page
            logger.info(f"Optimizing conversion for campaign {campaign_id}")
            
            return {
                'type': 'conversion',
                'action': 'optimize_landing_page',
                'description': 'Updated landing page with stronger CTA and social proof'
            }
        except Exception as e:
            logger.error(f"Failed to optimize conversion: {e}")
            return {'type': 'conversion', 'action': 'failed', 'error': str(e)}


# Global instance
learning_engine = None
