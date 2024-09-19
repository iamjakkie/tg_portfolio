from core.clients import clients
from datetime import datetime

class Wallet:
    def __init__(self):
        self.clients = clients
        self.last_update = None
        self.asset_holdings = {}

    async def check_balance(self):
        if not self.last_update or (datetime.now() - self.last_update).seconds > 360:
            await self._fetch_balance()
        return self.asset_holdings

    async def _fetch_balance(self):
        for client in self.clients:
            print(client)
            async with client:
                balances = await client.fetch_balances()
                print(balances)
        self.last_update = datetime.now()