"""
Autonomous Marketing Mode
Runs marketing operations automatically without user intervention
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

class BudgetExceededError(Exception):
    """Raised when autonomous action would exceed budget limit"""
    pass

class CriticalAutonomousError(Exception):
    """Raised when a critical error occurs in autonomous mode"""
    pass

class AutonomousMarketingEngine:
    """Fully automated marketing execution system"""
    
    def __init__(self, db, growth_engine, campaign_launcher):
        self.db = db
        self.growth_engine = growth_engine
        self.campaign_launcher = campaign_launcher
        self.scheduler = AsyncIOScheduler()
        self.active_businesses = {}  # business_id -> config
    
    async def enable_autonomous_mode(self, business_id: str, config: Dict[str, Any]):
        """Enable autonomous mode for a business"""
        try:
            # Validate config
            budget_limit = config.get('budget_limit', 10000)
            if budget_limit <= 0:
                raise ValueError("budget_limit must be greater than 0")
            
            # Extract safety constraints
            safety_constraints = config.get('safety_constraints', {})
            max_daily_spend = safety_constraints.get('max_daily_spend', budget_limit * 0.1)
            min_roi_threshold = safety_constraints.get('min_roi_threshold', 1.5)
            pause_on_negative_roi = safety_constraints.get('pause_on_negative_roi', True)
            
            self.active_businesses[business_id] = {
                'enabled': True,
                'budget_limit': budget_limit,
                'channels': config.get('channels', ['SEO', 'Social', 'Email']),
                'started_at': datetime.now(timezone.utc).isoformat(),
                'safety_constraints': {
                    'max_daily_spend': max_daily_spend,
                    'min_roi_threshold': min_roi_threshold,
                    'pause_on_negative_roi': pause_on_negative_roi
                },
                'total_spent': 0,
                'daily_spent': 0,
                'last_daily_reset': datetime.now(timezone.utc).isoformat()
            }
            
            # Save to database
            await self.db.autonomous_configs.update_one(
                {'business_id': business_id},
                {'$set': {
                    'business_id': business_id,
                    'enabled': True,
                    'config': self.active_businesses[business_id],
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            
            logger.info(f"Autonomous mode enabled for business {business_id} with budget limit {budget_limit}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable autonomous mode: {e}")
            return False
    
    async def disable_autonomous_mode(self, business_id: str, reason: str = "user_requested"):
        """Disable autonomous mode for a business"""
        try:
            if business_id in self.active_businesses:
                del self.active_businesses[business_id]
            
            await self.db.autonomous_configs.update_one(
                {'business_id': business_id},
                {'$set': {
                    'enabled': False,
                    'disabled_reason': reason,
                    'disabled_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }},
                upsert=True
            )
            
            logger.info(f"Autonomous mode disabled for business {business_id}, reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable autonomous mode: {e}")
            return False
    
    async def _check_budget_limit(self, business_id: str, proposed_spend: float) -> bool:
        """Check if proposed spend would exceed budget limits"""
        if business_id not in self.active_businesses:
            return False
        
        config = self.active_businesses[business_id]
        budget_limit = config.get('budget_limit', 0)
        total_spent = config.get('total_spent', 0)
        daily_spent = config.get('daily_spent', 0)
        max_daily_spend = config.get('safety_constraints', {}).get('max_daily_spend', budget_limit * 0.1)
        
        # Check total budget limit
        if total_spent + proposed_spend > budget_limit:
            logger.warning(f"Proposed spend {proposed_spend} would exceed budget limit {budget_limit} for business {business_id}")
            return False
        
        # Check daily spend limit
        if daily_spent + proposed_spend > max_daily_spend:
            logger.warning(f"Proposed spend {proposed_spend} would exceed daily limit {max_daily_spend} for business {business_id}")
            return False
        
        return True
    
    async def _update_spend_tracking(self, business_id: str, spend_amount: float):
        """Update spend tracking for budget enforcement"""
        if business_id not in self.active_businesses:
            return
        
        config = self.active_businesses[business_id]
        
        # Reset daily spend if it's a new day
        last_reset = datetime.fromisoformat(config.get('last_daily_reset', datetime.now(timezone.utc).isoformat()))
        now = datetime.now(timezone.utc)
        
        if now.date() > last_reset.date():
            config['daily_spent'] = 0
            config['last_daily_reset'] = now.isoformat()
        
        # Update spend tracking
        config['total_spent'] = config.get('total_spent', 0) + spend_amount
        config['daily_spent'] = config.get('daily_spent', 0) + spend_amount
        
        # Update in database
        await self.db.autonomous_configs.update_one(
            {'business_id': business_id},
            {'$set': {
                'config.total_spent': config['total_spent'],
                'config.daily_spent': config['daily_spent'],
                'config.last_daily_reset': config['last_daily_reset'],
                'updated_at': now.isoformat()
            }}
        )
        
        logger.info(f"Updated spend tracking for {business_id}: total={config['total_spent']}, daily={config['daily_spent']}")
    
    async def _handle_critical_error(self, business_id: str, error: Exception, context: str):
        """Handle critical errors by pausing autonomous mode and alerting user"""
        logger.critical(f"Critical error in autonomous mode for {business_id}: {error} (context: {context})")
        
        # Disable autonomous mode
        await self.disable_autonomous_mode(business_id, reason=f"critical_error: {context}")
        
        # Log critical error
        await self.db.autonomous_errors.insert_one({
            'business_id': business_id,
            'error_type': 'critical',
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'autonomous_mode_disabled': True
        })
        
        # Create alert for user
        await self.db.alerts.insert_one({
            'business_id': business_id,
            'type': 'critical_error',
            'severity': 'urgent',
            'title': 'Autonomous Mode Disabled',
            'message': f'Autonomous mode was automatically disabled due to a critical error: {str(error)}',
            'context': context,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'read': False
        })
        
        logger.info(f"Autonomous mode disabled and alert created for business {business_id}")
    
    def start(self):
        """Start autonomous marketing scheduler"""
        # Run autonomous campaigns every 6 hours
        self.scheduler.add_job(
            self.run_autonomous_campaigns,
            trigger=IntervalTrigger(hours=6),
            id='autonomous_campaigns',
            name='Autonomous Campaign Runner',
            replace_existing=True
        )
        
        # Optimize active campaigns every hour
        self.scheduler.add_job(
            self.optimize_active_campaigns,
            trigger=IntervalTrigger(hours=1),
            id='campaign_optimizer',
            name='Campaign Optimizer',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Autonomous marketing engine started")
    
    def stop(self):
        """Stop autonomous marketing scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Autonomous marketing engine stopped")
    
    async def run_autonomous_campaigns(self):
        """Execute campaigns automatically for all enabled businesses"""
        logger.info("Starting autonomous campaign execution cycle")
        
        for business_id, config in list(self.active_businesses.items()):
            if not config.get('enabled'):
                continue
            
            try:
                logger.info(f"Running autonomous campaign for business {business_id}")
                
                # Get daily actions
                actions = await self.growth_engine.generate_daily_actions(business_id)
                
                if not actions:
                    logger.warning(f"No actions generated for business {business_id}")
                    continue
                
                # Execute top priority action (highest ROI score)
                top_action = max(actions, key=lambda x: x.get('roi_score', 0))
                
                # Estimate spend for this action (use budget allocation or default)
                estimated_spend = top_action.get('estimated_spend', 500)
                
                # Check budget before executing
                if not await self._check_budget_limit(business_id, estimated_spend):
                    logger.warning(f"Budget limit reached for business {business_id}, skipping action")
                    
                    # Create alert for user
                    await self.db.alerts.insert_one({
                        'business_id': business_id,
                        'type': 'budget_limit_reached',
                        'severity': 'warning',
                        'title': 'Budget Limit Reached',
                        'message': f'Autonomous mode skipped action due to budget limit. Total spent: {config.get("total_spent", 0)}',
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'read': False
                    })
                    continue
                
                # Execute the action
                await self._execute_action(business_id, top_action, estimated_spend)
                
            except CriticalAutonomousError as e:
                # Critical error - disable autonomous mode
                await self._handle_critical_error(business_id, e, "autonomous_campaign_execution")
                
            except Exception as e:
                # Non-critical error - log and continue
                logger.error(f"Error in autonomous campaign for business {business_id}: {e}", exc_info=True)
                
                # Log error but don't disable autonomous mode
                await self.db.autonomous_errors.insert_one({
                    'business_id': business_id,
                    'error_type': 'minor',
                    'error_message': str(e),
                    'context': 'autonomous_campaign_execution',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'autonomous_mode_disabled': False
                })
        
        logger.info("Autonomous campaign execution cycle completed")
    
    async def optimize_active_campaigns(self):
        """Optimize all active campaigns"""
        logger.info("Starting campaign optimization cycle")
        
        for business_id in list(self.active_businesses.keys()):
            try:
                # Get active campaigns for this business
                campaigns = await self.db.campaigns.find(
                    {'business_id': business_id, 'status': 'active'}
                ).to_list(length=100)
                
                if not campaigns:
                    continue
                
                logger.info(f"Optimizing {len(campaigns)} campaigns for business {business_id}")
                
                for campaign in campaigns:
                    try:
                        # Analyze performance
                        performance = campaign.get('performance', {})
                        roi = performance.get('roi', 0)
                        
                        # Get safety constraints
                        config = self.active_businesses.get(business_id, {})
                        min_roi_threshold = config.get('safety_constraints', {}).get('min_roi_threshold', 1.5)
                        pause_on_negative_roi = config.get('safety_constraints', {}).get('pause_on_negative_roi', True)
                        
                        # Check if campaign is underperforming
                        if roi < min_roi_threshold:
                            logger.warning(f"Campaign {campaign.get('id')} underperforming with ROI {roi}")
                            
                            # If ROI is negative and pause_on_negative_roi is enabled, pause campaign
                            if roi < 0 and pause_on_negative_roi:
                                await self.campaign_launcher.pause_campaign(campaign.get('id'))
                                logger.info(f"Paused campaign {campaign.get('id')} due to negative ROI")
                            else:
                                # Otherwise, optimize the campaign
                                await self._optimize_campaign(campaign)
                        
                    except Exception as e:
                        logger.error(f"Error optimizing campaign {campaign.get('id')}: {e}")
                        # Continue with other campaigns
                        continue
                
            except CriticalAutonomousError as e:
                # Critical error - disable autonomous mode
                await self._handle_critical_error(business_id, e, "campaign_optimization")
                
            except Exception as e:
                # Non-critical error - log and continue
                logger.error(f"Error in campaign optimization for business {business_id}: {e}", exc_info=True)
        
        logger.info("Campaign optimization cycle completed")
    
    async def _execute_action(self, business_id: str, action: Dict[str, Any], estimated_spend: float = 0):
        """Execute a specific marketing action with budget enforcement"""
        try:
            # Check budget limit before execution
            if estimated_spend > 0:
                if not await self._check_budget_limit(business_id, estimated_spend):
                    raise BudgetExceededError(f"Action would exceed budget limit")
            
            # Determine action type and execute accordingly
            action_type = action.get('channel', 'general').lower()
            
            # For high-value actions, launch a campaign
            if action.get('roi_score', 0) >= 70:
                try:
                    # Launch campaign with autonomous attribution
                    campaign_result = await self.campaign_launcher.launch_campaign(
                        business_id=business_id,
                        goal=action.get('action', 'Autonomous campaign'),
                        channels=[action.get('channel', 'SEO')],
                        budget=estimated_spend
                    )
                    
                    # Mark campaign as created by autonomous mode
                    if campaign_result and 'campaign_id' in campaign_result:
                        await self.db.campaigns.update_one(
                            {'id': campaign_result['campaign_id']},
                            {'$set': {'created_by': 'autonomous'}}
                        )
                    
                    # Update spend tracking
                    if estimated_spend > 0:
                        await self._update_spend_tracking(business_id, estimated_spend)
                    
                except Exception as e:
                    logger.error(f"Failed to launch autonomous campaign: {e}")
                    # Check if this is a critical error
                    if "deployment failed" in str(e).lower() or "rollback" in str(e).lower():
                        raise CriticalAutonomousError(f"Campaign deployment failed: {e}")
                    raise
            
            # Log action execution
            await self.db.autonomous_actions.insert_one({
                'business_id': business_id,
                'action': action,
                'estimated_spend': estimated_spend,
                'executed_at': datetime.now(timezone.utc).isoformat(),
                'status': 'executed'
            })
            
            logger.info(f"Executed action: {action.get('action')} for business {business_id}")
            
        except BudgetExceededError:
            # Budget exceeded - log but don't treat as critical
            logger.warning(f"Budget exceeded for business {business_id}, action skipped")
            raise
            
        except CriticalAutonomousError:
            # Re-raise critical errors
            raise
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}", exc_info=True)
            # Check if error is critical
            if "database" in str(e).lower() or "connection" in str(e).lower():
                raise CriticalAutonomousError(f"Database error during action execution: {e}")
            raise
    
    async def _optimize_campaign(self, campaign: Dict[str, Any]):
        """Optimize a specific campaign"""
        try:
            campaign_id = campaign.get('id')
            performance = campaign.get('performance', {})
            
            # Calculate optimization adjustments
            roi = performance.get('roi', 0)
            ctr = performance.get('clicks', 0) / max(performance.get('impressions', 1), 1)
            conversion_rate = performance.get('conversions', 0) / max(performance.get('clicks', 1), 1)
            
            # Determine optimization strategy
            optimization_type = None
            if ctr < 0.02:  # Low CTR
                optimization_type = 'creative'
            elif conversion_rate < 0.03:  # Low conversion
                optimization_type = 'targeting'
            elif roi < 1.5:  # Low ROI
                optimization_type = 'budget'
            
            # Update campaign with optimization
            await self.db.campaigns.update_one(
                {'id': campaign_id},
                {'$set': {
                    'optimized_at': datetime.now(timezone.utc).isoformat(),
                    'optimization_count': campaign.get('optimization_count', 0) + 1,
                    'last_optimization_type': optimization_type
                }}
            )
            
            # Log optimization
            await self.db.campaign_optimizations.insert_one({
                'campaign_id': campaign_id,
                'optimization_type': optimization_type,
                'before_metrics': performance,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Optimized campaign {campaign_id} with strategy: {optimization_type}")
            
        except Exception as e:
            logger.error(f"Campaign optimization failed: {e}", exc_info=True)
            # Check if error is critical
            if "database" in str(e).lower():
                raise CriticalAutonomousError(f"Database error during campaign optimization: {e}")
            raise
    
    async def get_autonomous_status(self, business_id: str) -> Dict[str, Any]:
        """Get autonomous mode status and recent actions"""
        try:
            # Get config from database
            config_doc = await self.db.autonomous_configs.find_one({'business_id': business_id})
            
            if not config_doc:
                return {
                    'enabled': False,
                    'config': None,
                    'recent_actions': [],
                    'performance_summary': {}
                }
            
            # Get recent actions
            recent_actions = await self.db.autonomous_actions.find(
                {'business_id': business_id}
            ).sort('executed_at', -1).limit(10).to_list(length=10)
            
            # Get autonomous campaigns
            autonomous_campaigns = await self.db.campaigns.find(
                {'business_id': business_id, 'created_by': 'autonomous'}
            ).to_list(length=100)
            
            # Calculate performance summary
            total_spend = sum(c.get('spent', 0) for c in autonomous_campaigns)
            total_revenue = sum(c.get('performance', {}).get('revenue', 0) for c in autonomous_campaigns)
            avg_roi = (total_revenue / total_spend) if total_spend > 0 else 0
            
            performance_summary = {
                'campaigns_launched': len(autonomous_campaigns),
                'total_spend': total_spend,
                'total_revenue': total_revenue,
                'roi': avg_roi
            }
            
            return {
                'enabled': config_doc.get('enabled', False),
                'config': config_doc.get('config', {}),
                'recent_actions': [
                    {
                        'action': a.get('action', {}).get('action', 'Unknown'),
                        'executed_at': a.get('executed_at'),
                        'result': f"Executed {a.get('action', {}).get('channel', 'action')}"
                    }
                    for a in recent_actions
                ],
                'performance_summary': performance_summary
            }
            
        except Exception as e:
            logger.error(f"Failed to get autonomous status: {e}")
            return {
                'enabled': False,
                'config': None,
                'recent_actions': [],
                'performance_summary': {},
                'error': str(e)
            }

# Global instance
autonomous_engine = None
