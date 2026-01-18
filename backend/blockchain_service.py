"""
Blockchain Service for timestamping AI insights on Polygon
Falls back to MongoDB when blockchain is not available
"""
import os
import logging
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.enabled = os.environ.get('ENABLE_BLOCKCHAIN', 'false').lower() == 'true'
        self.rpc_url = os.environ.get('POLYGON_RPC_URL', '')
        self.private_key = os.environ.get('WALLET_PRIVATE_KEY', '')
        self.wallet_address = os.environ.get('WALLET_ADDRESS', '')
        self.contract_address = os.environ.get('CONTRACT_ADDRESS', '')
        
        self.w3 = None
        self.account = None
        
        if self.enabled and self.rpc_url and self.private_key:
            try:
                self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
                self.account = Account.from_key(self.private_key)
                logger.info(f"Blockchain service initialized: {self.wallet_address}")
            except Exception as e:
                logger.error(f"Failed to initialize blockchain: {e}")
                self.enabled = False
    
    async def timestamp_analysis(self, analysis_data: Dict[str, Any], db_collection=None) -> Dict[str, Any]:
        """
        Timestamp an analysis on blockchain or fallback to database
        """
        # Generate hash of the analysis
        data_hash = self._generate_hash(analysis_data)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        if self.enabled and self.w3 and self.w3.is_connected():
            try:
                # In production, this would call a smart contract
                # For now, we'll create a transaction with the hash in the data field
                tx_hash = await self._create_timestamp_transaction(data_hash)
                
                return {
                    'hash': data_hash,
                    'timestamp': timestamp,
                    'network': 'Polygon Amoy Testnet',
                    'tx_hash': tx_hash,
                    'explorer_url': f'https://amoy.polygonscan.com/tx/{tx_hash}',
                    'wallet': self.wallet_address,
                    'verified': True
                }
            except Exception as e:
                logger.error(f"Blockchain timestamp failed: {e}")
                # Fallback to database
                return await self._fallback_to_database(data_hash, timestamp, analysis_data, db_collection)
        else:
            # Use database fallback
            return await self._fallback_to_database(data_hash, timestamp, analysis_data, db_collection)
    
    async def _create_timestamp_transaction(self, data_hash: str) -> str:
        """Create a transaction on Polygon to timestamp the data"""
        try:
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.wallet_address)
            
            # Build transaction
            transaction = {
                'nonce': nonce,
                'to': self.wallet_address,  # Send to self
                'value': 0,
                'gas': 21000,
                'gasPrice': self.w3.eth.gas_price,
                'data': self.w3.to_hex(text=data_hash),
                'chainId': 80002  # Polygon Amoy testnet
            }
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return self.w3.to_hex(tx_hash)
        except Exception as e:
            logger.error(f"Transaction creation failed: {e}")
            raise
    
    async def _fallback_to_database(
        self, 
        data_hash: str, 
        timestamp: str, 
        analysis_data: Dict[str, Any],
        db_collection
    ) -> Dict[str, Any]:
        """Store proof in database when blockchain is unavailable"""
        proof = {
            'hash': data_hash,
            'timestamp': timestamp,
            'network': 'AstraMark Intelligence Ledger (Database)',
            'analysis_id': analysis_data.get('id', 'unknown'),
            'verified': False,
            'storage': 'mongodb'
        }
        
        # Store in database if collection is provided
        if db_collection is not None:
            try:
                await db_collection.insert_one({
                    'proof_hash': data_hash,
                    'timestamp': timestamp,
                    'analysis_id': analysis_data.get('id'),
                    'created_at': datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                logger.error(f"Database proof storage failed: {e}")
        
        return proof
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash of analysis data"""
        # Create a deterministic string representation
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def verify_proof(self, proof_hash: str, tx_hash: Optional[str] = None) -> bool:
        """Verify a blockchain proof"""
        if not self.enabled or not tx_hash:
            return False
        
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            tx_data = self.w3.to_text(tx['data'])
            return tx_data == proof_hash
        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return False

# Singleton instance
blockchain_service = BlockchainService()
