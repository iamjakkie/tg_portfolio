import asyncio
import aiohttp
import ccxt.async_support as ccxt
import os
from dotenv import load_dotenv
from web3 import Web3
from dataclasses import dataclass

load_dotenv()

# exchanges:
# Binance x
# GATEIO x
# Coinbase x
# OKX
# On-chain:
    # EVM
    # SOL
    # Uniswap LP
    # Hyperliquid x
    # dydx x

@dataclass
class Balance:
    source: str
    asset: str
    amount: float
    usd_value: float = 0.0


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
        balances_raw = await self.client.fetch_balance()
        balances = balances_raw.get('info')
        if balances:
            balances = balances.get('balances')
            return [Balance(source='BINANCE', asset=balance['asset'], amount=float(balance['free'])) for balance in balances if float(balance['free']) > 0]

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
        balances_raw = await self.client.fetch_balance()
        balances = balances_raw.get('info')
        return [Balance(source='GATEIO', asset=balance['currency'], amount=float(balance['available'])) for balance in balances]
    
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
        balances_raw = await self.client.fetch_balance()
        balances = balances_raw.get('total')
        #rename ETH2 to ETH
        if 'ETH2' in balances:
            balances['ETH'] = balances.pop('ETH2')
        return [Balance(source='COINBASE', asset=asset, amount=float(amount)) for asset, amount in balances.items() if float(amount) > 0]
    
class HyperliquidClient:
    def __init__(self, address):
        self.address = address

    async def __aenter__(self):
        self.client = ccxt.coinbaseadvanced({
            "walletAddress": self.address
        })
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()
    
    async def fetch_balances(self):
        balances_raw = await self.client.fetch_balance()
        balances = balances_raw.get('total')
        return balances
        # return [Balance(source='HYPERLIQUID', asset=balance['currency'], amount=float(balance['available'])) for balance in balances]
    
class DydxClient:
    def __init__(self, wallet):
        ...
    
class EVMCLient:
    def __init__(self, wallet):
        self.blockchains = ['eth-mainnet', 'opt-mainnet', 'polygon-mainnet',
                            'arb-mainnet', 'base-mainnet', 'avax-mainnet']
        self.headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }
        self.wallet = wallet 

    async def __aenter__(self):
        self.client = aiohttp.ClientSession(headers=self.headers)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()

    async def map_contract(self, blockchain, contract):
        url = f'https://{blockchain}.g.alchemy.com/v2/{os.getenv("ALCHEMY_API_KEY")}'

        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getTokenMetadata",
            "params": [contract]
        }

        response = await self.client.post(url, json=payload)
        response = await response.json()
        token_data = response.get('result')
        decimals = token_data.get('decimals')
        symbol = token_data.get('symbol')
        return symbol, decimals
    
    async def fetch_balances(self):
        for blockchain in self.blockchains:
            url = f'https://{blockchain}.g.alchemy.com/v2/{os.getenv("ALCHEMY_API_KEY")}'

            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "alchemy_getTokenBalances",
                "params": [self.wallet]
            }
            
            response = await self.client.post(url, json=payload)
            response = await response.json()
            balances = response.get('result')
            token_balances = balances.get('tokenBalances')
            final_balances = []
            for token in token_balances:
                contract_address = token['contractAddress']
                balance = token['tokenBalance']
                token_balance_int = int(balance[2:], 16)
                token_symbol, decimals = await self.map_contract(blockchain, contract_address)
                token_balance = token_balance_int / 10 ** decimals
                print(f"{contract_address}, {token_symbol}: {token_balance}")
                final_balances.append(Balance(source=blockchain, asset=token_symbol, amount=token_balance))
            return final_balances
        
class CoingeckoClient:
    def __init__(self):
        self._base_url = "https://pro-api.coingecko.com/api/v3"
        self._headers = {
            "accept": "application/json",
            "x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")
        }
        self.fiats = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'KRW']
        self.usd_pegged_stables = ['USDT', 'USDC', 'FDUSD']
        self.main_assets = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'AVAX': 'avalanche-2',
            'TRX': 'tron',
        }
        self.assets = None

    async def _get_data_from_address(self, blockchain, address):
        ...


    async def refresh_all_assets(self):
        url = f"{self._base_url}/coins/list?include_platform=true"
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.get(url) as response:
                response = await response.json()
                self.assets = {asset['symbol'].upper(): asset['id'] for asset in response}
        self.assets.update(self.main_assets)

    async def get_price(self, asset):
        if asset in self.fiats or asset in self.usd_pegged_stables:
            return 1
        if not self.assets:
            await self.refresh_all_assets()
        url = f"{self._base_url}/simple/price?ids={self.assets[asset]}&vs_currencies=usd"
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.get(url) as response:
                response = await response.json()
                return response[self.assets[asset]]['usd']
    
clients = [EVMCLient('0xa49D6B59ccC2c1544a9DeAAC77A0ecF77907ef86')]
# clients = [BinanceClient(), GateioClient(), CoinbaseClient(), EVMCLient('0xa49D6B59ccC2c1544a9DeAAC77A0ecF77907ef86')]