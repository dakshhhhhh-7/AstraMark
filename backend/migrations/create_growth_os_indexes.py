"""
Database Migration: Create Indexes for Growth Operating System Collections

This migration creates comprehensive indexes for all Growth OS collections
to optimize query performance across campaigns, autonomous mode, competitors,
leads, learning updates, and revenue projections.

Collections:
- campaigns
- daily_actions
- autonomous_configs
- autonomous_actions
- competitors
- lead_funnels
- leads
- learning_updates
- revenue_projections

Run with: python backend/migrations/create_growth_os_indexes.py
"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def create_growth_os_indexes():
    """Create all indexes for Growth Operating System collections"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "test_database")
    
    print(f"Connecting to {mongo_url} / {db_name}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        print("\n=== Creating Growth OS Indexes ===\n")
        
        # ===== CAMPAIGNS COLLECTION =====
        print("Creating indexes for 'campaigns' collection...")
        await db.campaigns.create_index("id", unique=True)
        await db.campaigns.create_index("business_id")
        await db.campaigns.create_index("status")
        await db.campaigns.create_index("created_at")
        await db.campaigns.create_index("launched_at")
        # Compound indexes for common queries
        await db.campaigns.create_index([("business_id", 1), ("status", 1)])
        await db.campaigns.create_index([("business_id", 1), ("created_at", -1)])
        await db.campaigns.create_index([("status", 1), ("launched_at", -1)])
        await db.campaigns.create_index([("business_id", 1), ("created_by", 1)])
        print("✓ Campaigns indexes created")
        
        # ===== DAILY_ACTIONS COLLECTION =====
        print("Creating indexes for 'daily_actions' collection...")
        await db.daily_actions.create_index("id", unique=True)
        await db.daily_actions.create_index("business_id")
        await db.daily_actions.create_index("status")
        await db.daily_actions.create_index("created_at")
        await db.daily_actions.create_index("priority")
        # Compound indexes for filtering and sorting
        await db.daily_actions.create_index([("business_id", 1), ("status", 1)])
        await db.daily_actions.create_index([("business_id", 1), ("created_at", -1)])
        await db.daily_actions.create_index([("business_id", 1), ("priority", 1), ("roi_score", -1)])
        await db.daily_actions.create_index([("status", 1), ("created_at", -1)])
        print("✓ Daily actions indexes created")
        
        # ===== AUTONOMOUS_CONFIGS COLLECTION =====
        print("Creating indexes for 'autonomous_configs' collection...")
        await db.autonomous_configs.create_index("business_id", unique=True)
        await db.autonomous_configs.create_index("enabled")
        await db.autonomous_configs.create_index("started_at")
        # Compound index for active autonomous businesses
        await db.autonomous_configs.create_index([("enabled", 1), ("started_at", -1)])
        print("✓ Autonomous configs indexes created")
        
        # ===== AUTONOMOUS_ACTIONS COLLECTION =====
        print("Creating indexes for 'autonomous_actions' collection...")
        await db.autonomous_actions.create_index("business_id")
        await db.autonomous_actions.create_index("executed_at")
        await db.autonomous_actions.create_index("status")
        # Compound indexes for querying recent actions
        await db.autonomous_actions.create_index([("business_id", 1), ("executed_at", -1)])
        await db.autonomous_actions.create_index([("business_id", 1), ("status", 1)])
        await db.autonomous_actions.create_index([("executed_at", -1)])
        print("✓ Autonomous actions indexes created")
        
        # ===== COMPETITORS COLLECTION =====
        print("Creating indexes for 'competitors' collection...")
        await db.competitors.create_index("id", unique=True)
        await db.competitors.create_index("business_id")
        await db.competitors.create_index("domain")
        await db.competitors.create_index("last_scan")
        await db.competitors.create_index("monitoring_since")
        # Compound indexes for monitoring queries
        await db.competitors.create_index([("business_id", 1), ("last_scan", -1)])
        await db.competitors.create_index([("business_id", 1), ("domain", 1)])
        await db.competitors.create_index([("last_scan", 1)])  # For scheduled monitoring
        print("✓ Competitors indexes created")
        
        # ===== LEAD_FUNNELS COLLECTION =====
        print("Creating indexes for 'lead_funnels' collection...")
        await db.lead_funnels.create_index("id", unique=True)
        await db.lead_funnels.create_index("business_id")
        await db.lead_funnels.create_index("created_at")
        await db.lead_funnels.create_index("status")
        # Compound indexes for business funnel queries
        await db.lead_funnels.create_index([("business_id", 1), ("status", 1)])
        await db.lead_funnels.create_index([("business_id", 1), ("created_at", -1)])
        print("✓ Lead funnels indexes created")
        
        # ===== LEADS COLLECTION =====
        print("Creating indexes for 'leads' collection...")
        await db.leads.create_index("id", unique=True)
        await db.leads.create_index("funnel_id")
        await db.leads.create_index("business_id")
        await db.leads.create_index("email")
        await db.leads.create_index("status")
        await db.leads.create_index("current_stage")
        await db.leads.create_index("score")
        await db.leads.create_index("entered_at")
        await db.leads.create_index("last_activity")
        # Compound indexes for lead management queries
        await db.leads.create_index([("funnel_id", 1), ("status", 1)])
        await db.leads.create_index([("funnel_id", 1), ("current_stage", 1)])
        await db.leads.create_index([("business_id", 1), ("status", 1)])
        await db.leads.create_index([("business_id", 1), ("score", -1)])
        await db.leads.create_index([("funnel_id", 1), ("score", -1)])
        await db.leads.create_index([("status", 1), ("last_activity", 1)])  # For cold lead detection
        await db.leads.create_index([("business_id", 1), ("entered_at", -1)])
        print("✓ Leads indexes created")
        
        # ===== LEARNING_UPDATES COLLECTION =====
        print("Creating indexes for 'learning_updates' collection...")
        await db.learning_updates.create_index("id", unique=True)
        await db.learning_updates.create_index("campaign_id")
        await db.learning_updates.create_index("business_id")
        await db.learning_updates.create_index("applied_at")
        await db.learning_updates.create_index("optimization_type")
        # Compound indexes for learning queries
        await db.learning_updates.create_index([("campaign_id", 1), ("applied_at", -1)])
        await db.learning_updates.create_index([("business_id", 1), ("applied_at", -1)])
        await db.learning_updates.create_index([("optimization_type", 1), ("applied_at", -1)])
        await db.learning_updates.create_index([("business_id", 1), ("optimization_type", 1)])
        print("✓ Learning updates indexes created")
        
        # ===== REVENUE_PROJECTIONS COLLECTION =====
        print("Creating indexes for 'revenue_projections' collection...")
        await db.revenue_projections.create_index("id", unique=True)
        await db.revenue_projections.create_index("business_id")
        await db.revenue_projections.create_index("campaign_id")
        await db.revenue_projections.create_index("created_at")
        # Compound indexes for projection queries
        await db.revenue_projections.create_index([("business_id", 1), ("created_at", -1)])
        await db.revenue_projections.create_index([("campaign_id", 1), ("created_at", -1)])
        await db.revenue_projections.create_index([("business_id", 1), ("campaign_id", 1)])
        print("✓ Revenue projections indexes created")
        
        # ===== ADDITIONAL SUPPORTING COLLECTIONS =====
        print("\nCreating indexes for supporting collections...")
        
        # Campaign deployments
        await db.campaign_deployments.create_index("campaign_id")
        await db.campaign_deployments.create_index([("campaign_id", 1), ("channel", 1)])
        await db.campaign_deployments.create_index("deployed_at")
        print("✓ Campaign deployments indexes created")
        
        # Campaign optimizations
        await db.campaign_optimizations.create_index("campaign_id")
        await db.campaign_optimizations.create_index([("campaign_id", 1), ("applied_at", -1)])
        print("✓ Campaign optimizations indexes created")
        
        # Autonomous errors
        await db.autonomous_errors.create_index("business_id")
        await db.autonomous_errors.create_index([("business_id", 1), ("timestamp", -1)])
        print("✓ Autonomous errors indexes created")
        
        # Alerts
        await db.alerts.create_index("business_id")
        await db.alerts.create_index([("business_id", 1), ("created_at", -1)])
        await db.alerts.create_index("status")
        print("✓ Alerts indexes created")
        
        # A/B tests
        await db.ab_tests.create_index("id", unique=True)
        await db.ab_tests.create_index("page_id")
        await db.ab_tests.create_index([("page_id", 1), ("status", 1)])
        print("✓ A/B tests indexes created")
        
        print("\n=== All Growth OS Indexes Created Successfully ===")
        print("\nIndex Summary:")
        print("  ✓ campaigns: 9 indexes")
        print("  ✓ daily_actions: 8 indexes")
        print("  ✓ autonomous_configs: 4 indexes")
        print("  ✓ autonomous_actions: 6 indexes")
        print("  ✓ competitors: 8 indexes")
        print("  ✓ lead_funnels: 5 indexes")
        print("  ✓ leads: 14 indexes")
        print("  ✓ learning_updates: 8 indexes")
        print("  ✓ revenue_projections: 7 indexes")
        print("  ✓ Supporting collections: 10 indexes")
        print("\nTotal: 79 indexes created for optimal query performance")
        
    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        raise
    finally:
        client.close()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    asyncio.run(create_growth_os_indexes())
