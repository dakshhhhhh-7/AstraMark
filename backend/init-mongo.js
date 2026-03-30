// MongoDB initialization script
db = db.getSiblingDB('astramark_dev');

// Create collections with indexes
db.createCollection('users');
db.createCollection('businesses');
db.createCollection('analyses');
db.createCollection('payments');
db.createCollection('market_signals');
db.createCollection('blockchain_proofs');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "id": 1 }, { unique: true });
db.users.createIndex({ "stripe_customer_id": 1 });

db.businesses.createIndex({ "id": 1 }, { unique: true });
db.businesses.createIndex({ "created_at": -1 });

db.analyses.createIndex({ "id": 1 }, { unique: true });
db.analyses.createIndex({ "business_id": 1 });
db.analyses.createIndex({ "created_at": -1 });

db.payments.createIndex({ "user_id": 1 });
db.payments.createIndex({ "created_at": -1 });

db.market_signals.createIndex({ "business_type": 1 });
db.market_signals.createIndex({ "created_at": -1 });

db.blockchain_proofs.createIndex({ "analysis_id": 1 });
db.blockchain_proofs.createIndex({ "proof_hash": 1 }, { unique: true });

print('Database initialized successfully');