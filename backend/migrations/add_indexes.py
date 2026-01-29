from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def add_indexes():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "test_database")
    
    print(f"Connecting to {mongo_url} / {db_name}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Users collection
        await db.users.create_index("email", unique=True)
        await db.users.create_index("created_at")
        
        # Analyses collection
        await db.analyses.create_index("business_id")
        await db.analyses.create_index("created_at")
        await db.analyses.create_index([("business_id", 1), ("created_at", -1)])
        
        # Market signals
        await db.market_signals.create_index("detected_at")
        await db.market_signals.create_index([("business_type", 1), ("detected_at", -1)])
        
        print("Indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_indexes())
