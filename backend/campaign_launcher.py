"""
One-Click Campaign Launcher
Automatically creates and deploys complete marketing campaigns
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class CampaignLauncher:
    """One-click campaign creation and deployment"""
    
    def __init__(self, db, growth_engine):
        self.db = db
        self.growth_engine = growth_engine
    
    async def launch_campaign(self, business_id: str, goal: str, channels: List[str], budget: float = 0) -> Dict[str, Any]:
        """Launch a complete campaign with one click"""
        campaign_id = str(uuid.uuid4())
        deployed_channels = []
        
        try:
            # Generate all campaign assets
            logger.info(f"Generating campaign assets for campaign {campaign_id}")
            assets = await self.growth_engine.generate_campaign_assets(goal, business_id)
            
            if not assets:
                raise Exception("Failed to generate campaign assets")
            
            # Validate assets completeness
            if not self._validate_assets(assets):
                raise Exception("Generated assets are incomplete")
            
            # Create campaign record with draft status
            campaign = {
                'id': campaign_id,
                'business_id': business_id,
                'name': assets.get('campaign_name', f'Campaign: {goal}'),
                'goal': goal,
                'channels': channels,
                'assets': assets,
                'status': 'draft',
                'total_budget': budget,
                'budget_allocation': assets.get('budget_allocation', {}),
                'spent': 0,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'created_by': 'user',
                'version': 0,
                'performance': {
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'spend': 0,
                    'revenue': 0,
                    'roi': 0
                }
            }
            
            # Save to database
            await self.db.campaigns.insert_one(campaign.copy())
            logger.info(f"Campaign {campaign_id} created in draft status")
            
            # Deploy to channels
            deployment_results = []
            for channel in channels:
                try:
                    result_deploy = await self._deploy_to_channel(campaign_id, channel, assets)
                    deployment_results.append(result_deploy)
                    
                    if result_deploy['status'] == 'deployed':
                        deployed_channels.append(channel)
                    else:
                        # Deployment failed, trigger rollback
                        logger.error(f"Deployment to {channel} failed, initiating rollback")
                        await self._rollback_deployments(campaign_id, deployed_channels)
                        raise Exception(f"Deployment to {channel} failed: {result_deploy.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Error deploying to {channel}: {e}")
                    # Rollback all successful deployments
                    await self._rollback_deployments(campaign_id, deployed_channels)
                    raise Exception(f"Campaign deployment failed at {channel}: {str(e)}")
            
            # All deployments successful, update campaign status to active
            await self.db.campaigns.update_one(
                {'id': campaign_id},
                {
                    '$set': {
                        'status': 'active',
                        'launched_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(f"Campaign {campaign_id} launched successfully to all channels")
            
            # Return without ObjectId
            return {
                'campaign_id': campaign_id,
                'status': 'launched',
                'assets': assets,
                'deployments': deployment_results
            }
            
        except Exception as e:
            logger.error(f"Campaign launch failed: {e}", exc_info=True)
            
            # Update campaign status to failed
            await self.db.campaigns.update_one(
                {'id': campaign_id},
                {
                    '$set': {
                        'status': 'failed',
                        'error': str(e),
                        'failed_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            raise Exception(f"Campaign launch failed: {str(e)}")
    
    def _validate_assets(self, assets: Dict[str, Any]) -> bool:
        """Validate that all required campaign assets are present"""
        required_keys = ['landing_page', 'ad_creatives', 'email_sequence', 'targeting', 'budget_allocation']
        
        # Check all required keys exist
        if not all(key in assets for key in required_keys):
            logger.error(f"Missing required asset keys. Required: {required_keys}, Got: {list(assets.keys())}")
            return False
        
        # Validate email sequence has at least 3 emails
        if not isinstance(assets['email_sequence'], list) or len(assets['email_sequence']) < 3:
            logger.error(f"Email sequence must have at least 3 emails, got {len(assets.get('email_sequence', []))}")
            return False
        
        # Validate ad_creatives has at least 1 creative
        if not isinstance(assets['ad_creatives'], list) or len(assets['ad_creatives']) < 1:
            logger.error("Ad creatives must have at least 1 creative")
            return False
        
        return True
    
    async def _deploy_to_channel(self, campaign_id: str, channel: str, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy campaign to specific channel"""
        try:
            logger.info(f"Deploying campaign {campaign_id} to {channel}")
            
            # Channel-specific deployment logic
            if channel.lower() in ['google ads', 'google', 'googleads']:
                result = await self._deploy_google_ads(campaign_id, assets)
            elif channel.lower() in ['facebook ads', 'facebook', 'facebookads', 'meta']:
                result = await self._deploy_facebook_ads(campaign_id, assets)
            elif channel.lower() in ['email', 'email marketing']:
                result = await self._deploy_email(campaign_id, assets)
            else:
                # Generic deployment for other channels
                result = await self._deploy_generic(campaign_id, channel, assets)
            
            # Save deployment record
            deployment = {
                'campaign_id': campaign_id,
                'channel': channel,
                'status': result['status'],
                'deployed_at': datetime.now(timezone.utc).isoformat(),
                'deployment_id': result.get('deployment_id'),
                'error': result.get('error')
            }
            await self.db.campaign_deployments.insert_one(deployment.copy())
            
            # Log deployment
            if result['status'] == 'deployed':
                logger.info(f"Successfully deployed campaign {campaign_id} to {channel}")
            else:
                logger.error(f"Failed to deploy campaign {campaign_id} to {channel}: {result.get('error')}")
            
            # Return clean dict without MongoDB result
            return {
                'channel': channel,
                'status': result['status'],
                'deployed_at': deployment['deployed_at'],
                'deployment_id': result.get('deployment_id'),
                'error': result.get('error')
            }
            
        except Exception as e:
            logger.error(f"Channel deployment failed for {channel}: {e}", exc_info=True)
            
            # Save failed deployment record
            deployment = {
                'campaign_id': campaign_id,
                'channel': channel,
                'status': 'failed',
                'deployed_at': datetime.now(timezone.utc).isoformat(),
                'error': str(e)
            }
            await self.db.campaign_deployments.insert_one(deployment.copy())
            
            return {
                'channel': channel,
                'status': 'failed',
                'error': str(e)
            }
    
    async def _deploy_google_ads(self, campaign_id: str, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy campaign to Google Ads"""
        try:
            # Extract Google Ads specific creatives
            google_creatives = [
                creative for creative in assets.get('ad_creatives', [])
                if creative.get('platform', '').lower() in ['google', 'google ads']
            ]
            
            if not google_creatives:
                # Use first creative if no Google-specific creative found
                google_creatives = assets.get('ad_creatives', [])[:1]
            
            # Simulated Google Ads API call
            # In production, this would use the Google Ads API
            deployment_id = f"google_ads_{campaign_id}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Google Ads deployment simulated: {deployment_id}")
            
            return {
                'status': 'deployed',
                'deployment_id': deployment_id,
                'creatives_deployed': len(google_creatives)
            }
            
        except Exception as e:
            logger.error(f"Google Ads deployment failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _deploy_facebook_ads(self, campaign_id: str, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy campaign to Facebook Ads"""
        try:
            # Extract Facebook Ads specific creatives
            facebook_creatives = [
                creative for creative in assets.get('ad_creatives', [])
                if creative.get('platform', '').lower() in ['facebook', 'facebook ads', 'meta']
            ]
            
            if not facebook_creatives:
                # Use first creative if no Facebook-specific creative found
                facebook_creatives = assets.get('ad_creatives', [])[:1]
            
            # Simulated Facebook Ads API call
            # In production, this would use the Facebook Marketing API
            deployment_id = f"facebook_ads_{campaign_id}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Facebook Ads deployment simulated: {deployment_id}")
            
            return {
                'status': 'deployed',
                'deployment_id': deployment_id,
                'creatives_deployed': len(facebook_creatives)
            }
            
        except Exception as e:
            logger.error(f"Facebook Ads deployment failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _deploy_email(self, campaign_id: str, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy email campaign"""
        try:
            email_sequence = assets.get('email_sequence', [])
            
            if len(email_sequence) < 3:
                raise Exception("Email sequence must have at least 3 emails")
            
            # Simulated email service provider API call
            # In production, this would use SendGrid, Mailchimp, etc.
            deployment_id = f"email_{campaign_id}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Email campaign deployment simulated: {deployment_id}")
            
            return {
                'status': 'deployed',
                'deployment_id': deployment_id,
                'emails_scheduled': len(email_sequence)
            }
            
        except Exception as e:
            logger.error(f"Email deployment failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _deploy_generic(self, campaign_id: str, channel: str, assets: Dict[str, Any]) -> Dict[str, Any]:
        """Generic deployment for other channels"""
        try:
            # Simulated deployment for other channels (SEO, Social, etc.)
            deployment_id = f"{channel.lower().replace(' ', '_')}_{campaign_id}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"{channel} deployment simulated: {deployment_id}")
            
            return {
                'status': 'deployed',
                'deployment_id': deployment_id
            }
            
        except Exception as e:
            logger.error(f"{channel} deployment failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _rollback_deployments(self, campaign_id: str, deployed_channels: List[str]) -> None:
        """Rollback deployments for failed campaign launch"""
        logger.warning(f"Rolling back deployments for campaign {campaign_id}: {deployed_channels}")
        
        for channel in deployed_channels:
            try:
                await self._rollback_channel(campaign_id, channel)
                logger.info(f"Rolled back {channel} deployment for campaign {campaign_id}")
            except Exception as e:
                logger.error(f"Failed to rollback {channel} for campaign {campaign_id}: {e}")
        
        # Update deployment records to rolled back status
        await self.db.campaign_deployments.update_many(
            {'campaign_id': campaign_id, 'channel': {'$in': deployed_channels}},
            {
                '$set': {
                    'status': 'rolled_back',
                    'rolled_back_at': datetime.now(timezone.utc).isoformat()
                }
            }
        )
    
    async def _rollback_channel(self, campaign_id: str, channel: str) -> None:
        """Rollback deployment for a specific channel"""
        try:
            # Get deployment record
            deployment = await self.db.campaign_deployments.find_one({
                'campaign_id': campaign_id,
                'channel': channel
            })
            
            if not deployment:
                logger.warning(f"No deployment record found for {channel} in campaign {campaign_id}")
                return
            
            deployment_id = deployment.get('deployment_id')
            
            # Channel-specific rollback logic
            if channel.lower() in ['google ads', 'google', 'googleads']:
                await self._rollback_google_ads(deployment_id)
            elif channel.lower() in ['facebook ads', 'facebook', 'facebookads', 'meta']:
                await self._rollback_facebook_ads(deployment_id)
            elif channel.lower() in ['email', 'email marketing']:
                await self._rollback_email(deployment_id)
            else:
                await self._rollback_generic(channel, deployment_id)
                
        except Exception as e:
            logger.error(f"Rollback failed for {channel}: {e}")
            raise
    
    async def _rollback_google_ads(self, deployment_id: Optional[str]) -> None:
        """Rollback Google Ads deployment"""
        # Simulated Google Ads API call to pause/delete campaign
        logger.info(f"Google Ads rollback simulated for deployment {deployment_id}")
    
    async def _rollback_facebook_ads(self, deployment_id: Optional[str]) -> None:
        """Rollback Facebook Ads deployment"""
        # Simulated Facebook Ads API call to pause/delete campaign
        logger.info(f"Facebook Ads rollback simulated for deployment {deployment_id}")
    
    async def _rollback_email(self, deployment_id: Optional[str]) -> None:
        """Rollback email campaign"""
        # Simulated email service API call to cancel scheduled emails
        logger.info(f"Email campaign rollback simulated for deployment {deployment_id}")
    
    async def _rollback_generic(self, channel: str, deployment_id: Optional[str]) -> None:
        """Generic rollback for other channels"""
        logger.info(f"{channel} rollback simulated for deployment {deployment_id}")
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign status and performance"""
        try:
            campaign = await self.db.campaigns.find_one({'id': campaign_id})
            if not campaign:
                return {}
            
            # Get deployment status
            deployments = await self.db.campaign_deployments.find(
                {'campaign_id': campaign_id}
            ).to_list(length=100)
            
            # Convert MongoDB ObjectId to string for JSON serialization
            if '_id' in campaign:
                campaign['_id'] = str(campaign['_id'])
            
            # Recursively convert any nested ObjectIds
            def convert_objectids(obj):
                if isinstance(obj, dict):
                    return {k: convert_objectids(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_objectids(item) for item in obj]
                elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'ObjectId':
                    return str(obj)
                return obj
            
            campaign = convert_objectids(campaign)
            
            # Add deployment information
            campaign['deployments'] = [
                {
                    'channel': d.get('channel'),
                    'status': d.get('status'),
                    'deployed_at': d.get('deployed_at'),
                    'deployment_id': d.get('deployment_id')
                }
                for d in deployments
            ]
            
            return campaign
            
        except Exception as e:
            logger.error(f"Failed to get campaign status: {e}")
            return {}
    
    async def update_campaign_performance(self, campaign_id: str, performance_data: Dict[str, Any]) -> bool:
        """Update campaign performance metrics"""
        try:
            # Calculate ROI
            spend = performance_data.get('spend', 0)
            revenue = performance_data.get('revenue', 0)
            roi = (revenue / spend) if spend > 0 else 0
            
            performance_data['roi'] = roi
            
            # Update campaign with optimistic locking
            campaign = await self.db.campaigns.find_one({'id': campaign_id})
            if not campaign:
                logger.error(f"Campaign {campaign_id} not found")
                return False
            
            version = campaign.get('version', 0)
            
            result = await self.db.campaigns.update_one(
                {'id': campaign_id, 'version': version},
                {
                    '$set': {
                        'performance': performance_data,
                        'version': version + 1,
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count == 0:
                logger.warning(f"Campaign {campaign_id} was modified by another process")
                return False
            
            logger.info(f"Updated performance for campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update campaign performance: {e}")
            return False
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause an active campaign"""
        try:
            result = await self.db.campaigns.update_one(
                {'id': campaign_id, 'status': 'active'},
                {
                    '$set': {
                        'status': 'paused',
                        'paused_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Campaign {campaign_id} paused")
                return True
            else:
                logger.warning(f"Campaign {campaign_id} not found or not active")
                return False
                
        except Exception as e:
            logger.error(f"Failed to pause campaign: {e}")
            return False
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume a paused campaign"""
        try:
            result = await self.db.campaigns.update_one(
                {'id': campaign_id, 'status': 'paused'},
                {
                    '$set': {
                        'status': 'active',
                        'resumed_at': datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Campaign {campaign_id} resumed")
                return True
            else:
                logger.warning(f"Campaign {campaign_id} not found or not paused")
                return False
                
        except Exception as e:
            logger.error(f"Failed to resume campaign: {e}")
            return False

# Global instance
campaign_launcher = None
