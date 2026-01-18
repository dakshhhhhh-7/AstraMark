"""
Background Market Scanner
Periodically scans markets for signals and competitor updates
"""
import os
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

class BackgroundScanner:
    def __init__(self, serp_service, db):
        self.serp_service = serp_service
        self.db = db
        self.scheduler = AsyncIOScheduler()
        self.enabled = os.environ.get('ENABLE_BACKGROUND_SCANNER', 'true').lower() == 'true'
        self.scan_interval_minutes = 30  # Scan every 30 minutes
        
    def start(self):
        """Start the background scanner"""
        if not self.enabled:
            logger.info("Background scanner is disabled")
            return
        
        # Schedule market scanning
        self.scheduler.add_job(
            self.scan_markets,
            trigger=IntervalTrigger(minutes=self.scan_interval_minutes),
            id='market_scanner',
            name='Market Signal Scanner',
            replace_existing=True
        )
        
        # Schedule competitor monitoring
        self.scheduler.add_job(
            self.monitor_competitors,
            trigger=IntervalTrigger(minutes=60),  # Every hour
            id='competitor_monitor',
            name='Competitor Monitor',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(f"Background scanner started (interval: {self.scan_interval_minutes} minutes)")
    
    def stop(self):
        """Stop the background scanner"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Background scanner stopped")
    
    async def scan_markets(self):
        """Scan markets for new signals and trends"""
        try:
            logger.info("Starting market scan...")
            
            # Get recent analyses to know what markets to monitor
            recent_analyses = await self.db.analyses.find({}).sort("created_at", -1).limit(10).to_list(length=10)
            
            if not recent_analyses:
                logger.info("No analyses to monitor")
                return
            
            # Extract unique business types and markets
            markets_to_scan = set()
            for analysis in recent_analyses:
                # Try to get business info from linked business profile
                business_id = analysis.get('business_id')
                if business_id:
                    business = await self.db.businesses.find_one({'id': business_id})
                    if business:
                        business_type = business.get('business_type', '')
                        target_market = business.get('target_market', '')
                        if business_type and target_market:
                            markets_to_scan.add((business_type, target_market))
            
            # Scan each market
            signals_generated = 0
            for business_type, target_market in markets_to_scan:
                signals = await self._generate_market_signals(business_type, target_market)
                
                # Store signals in database
                for signal in signals:
                    await self.db.market_signals.insert_one({
                        'business_type': business_type,
                        'target_market': target_market,
                        'signal_type': signal['type'],
                        'severity': signal['severity'],
                        'message': signal['message'],
                        'detected_at': datetime.now(timezone.utc).isoformat(),
                        'created_at': datetime.now(timezone.utc).isoformat()
                    })
                    signals_generated += 1
            
            logger.info(f"Market scan completed. Generated {signals_generated} signals")
            
        except Exception as e:
            logger.error(f"Market scan failed: {e}")
    
    async def monitor_competitors(self):
        """Monitor competitor activities"""
        try:
            logger.info("Starting competitor monitoring...")
            
            # Get recent analyses
            recent_analyses = await self.db.analyses.find({}).sort("created_at", -1).limit(5).to_list(length=5)
            
            updates_found = 0
            for analysis in recent_analyses:
                business_id = analysis.get('business_id')
                if business_id:
                    business = await self.db.businesses.find_one({'id': business_id})
                    if business:
                        business_type = business.get('business_type', '')
                        target_market = business.get('target_market', '')
                        
                        # Fetch competitor data
                        competitor_data = await self.serp_service.search_competitors(
                            business_type, 
                            target_market
                        )
                        
                        # Store competitor snapshot
                        await self.db.competitor_snapshots.insert_one({
                            'business_id': business_id,
                            'business_type': business_type,
                            'target_market': target_market,
                            'competitors': competitor_data.get('competitors', []),
                            'total_results': competitor_data.get('total_results', 0),
                            'snapshot_at': datetime.now(timezone.utc).isoformat(),
                            'created_at': datetime.now(timezone.utc).isoformat()
                        })
                        updates_found += 1
            
            logger.info(f"Competitor monitoring completed. {updates_found} snapshots created")
            
        except Exception as e:
            logger.error(f"Competitor monitoring failed: {e}")
    
    async def _generate_market_signals(self, business_type: str, target_market: str) -> List[Dict[str, Any]]:
        """Generate market signals for a specific business/market combination"""
        signals = []
        
        # Get market trends
        trends = await self.serp_service.get_market_trends(business_type)
        
        # Analyze CPC trends
        cpc_trend = trends.get('google_ads_cpc_trend', '')
        if '+' in cpc_trend:
            signals.append({
                'type': 'Market',
                'severity': 'warning',
                'message': f'Google Ads CPC increased {cpc_trend} for {business_type} - consider adjusting budget'
            })
        
        # Analyze CPM trends
        cpm_trend = trends.get('meta_ads_cpm_trend', '')
        if '-' in cpm_trend:
            signals.append({
                'type': 'Market',
                'severity': 'info',
                'message': f'Meta Ads CPM decreased {cpm_trend} - good opportunity for paid social campaigns'
            })
        
        # Get competitor data
        competitor_data = await self.serp_service.search_competitors(business_type, target_market)
        competitors = competitor_data.get('competitors', [])
        
        # Check for new competitors or changes
        if len(competitors) > 0:
            top_competitor = competitors[0]
            signals.append({
                'type': 'Competitive',
                'severity': 'info',
                'message': f'Top competitor "{top_competitor.get("name", "Unknown")}" detected in {target_market}'
            })
        
        # Add rising keyword signals
        rising_keywords = trends.get('top_rising_keywords', [])
        if rising_keywords:
            signals.append({
                'type': 'Consumer',
                'severity': 'info',
                'message': f'Rising search interest: {", ".join(rising_keywords[:3])}'
            })
        
        return signals
    
    async def get_latest_signals(self, business_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get latest market signals"""
        try:
            query = {}
            if business_type:
                query['business_type'] = business_type
            
            signals = await self.db.market_signals.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
            return signals
        except Exception as e:
            logger.error(f"Failed to fetch signals: {e}")
            return []
    
    async def get_competitor_updates(self, business_id: str) -> List[Dict[str, Any]]:
        """Get competitor updates for a specific business"""
        try:
            snapshots = await self.db.competitor_snapshots.find(
                {'business_id': business_id}
            ).sort("created_at", -1).limit(5).to_list(length=5)
            
            return snapshots
        except Exception as e:
            logger.error(f"Failed to fetch competitor updates: {e}")
            return []

# This will be initialized in server.py
background_scanner = None
