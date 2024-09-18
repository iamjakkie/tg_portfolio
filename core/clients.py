import ccxt.async_support as ccxt
import os

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

