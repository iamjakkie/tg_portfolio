import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# exchanges:
# Binance
# GATEIO
# Coinbase
# OKX
# On-chain:
    # EVM
    # SOL
    # Uniswap LP
    # Hyperliquid
    # dydx

class BinanceClient:
    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = ccxt.binance({
            "apiKey": os.getenv("BINANCE_API_KEY"),
            "secret": os.getenv("BINANCE_API_SECRET"),
            "enableRateLimit": True,
        })
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()
    
    async def fetch_balances(self):
        async with self:
            balances_raw = await self.client.fetch_balance()
        balances = balances_raw.get('info')
        if balances:
            balances = balances.get('balances')
            return [balance for balance in balances if float(balance['free']) > 0]

class GateioClient:
    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = ccxt.gateio({
            "apiKey": os.getenv("GATEIO_API_KEY"),
            "secret": os.getenv("GATEIO_API_SECRET"),
            "enableRateLimit": True,
        })
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()
    
    async def fetch_balances(self):
        async with self:
            balances_raw = await self.client.fetch_balance()
        balances = balances_raw.get('info')
        return balances
    
class CoinbaseClient:
    def __init__(self):
        self.client = None

    async def __aenter__(self):
        self.client = ccxt.coinbaseadvanced({
            "apiKey": os.getenv("COINBASE_API_KEY"),
            "secret": os.getenv("COINBASE_API_SECRET").replace('\\n', "\n")
        })
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()
    
    async def fetch_balances(self):
        async with self:
            balances_raw = await self.client.fetch_balance()
        balances = balances_raw.get('total')
        return balances
    

clients = [BinanceClient(), GateioClient(), CoinbaseClient()]