import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'farmguard-vibe-2026'
    # Get free keys from openweathermap.org and agromonitoring.com
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'YOUR_OPENWEATHER_KEY')
    AGRO_API_KEY = os.environ.get('AGRO_API_KEY', 'YOUR_AGRO_KEY')
    HELIUS_KEY = os.environ.get('HELIUS_KEY', 'YOUR_HELIUS_KEY')
    SOLANA_RPC_URL = f"https://devnet.helius-rpc.com/?api-key={HELIUS_KEY}"
    CONTRACT_ADDRESS = "7a9fB2c8D4e3c2E1a9fB2c8D4e3c2E1a9fB2c8D4e3c2E1a"
    
    # Thresholds
    DROUGHT_THRESHOLD = 100
    HEATWAVE_TEMP = 40
    CROP_HEALTH_THRESHOLD = 30 # NDVI %
    
    # Payouts
    DROUGHT_PAYOUT = 10000
    PREMIUM = 500