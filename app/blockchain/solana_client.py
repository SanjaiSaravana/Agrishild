"""
Solana Blockchain Client
Handles connection to Solana network and transaction execution
"""

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solders.message import Message
import base58
import os
from typing import Optional


class SolanaClient:
    def __init__(self, rpc_url: str = "https://api.devnet.solana.com"):
        """
        Initialize Solana client
        
        Args:
            rpc_url: Solana RPC endpoint (devnet, testnet, or mainnet)
        """
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url, commitment=Confirmed)
        
    async def get_balance(self, pubkey: str) -> float:
        """
        Get SOL balance for a wallet address
        
        Args:
            pubkey: Wallet public key as base58 string
            
        Returns:
            Balance in SOL
        """
        try:
            pubkey_obj = Pubkey.from_string(pubkey)
            response = await self.client.get_balance(pubkey_obj)
            # Convert lamports to SOL (1 SOL = 1,000,000,000 lamports)
            balance_sol = response.value / 1_000_000_000
            return balance_sol
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0.0
    
    async def send_sol(
        self, 
        from_keypair: Keypair, 
        to_pubkey: str, 
        amount_sol: float
    ) -> Optional[str]:
        """
        Send SOL from one wallet to another
        
        Args:
            from_keypair: Sender's keypair
            to_pubkey: Recipient's public key as base58 string
            amount_sol: Amount to send in SOL
            
        Returns:
            Transaction signature if successful, None otherwise
        """
        try:
            # Convert SOL to lamports
            amount_lamports = int(amount_sol * 1_000_000_000)
            
            # Create recipient pubkey
            to_pubkey_obj = Pubkey.from_string(to_pubkey)
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=from_keypair.pubkey(),
                    to_pubkey=to_pubkey_obj,
                    lamports=amount_lamports
                )
            )
            
            # Get recent blockhash
            blockhash_resp = await self.client.get_latest_blockhash()
            recent_blockhash = blockhash_resp.value.blockhash
            
            # Create and sign transaction
            message = Message.new_with_blockhash(
                [transfer_ix],
                from_keypair.pubkey(),
                recent_blockhash
            )
            transaction = Transaction([from_keypair], message, recent_blockhash)
            
            # Send transaction
            response = await self.client.send_transaction(transaction)
            
            # Return transaction signature
            return str(response.value)
            
        except Exception as e:
            print(f"Error sending SOL: {e}")
            return None
    
    async def airdrop_sol(self, pubkey: str, amount_sol: float = 1.0) -> bool:
        """
        Request airdrop of SOL (devnet/testnet only)
        
        Args:
            pubkey: Wallet public key as base58 string
            amount_sol: Amount to airdrop in SOL
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pubkey_obj = Pubkey.from_string(pubkey)
            amount_lamports = int(amount_sol * 1_000_000_000)
            
            response = await self.client.request_airdrop(pubkey_obj, amount_lamports)
            
            # Wait for confirmation
            await self.client.confirm_transaction(response.value)
            
            return True
        except Exception as e:
            print(f"Error requesting airdrop: {e}")
            return False
    
    async def get_transaction_status(self, signature: str) -> dict:
        """
        Get transaction status and details
        
        Args:
            signature: Transaction signature
            
        Returns:
            Transaction details
        """
        try:
            response = await self.client.get_transaction(signature)
            return {
                "confirmed": response.value is not None,
                "slot": response.value.slot if response.value else None,
                "block_time": response.value.block_time if response.value else None
            }
        except Exception as e:
            print(f"Error getting transaction: {e}")
            return {"confirmed": False}
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()


def create_keypair() -> Keypair:
    """
    Generate a new Solana keypair
    
    Returns:
        New Keypair object
    """
    return Keypair()


def keypair_from_secret(secret_key: str) -> Keypair:
    """
    Load keypair from base58 encoded secret key
    
    Args:
        secret_key: Base58 encoded secret key
        
    Returns:
        Keypair object
    """
    secret_bytes = base58.b58decode(secret_key)
    return Keypair.from_bytes(secret_bytes)


def keypair_to_secret(keypair: Keypair) -> str:
    """
    Convert keypair to base58 encoded secret key
    
    Args:
        keypair: Keypair object
        
    Returns:
        Base58 encoded secret key
    """
    return base58.b58encode(bytes(keypair)).decode('utf-8')
