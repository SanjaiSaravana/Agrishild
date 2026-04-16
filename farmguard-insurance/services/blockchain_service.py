import requests
from config import Config

class BlockchainService:
    @staticmethod
    def get_sol_balance(wallet_address):
        # Helius RPC Endpoint
        url = f"https://devnet.helius-rpc.com/?api-key={Config.HELIUS_KEY}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [wallet_address]
        }
        
        try:
            response = requests.post(url, json=payload).json()
            # Balance comes in Lamports (1 SOL = 1,000,000,000 Lamports)
            lamports = response['result']['value']
            sol_balance = lamports / 10**9
            return sol_balance
        except Exception as e:
            print(f"Helius Fetch Error: {e}")
            return 0