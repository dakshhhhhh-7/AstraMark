"""
Competitor Hijacking Engine
Real-time competitor monitoring and counter-strategy generation
"""
import logging
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from apify_market_service import apify_market_service
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

class CompetitorHijackingEngine:
    """
    Tracks competitors in real-time and identifies opportunities to outperform them
    """
    
    def __init__(self, db, growth_engine):
        self.db = db
        self.growth_engine = growth_engine
        self.scheduler = AsyncIOScheduler()
        self.monitoring_active = False
    
    async def add_competitor(self, business_id: str, competitor_url: str) -> str:
        """Add a competitor to monitor"""
        try:
            competitor_id = str(uuid.uuid4())
            
            # Extract domain from URL
            domain = self._extract_domain(competitor_url)
            
            # Initial scan to get competitor data
            initial_data = await self._scan_competitor_website(competitor_url)
            
            competitor = {
                'id': competitor_id,
                'business_id': business_id,
                'name': initial_data.get('name', domain),
                'domain': domain,
                'url': competitor_url,
                'monitoring_since': datetime.now(timezone.utc).isoformat(),
                'last_scan': datetime.now(timezone.utc).isoformat(),
                'metrics': {
                    'estimated_traffic': initial_data.get('estimated_traffic', 'Unknown'),
                    'estimated_ad_spend': initial_data.get('estimated_ad_spend', 'Unknown'),
                    'active_campaigns': initial_data.get('active_campaigns', 0),
                    'top_keywords': initial_data.get('top_keywords', []),
                    'domain_authority': initial_data.get('domain_authority', 0)
                },
                'changes_detected': [],
                'weaknesses': [],
                'strategies': [],
                'website_snapshot': initial_data.get('content', ''),
                'ad_campaigns_snapshot': []
            }
            
            # Save to database
            await self.db.competitors.insert_one(competitor.copy())
            logger.info(f"Added competitor {competitor_id} for business {business_id}")
            
            # Analyze weaknesses and generate strategies
            await self._analyze_and_update_competitor(competitor_id)
            
            return competitor_id
            
        except Exception as e:
            logger.error(f"Failed to add competitor: {e}", exc_info=True)
            raise Exception(f"Failed to add competitor: {str(e)}")
    
    async def monitor_competitors(self, business_id: str) -> List[Dict[str, Any]]:
        """Get all monitored competitors for a business"""
        try:
            competitors = await self.db.competitors.find(
                {'business_id': business_id}
            ).to_list(length=100)
            
            # Remove MongoDB ObjectId
            for competitor in competitors:
                if '_id' in competitor:
                    del competitor['_id']
            
            return competitors
            
        except Exception as e:
            logger.error(f"Failed to get competitors: {e}", exc_info=True)
            return []
    
    async def detect_changes(self, competitor_id: str) -> List[Dict[str, Any]]:
        """Detect changes in competitor's website and campaigns"""
        try:
            competitor = await self.db.competitors.find_one({'id': competitor_id})
            if not competitor:
                logger.warning(f"Competitor {competitor_id} not found")
                return []
            
            changes = []
            
            # Scan current state
            current_data = await self._scan_competitor_website(competitor['url'])
            
            # Compare website content
            old_snapshot = competitor.get('website_snapshot', '')
            new_snapshot = current_data.get('content', '')
            
            if old_snapshot and new_snapshot != old_snapshot:
                # Detect significant changes
                change = {
                    'type': 'website_change',
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    'description': 'Landing page content updated',
                    'impact': 'medium',
                    'details': self._analyze_content_changes(old_snapshot, new_snapshot)
                }
                changes.append(change)
            
            # Check for new campaigns (simulated - would use ad library APIs in production)
            new_campaigns = await self._detect_new_campaigns(competitor)
            if new_campaigns:
                for campaign in new_campaigns:
                    change = {
                        'type': 'new_ad_campaign',
                        'detected_at': datetime.now(timezone.utc).isoformat(),
                        'description': f"Launched new {campaign['platform']} campaign",
                        'impact': 'high',
                        'details': campaign
                    }
                    changes.append(change)
            
            # Update competitor record
            if changes:
                await self.db.competitors.update_one(
                    {'id': competitor_id},
                    {
                        '$set': {
                            'last_scan': datetime.now(timezone.utc).isoformat(),
                            'website_snapshot': new_snapshot
                        },
                        '$push': {
                            'changes_detected': {'$each': changes}
                        }
                    }
                )
                logger.info(f"Detected {len(changes)} changes for competitor {competitor_id}")
            
            return changes
            
        except Exception as e:
            logger.error(f"Failed to detect changes: {e}", exc_info=True)
            return []
    
    async def analyze_landing_page(self, competitor_id: str, url: str) -> Dict[str, Any]:
        """Analyze competitor landing page for weaknesses"""
        try:
            # Scan the landing page
            page_data = await self._scan_competitor_website(url)
            
            # Use growth engine to analyze conversion weaknesses
            analysis = await self.growth_engine.optimize_conversion({
                'url': url,
                'content': page_data.get('content', ''),
                'title': page_data.get('name', '')
            })
            
            # Extract weaknesses
            weaknesses = []
            for bottleneck in analysis.get('bottlenecks', []):
                weaknesses.append({
                    'element': bottleneck.get('element'),
                    'issue': bottleneck.get('issue'),
                    'opportunity': f"Improve your {bottleneck.get('element')} to outperform",
                    'confidence': bottleneck.get('confidence', 70)
                })
            
            return {
                'url': url,
                'weaknesses': weaknesses,
                'conversion_rate': analysis.get('current_conversion_rate', 0),
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze landing page: {e}", exc_info=True)
            return {'url': url, 'weaknesses': [], 'error': str(e)}
    
    async def estimate_metrics(self, competitor_id: str) -> Dict[str, Any]:
        """Estimate competitor metrics (traffic, ad spend, keywords)"""
        try:
            competitor = await self.db.competitors.find_one({'id': competitor_id})
            if not competitor:
                return {}
            
            # Use APIFY to get real market data
            domain = competitor['domain']
            
            # Estimate traffic (would use SimilarWeb/SEMrush API in production)
            estimated_traffic = await self._estimate_traffic(domain)
            
            # Estimate ad spend (would use ad intelligence tools in production)
            estimated_ad_spend = await self._estimate_ad_spend(domain)
            
            # Get keywords (would use SEMrush/Ahrefs API in production)
            keywords = await self._get_competitor_keywords(domain)
            
            metrics = {
                'estimated_traffic': estimated_traffic,
                'estimated_ad_spend': estimated_ad_spend,
                'top_keywords': keywords[:10],  # Top 10 keywords
                'active_campaigns': len(competitor.get('ad_campaigns_snapshot', [])),
                'domain_authority': await self._estimate_domain_authority(domain),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Update competitor metrics
            await self.db.competitors.update_one(
                {'id': competitor_id},
                {'$set': {'metrics': metrics}}
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to estimate metrics: {e}", exc_info=True)
            return {}
    
    async def suggest_counter_strategies(self, business_id: str, competitor_id: str) -> List[Dict[str, Any]]:
        """Generate counter-strategies to beat a competitor"""
        try:
            competitor = await self.db.competitors.find_one({'id': competitor_id})
            if not competitor:
                return []
            
            # Get business profile
            business = await self.db.businesses.find_one({'id': business_id})
            if not business:
                return []
            
            # Use growth engine to analyze competitor and generate strategies
            competitors_data = [{
                'name': competitor['name'],
                'domain': competitor['domain'],
                'metrics': competitor.get('metrics', {}),
                'weaknesses': competitor.get('weaknesses', [])
            }]
            
            analysis = await self.growth_engine.analyze_competitors(business_id, competitors_data)
            
            strategies = analysis.get('hijack_strategies', [])
            
            # Update competitor with strategies
            await self.db.competitors.update_one(
                {'id': competitor_id},
                {'$set': {'strategies': strategies}}
            )
            
            return strategies
            
        except Exception as e:
            logger.error(f"Failed to generate counter-strategies: {e}", exc_info=True)
            return []
    
    async def start_monitoring(self):
        """Start scheduled monitoring jobs"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        try:
            # Schedule website monitoring (every 24 hours)
            self.scheduler.add_job(
                self._monitor_all_websites,
                trigger=IntervalTrigger(hours=24),
                id='website_monitoring',
                replace_existing=True
            )
            
            # Schedule ad campaign monitoring (every 6 hours)
            self.scheduler.add_job(
                self._monitor_all_ad_campaigns,
                trigger=IntervalTrigger(hours=6),
                id='ad_monitoring',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.monitoring_active = True
            logger.info("Competitor monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}", exc_info=True)
            raise
    
    async def stop_monitoring(self):
        """Stop scheduled monitoring jobs"""
        if not self.monitoring_active:
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.monitoring_active = False
            logger.info("Competitor monitoring stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}", exc_info=True)
    
    # Private helper methods
    
    async def _monitor_all_websites(self):
        """Monitor all competitor websites for changes"""
        try:
            logger.info("Running scheduled website monitoring")
            
            # Get all competitors
            competitors = await self.db.competitors.find({}).to_list(length=1000)
            
            for competitor in competitors:
                try:
                    changes = await self.detect_changes(competitor['id'])
                    if changes:
                        logger.info(f"Detected {len(changes)} changes for {competitor['name']}")
                        # Could send notifications here
                except Exception as e:
                    logger.error(f"Failed to monitor competitor {competitor['id']}: {e}")
                
                # Small delay between requests
                await asyncio.sleep(2)
            
            logger.info(f"Website monitoring complete. Checked {len(competitors)} competitors")
            
        except Exception as e:
            logger.error(f"Website monitoring job failed: {e}", exc_info=True)
    
    async def _monitor_all_ad_campaigns(self):
        """Monitor all competitor ad campaigns"""
        try:
            logger.info("Running scheduled ad campaign monitoring")
            
            # Get all competitors
            competitors = await self.db.competitors.find({}).to_list(length=1000)
            
            for competitor in competitors:
                try:
                    # Check for new campaigns
                    new_campaigns = await self._detect_new_campaigns(competitor)
                    if new_campaigns:
                        logger.info(f"Detected {len(new_campaigns)} new campaigns for {competitor['name']}")
                        
                        # Update competitor record
                        changes = []
                        for campaign in new_campaigns:
                            change = {
                                'type': 'new_ad_campaign',
                                'detected_at': datetime.now(timezone.utc).isoformat(),
                                'description': f"New {campaign['platform']} campaign detected",
                                'impact': 'high',
                                'details': campaign
                            }
                            changes.append(change)
                        
                        await self.db.competitors.update_one(
                            {'id': competitor['id']},
                            {'$push': {'changes_detected': {'$each': changes}}}
                        )
                except Exception as e:
                    logger.error(f"Failed to monitor ads for competitor {competitor['id']}: {e}")
                
                # Small delay between requests
                await asyncio.sleep(2)
            
            logger.info(f"Ad campaign monitoring complete. Checked {len(competitors)} competitors")
            
        except Exception as e:
            logger.error(f"Ad campaign monitoring job failed: {e}", exc_info=True)
    
    async def _analyze_and_update_competitor(self, competitor_id: str):
        """Analyze competitor and update with weaknesses and strategies"""
        try:
            competitor = await self.db.competitors.find_one({'id': competitor_id})
            if not competitor:
                return
            
            # Analyze landing page for weaknesses
            analysis = await self.analyze_landing_page(competitor_id, competitor['url'])
            weaknesses = analysis.get('weaknesses', [])
            
            # Generate counter-strategies
            strategies = await self.suggest_counter_strategies(
                competitor['business_id'],
                competitor_id
            )
            
            # Update competitor
            await self.db.competitors.update_one(
                {'id': competitor_id},
                {
                    '$set': {
                        'weaknesses': weaknesses,
                        'strategies': strategies
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze competitor: {e}", exc_info=True)
    
    async def _scan_competitor_website(self, url: str) -> Dict[str, Any]:
        """Scan competitor website using APIFY"""
        try:
            # Use APIFY to scrape website
            result = await apify_market_service.analyze_competitor_websites([url])
            
            return {
                'name': self._extract_domain(url),
                'content': str(result),
                'estimated_traffic': '10K-50K/month',  # Would come from traffic estimation API
                'estimated_ad_spend': '$1K-5K/month',  # Would come from ad intelligence API
                'active_campaigns': 0,
                'top_keywords': [],
                'domain_authority': 40
            }
            
        except Exception as e:
            logger.error(f"Failed to scan website: {e}")
            return {
                'name': self._extract_domain(url),
                'content': '',
                'estimated_traffic': 'Unknown',
                'estimated_ad_spend': 'Unknown',
                'active_campaigns': 0,
                'top_keywords': [],
                'domain_authority': 0
            }
    
    async def _detect_new_campaigns(self, competitor: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect new ad campaigns (simulated - would use ad library APIs)"""
        try:
            # In production, this would use:
            # - Facebook Ad Library API
            # - Google Ads Transparency Center
            # - LinkedIn Ad Library
            
            # For now, return empty list (no new campaigns detected)
            # This would be populated with real ad data in production
            return []
            
        except Exception as e:
            logger.error(f"Failed to detect new campaigns: {e}")
            return []
    
    def _analyze_content_changes(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Analyze what changed in website content"""
        # Simple change detection
        old_len = len(old_content)
        new_len = len(new_content)
        
        change_percentage = abs(new_len - old_len) / max(old_len, 1) * 100
        
        return {
            'change_percentage': round(change_percentage, 2),
            'old_length': old_len,
            'new_length': new_len,
            'significant': change_percentage > 10
        }
    
    async def _estimate_traffic(self, domain: str) -> str:
        """Estimate website traffic"""
        # In production, would use SimilarWeb or SEMrush API
        # For now, return estimated range
        return "10K-50K/month"
    
    async def _estimate_ad_spend(self, domain: str) -> str:
        """Estimate ad spend"""
        # In production, would use ad intelligence tools
        # For now, return estimated range
        return "$1K-5K/month"
    
    async def _get_competitor_keywords(self, domain: str) -> List[str]:
        """Get competitor's top keywords"""
        # In production, would use SEMrush or Ahrefs API
        # For now, return generic keywords
        return [
            f"{domain.split('.')[0]} software",
            f"{domain.split('.')[0]} platform",
            f"{domain.split('.')[0]} tool",
            f"best {domain.split('.')[0]} alternative"
        ]
    
    async def _estimate_domain_authority(self, domain: str) -> int:
        """Estimate domain authority"""
        # In production, would use Moz API
        # For now, return estimated value
        return 45
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain if domain else url
        except:
            return url

# Global instance
competitor_hijacking_engine = None
