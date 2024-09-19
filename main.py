import asyncio
import telebot.async_telebot
import os

from bot import handlers
from core.wallet import Wallet



async def check(wallet):
    await asyncio.sleep(5)
    while True:
        try:
            await wallet.check_balance()
        except Exception as e:
            print(e)
        await asyncio.sleep(5)

async def main():
    wallet = Wallet()
    check_task = asyncio.create_task(check(wallet))

    await asyncio.gather(check_task)

if __name__ == "__main__":
    asyncio.run(main())