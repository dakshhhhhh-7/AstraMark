"""
MongoDB Collections and Indexes Initialization for Business Analysis Feature

This script creates the required MongoDB collections and indexes for the AI Business Analysis feature.
It ensures efficient queries and automatic cleanup of expired sessions.

Collections:
- analysis_sessions: Stores active and completed analysis sessions with conversation history
- business_analysis_reports: Stores generated reports with all analysis components
- market_research_cache: Caches market research data to reduce API calls

Requirements: REQ-9, REQ-12, REQ-13
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from config import settings


async def create_collections_and_indexes():
    """
    Create MongoDB collections and indexes for business analysis feature.
    
    This function:
    1. Creates three collections: analysis_sessions, business_analysis_reports, market_research_cache
    2. Adds unique indexes on session_id and report_id
    3. Adds compound indexes on user_id + created_at for efficient history queries
    4. Adds TTL indexes on expires_at for automatic cleanup (24 hours)
    """
    
    print("=" * 80)
    print("Business Analysis Database Initialization")
    print("=" * 80)
    print(f"\nConnecting to MongoDB: {settings.mongo_url}")
    print(f"Database: {settings.db_name}\n")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.mongo_url)
        db = client[settings.db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✓ Successfully connected to MongoDB\n")
        
        # =====================================================================
        # 1. Create analysis_sessions collection
        # =====================================================================
        print("Creating 'analysis_sessions' collection...")
        
        # Check if collection exists
        existing_collections = await db.list_collection_names()
        if "analysis_sessions" not in existing_collections:
            await db.create_collection("analysis_sessions")
            print("  ✓ Collection created")
        else:
            print("  ℹ Collection already exists")
        
        # Create indexes for analysis_sessions
        print("  Creating indexes...")
        
        # Unique index on session_id
        await db.analysis_sessions.create_index(
            "session_id",
            unique=True,
            name="session_id_unique"
        )
        print("    ✓ session_id (unique)")
        
        # Compound index on user_id + created_at for efficient history queries
        await db.analysis_sessions.create_index(
            [("user_id", 1), ("created_at", -1)],
            name="user_id_created_at_compound"
        )
        print("    ✓ user_id + created_at (compound)")
        
        # TTL index on expires_at for auto-cleanup (24 hours)
        await db.analysis_sessions.create_index(
            "expires_at",
            expireAfterSeconds=0,  # Expire at the time specified in expires_at field
            name="expires_at_ttl"
        )
        print("    ✓ expires_at (TTL index for auto-cleanup)")
        
        # Additional indexes for common queries
        await db.analysis_sessions.create_index(
            "status",
            name="status_index"
        )
        print("    ✓ status")
        
        await db.analysis_sessions.create_index(
            "last_activity_at",
            name="last_activity_at_index"
        )
        print("    ✓ last_activity_at")
        
        print("  ✓ All indexes created for analysis_sessions\n")
        
        # =====================================================================
        # 2. Create business_analysis_reports collection
        # =====================================================================
        print("Creating 'business_analysis_reports' collection...")
        
        if "business_analysis_reports" not in existing_collections:
            await db.create_collection("business_analysis_reports")
            print("  ✓ Collection created")
        else:
            print("  ℹ Collection already exists")
        
        # Create indexes for business_analysis_reports
        print("  Creating indexes...")
        
        # Unique index on report_id
        await db.business_analysis_reports.create_index(
            "report_id",
            unique=True,
            name="report_id_unique"
        )
        print("    ✓ report_id (unique)")
        
        # Compound index on user_id + created_at for efficient history queries
        await db.business_analysis_reports.create_index(
            [("user_id", 1), ("created_at", -1)],
            name="user_id_created_at_compound"
        )
        print("    ✓ user_id + created_at (compound)")
        
        # Index on session_id for lookups
        await db.business_analysis_reports.create_index(
            "session_id",
            name="session_id_index"
        )
        print("    ✓ session_id")
        
        print("  ✓ All indexes created for business_analysis_reports\n")
        
        # =====================================================================
        # 3. Create market_research_cache collection
        # =====================================================================
        print("Creating 'market_research_cache' collection...")
        
        if "market_research_cache" not in existing_collections:
            await db.create_collection("market_research_cache")
            print("  ✓ Collection created")
        else:
            print("  ℹ Collection already exists")
        
        # Create indexes for market_research_cache
        print("  Creating indexes...")
        
        # Unique index on cache_key
        await db.market_research_cache.create_index(
            "cache_key",
            unique=True,
            name="cache_key_unique"
        )
        print("    ✓ cache_key (unique)")
        
        # TTL index on expires_at for auto-cleanup (24 hours)
        await db.market_research_cache.create_index(
            "expires_at",
            expireAfterSeconds=0,  # Expire at the time specified in expires_at field
            name="expires_at_ttl"
        )
        print("    ✓ expires_at (TTL index for auto-cleanup)")
        
        # Indexes for common query patterns
        await db.market_research_cache.create_index(
            [("business_type", 1), ("target_market", 1)],
            name="business_type_target_market_compound"
        )
        print("    ✓ business_type + target_market (compound)")
        
        await db.market_research_cache.create_index(
            "last_accessed_at",
            name="last_accessed_at_index"
        )
        print("    ✓ last_accessed_at")
        
        print("  ✓ All indexes created for market_research_cache\n")
        
        # =====================================================================
        # Verify all indexes
        # =====================================================================
        print("=" * 80)
        print("Verifying Indexes")
        print("=" * 80)
        
        # Verify analysis_sessions indexes
        print("\nanalysis_sessions indexes:")
        indexes = await db.analysis_sessions.list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        # Verify business_analysis_reports indexes
        print("\nbusiness_analysis_reports indexes:")
        indexes = await db.business_analysis_reports.list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        # Verify market_research_cache indexes
        print("\nmarket_research_cache indexes:")
        indexes = await db.market_research_cache.list_indexes().to_list(length=None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        print("\n" + "=" * 80)
        print("✓ Database initialization completed successfully!")
        print("=" * 80)
        print("\nCollections created:")
        print("  1. analysis_sessions - Stores analysis sessions with auto-cleanup")
        print("  2. business_analysis_reports - Stores generated reports")
        print("  3. market_research_cache - Caches market research data")
        print("\nKey features:")
        print("  • Unique indexes on session_id and report_id")
        print("  • Compound indexes on user_id + created_at for efficient queries")
        print("  • TTL indexes for automatic cleanup after 24 hours")
        print("  • Additional indexes for common query patterns")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Close connection
        client.close()
        print("MongoDB connection closed.\n")


async def verify_collections():
    """
    Verify that all collections and indexes exist.
    """
    print("=" * 80)
    print("Verification Mode")
    print("=" * 80)
    
    try:
        client = AsyncIOMotorClient(settings.mongo_url)
        db = client[settings.db_name]
        
        await client.admin.command('ping')
        print("✓ Connected to MongoDB\n")
        
        # Check collections
        collections = await db.list_collection_names()
        required_collections = [
            "analysis_sessions",
            "business_analysis_reports",
            "market_research_cache"
        ]
        
        print("Checking collections:")
        all_exist = True
        for coll in required_collections:
            exists = coll in collections
            status = "✓" if exists else "✗"
            print(f"  {status} {coll}")
            if not exists:
                all_exist = False
        
        if all_exist:
            print("\n✓ All required collections exist")
        else:
            print("\n✗ Some collections are missing. Run without --verify to create them.")
            sys.exit(1)
        
        # Check indexes
        print("\nChecking indexes:")
        
        # analysis_sessions indexes
        indexes = await db.analysis_sessions.list_indexes().to_list(length=None)
        index_names = [idx['name'] for idx in indexes]
        required_indexes = ["session_id_unique", "user_id_created_at_compound", "expires_at_ttl"]
        
        print("  analysis_sessions:")
        for idx_name in required_indexes:
            exists = idx_name in index_names
            status = "✓" if exists else "✗"
            print(f"    {status} {idx_name}")
        
        # business_analysis_reports indexes
        indexes = await db.business_analysis_reports.list_indexes().to_list(length=None)
        index_names = [idx['name'] for idx in indexes]
        required_indexes = ["report_id_unique", "user_id_created_at_compound", "session_id_index"]
        
        print("  business_analysis_reports:")
        for idx_name in required_indexes:
            exists = idx_name in index_names
            status = "✓" if exists else "✗"
            print(f"    {status} {idx_name}")
        
        # market_research_cache indexes
        indexes = await db.market_research_cache.list_indexes().to_list(length=None)
        index_names = [idx['name'] for idx in indexes]
        required_indexes = ["cache_key_unique", "expires_at_ttl"]
        
        print("  market_research_cache:")
        for idx_name in required_indexes:
            exists = idx_name in index_names
            status = "✓" if exists else "✗"
            print(f"    {status} {idx_name}")
        
        print("\n✓ Verification complete\n")
        
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        sys.exit(1)
    finally:
        client.close()


async def drop_collections():
    """
    Drop all business analysis collections (use with caution!).
    """
    print("=" * 80)
    print("WARNING: Drop Collections Mode")
    print("=" * 80)
    print("\nThis will permanently delete all business analysis data!")
    
    try:
        client = AsyncIOMotorClient(settings.mongo_url)
        db = client[settings.db_name]
        
        await client.admin.command('ping')
        
        collections = [
            "analysis_sessions",
            "business_analysis_reports",
            "market_research_cache"
        ]
        
        for coll in collections:
            await db[coll].drop()
            print(f"  ✓ Dropped {coll}")
        
        print("\n✓ All collections dropped\n")
        
    except Exception as e:
        print(f"\n✗ Error dropping collections: {e}")
        sys.exit(1)
    finally:
        client.close()


def main():
    """
    Main entry point for the script.
    
    Usage:
        python init_business_analysis_db.py           # Create collections and indexes
        python init_business_analysis_db.py --verify  # Verify collections exist
        python init_business_analysis_db.py --drop    # Drop all collections (DANGEROUS!)
    """
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify":
            asyncio.run(verify_collections())
        elif sys.argv[1] == "--drop":
            print("\nAre you sure you want to drop all business analysis collections?")
            print("Type 'yes' to confirm: ", end="")
            confirmation = input().strip().lower()
            if confirmation == "yes":
                asyncio.run(drop_collections())
            else:
                print("Aborted.")
        else:
            print("Usage:")
            print("  python init_business_analysis_db.py           # Create collections and indexes")
            print("  python init_business_analysis_db.py --verify  # Verify collections exist")
            print("  python init_business_analysis_db.py --drop    # Drop all collections")
    else:
        asyncio.run(create_collections_and_indexes())


if __name__ == "__main__":
    main()
