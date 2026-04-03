"""
Verify Growth OS Indexes

This script verifies that all indexes were created successfully
and displays index information for each collection.

Run with: python backend/migrations/verify_indexes.py
"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def verify_indexes():
    """Verify all Growth OS indexes were created"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "test_database")
    
    print(f"Connecting to {mongo_url} / {db_name}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    collections = [
        "campaigns",
        "daily_actions",
        "autonomous_configs",
        "autonomous_actions",
        "competitors",
        "lead_funnels",
        "leads",
        "learning_updates",
        "revenue_projections",
        "campaign_deployments",
        "campaign_optimizations",
        "autonomous_errors",
        "alerts",
        "ab_tests"
    ]
    
    try:
        print("\n=== Verifying Growth OS Indexes ===\n")
        
        total_indexes = 0
        
        for collection_name in collections:
            collection = db[collection_name]
            indexes = await collection.index_information()
            
            # Exclude the default _id index from count
            index_count = len(indexes) - 1 if '_id_' in indexes else len(indexes)
            total_indexes += index_count
            
            print(f"Collection: {collection_name}")
            print(f"  Indexes: {index_count}")
            
            # Display index details
            for index_name, index_info in indexes.items():
                if index_name != '_id_':  # Skip default _id index
                    keys = index_info.get('key', [])
                    unique = index_info.get('unique', False)
                    unique_str = " [UNIQUE]" if unique else ""
                    print(f"    - {index_name}: {keys}{unique_str}")
            
            print()
        
        print(f"=== Verification Complete ===")
        print(f"Total custom indexes: {total_indexes}")
        print(f"Collections verified: {len(collections)}")
        
    except Exception as e:
        print(f"\n❌ Error verifying indexes: {e}")
        raise
    finally:
        client.close()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    asyncio.run(verify_indexes())
