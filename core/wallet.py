
from core.clients import clients, CoingeckoClient
from datetime import datetime

class Wallet:
    def __init__(self):
        self.clients = clients
        self.last_update = None
        self.asset_holdings = {}
        self._pricer = CoingeckoClient()

    async def check_balance(self):
        if not self.last_update or (datetime.now() - self.last_update).seconds > 360:
            await self._fetch_balance()
        return self.asset_holdings
    
    async def _price_assets(self):
        for asset in self.asset_holdings:
            if asset in self._pricer.assets:
                price = await self._pricer.get_price(asset)
                self.asset_holdings[asset]['usd_value'] = price * self.asset_holdings[asset]['amount']

    async def _fetch_balance(self):
        # TODO: improve speed, process in parallel
        await self._pricer.refresh_all_assets()
        self.asset_holdings = {}
        for client in self.clients:
            async with client:
                balances = await client.fetch_balances()
                for balance in balances:
                    asset = balance.asset
                    if asset not in self.asset_holdings:
                        self.asset_holdings[asset] = {
                            'amount': 0,
                            'usd_value': 0,
                            'balances': {}
                        }
                    source = balance.source
                    self.asset_holdings[asset]['balances'][source] = balance
                    self.asset_holdings[asset]['amount'] += balance.amount
        await self._price_assets()
        self.last_update = datetime.now()
        total_usd = 0
        for asset, data in self.asset_holdings.items():
            print(f"{asset}: {data['usd_value']}")
            total_usd += data['usd_value']
        print(f"Total USD: {total_usd}")