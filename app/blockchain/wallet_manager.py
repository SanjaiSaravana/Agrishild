"""
Insurance Wallet Manager
Manages the insurance pool wallet and policy escrow accounts
"""

from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58
import json
import os
from typing import Optional, Dict
from .solana_client import SolanaClient, create_keypair, keypair_from_secret, keypair_to_secret


class InsuranceWalletManager:
    def __init__(self, pool_keypair: Optional[Keypair] = None):
        """
        Initialize insurance wallet manager
        
        Args:
            pool_keypair: Main insurance pool keypair (if None, creates new one)
        """
        if pool_keypair is None:
            # Create new pool wallet
            self.pool_keypair = create_keypair()
            print(f"Created new insurance pool wallet: {self.pool_keypair.pubkey()}")
        else:
            self.pool_keypair = pool_keypair
            
        self.client = SolanaClient()
        
    def get_pool_address(self) -> str:
        """Get the insurance pool wallet address"""
        return str(self.pool_keypair.pubkey())
    
    def get_pool_secret(self) -> str:
        """Get the insurance pool secret key (base58 encoded)"""
        return keypair_to_secret(self.pool_keypair)
    
    async def get_pool_balance(self) -> float:
        """Get current balance of insurance pool"""
        return await self.client.get_balance(str(self.pool_keypair.pubkey()))
    
    async def fund_pool(self, amount_sol: float = 10.0) -> bool:
        """
        Request airdrop to fund the insurance pool (devnet only)
        
        Args:
            amount_sol: Amount to airdrop
            
        Returns:
            True if successful
        """
        return await self.client.airdrop_sol(
            str(self.pool_keypair.pubkey()), 
            amount_sol
        )
    
    async def collect_premium(
        self, 
        farmer_pubkey: str, 
        premium_amount: float
    ) -> Optional[str]:
        """
        Collect premium from farmer (in real implementation, farmer would send to pool)
        For MVP, we simulate this by checking farmer has enough balance
        
        Args:
            farmer_pubkey: Farmer's wallet address
            premium_amount: Premium amount in SOL
            
        Returns:
            Transaction signature if successful
        """
        # In production, farmer would initiate transfer to pool
        # For MVP, we just verify they have the balance
        farmer_balance = await self.client.get_balance(farmer_pubkey)
        
        if farmer_balance >= premium_amount:
            return f"premium_collected_{farmer_pubkey[:8]}"
        return None
    
    async def execute_payout(
        self, 
        farmer_pubkey: str, 
        payout_amount: float,
        policy_id: str
    ) -> Optional[Dict]:
        """
        Execute insurance payout to farmer
        
        Args:
            farmer_pubkey: Farmer's wallet address
            payout_amount: Payout amount in SOL
            policy_id: Policy ID for tracking
            
        Returns:
            Transaction details if successful
        """
        try:
            # Check pool has sufficient balance
            pool_balance = await self.get_pool_balance()
            
            if pool_balance < payout_amount:
                print(f"Insufficient pool balance: {pool_balance} SOL < {payout_amount} SOL")
                return None
            
            # Execute transfer from pool to farmer
            tx_signature = await self.client.send_sol(
                self.pool_keypair,
                farmer_pubkey,
                payout_amount
            )
            
            if tx_signature:
                # Get transaction status
                tx_status = await self.client.get_transaction_status(tx_signature)
                
                return {
                    "success": True,
                    "tx_signature": tx_signature,
                    "policy_id": policy_id,
                    "amount": payout_amount,
                    "recipient": farmer_pubkey,
                    "confirmed": tx_status.get("confirmed", False),
                    "explorer_url": f"https://explorer.solana.com/tx/{tx_signature}?cluster=devnet"
                }
            
            return None
            
        except Exception as e:
            print(f"Payout execution error: {e}")
            return None
    
    async def create_policy_escrow(
        self, 
        policy_id: str, 
        coverage_amount: float
    ) -> Dict:
        """
        Create escrow account for a policy (simplified for MVP)
        In production, this would use Program Derived Addresses (PDAs)
        
        Args:
            policy_id: Unique policy identifier
            coverage_amount: Coverage amount in SOL
            
        Returns:
            Escrow details
        """
        # For MVP, we just track this in memory/database
        # In production, create actual on-chain escrow account
        return {
            "policy_id": policy_id,
            "escrow_address": f"escrow_{policy_id}",
            "coverage_amount": coverage_amount,
            "pool_address": str(self.pool_keypair.pubkey())
        }
    
    async def close(self):
        """Close client connections"""
        await self.client.close()
    
    def save_to_file(self, filepath: str = ".insurance_pool_keypair"):
        """
        Save pool keypair to file
        
        Args:
            filepath: Path to save keypair
        """
        data = {
            "pubkey": str(self.pool_keypair.pubkey()),
            "secret": self.get_pool_secret()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        print(f"Pool keypair saved to {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str = ".insurance_pool_keypair"):
        """
        Load pool keypair from file
        
        Args:
            filepath: Path to keypair file
            
        Returns:
            InsuranceWalletManager instance
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Keypair file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        keypair = keypair_from_secret(data["secret"])
        return cls(pool_keypair=keypair)


# Global instance (will be initialized on first use)
_wallet_manager: Optional[InsuranceWalletManager] = None


async def get_wallet_manager() -> InsuranceWalletManager:
    """
    Get or create the global wallet manager instance
    
    Returns:
        InsuranceWalletManager instance
    """
    global _wallet_manager
    
    if _wallet_manager is None:
        # Try to load from file, otherwise create new
        try:
            _wallet_manager = InsuranceWalletManager.load_from_file()
            print("Loaded existing insurance pool wallet")
        except FileNotFoundError:
            _wallet_manager = InsuranceWalletManager()
            _wallet_manager.save_to_file()
            print("Created new insurance pool wallet")
            
            # Fund the pool with devnet SOL
            funded = await _wallet_manager.fund_pool(100.0)  # 100 SOL for testing
            if funded:
                print("Pool funded with 100 SOL from devnet faucet")
    
    return _wallet_manager
