from flask import Blueprint, request, jsonify
import requests
from config import Config

blockchain_bp = Blueprint('blockchain_api', __name__)

@blockchain_bp.route('/balance')
def get_balance():
    # Get address from query param; default to a known devnet address for testing
    address = request.args.get('address', '6x66...') 
    
    url = f"https://devnet.helius-rpc.com/?api-key={Config.HELIUS_KEY}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address]
    }
    
    try:
        response = requests.post(url, json=payload).json()
        # Lamports to SOL conversion (1 SOL = 10^9 Lamports)
        lamports = response.get('result', {}).get('value', 0)
        sol_balance = lamports / 1e9
        return jsonify({"balance": sol_balance, "address": address})
    except Exception as e:
        return jsonify({"error": str(e), "balance": 0}), 500

@blockchain_bp.route('/check-trigger', methods=['POST'])
def check_trigger():
    # Mocking a smart contract execution
    import uuid
    data = request.json
    return jsonify({
        "success": True,
        "tx_hash": f"{uuid.uuid4().hex}{uuid.uuid4().hex}"[:44],
        "amount": 10000
    })