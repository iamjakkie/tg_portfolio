import asyncio
from telegram.ext import ExtBot
from core.wallet import Wallet  # Assuming this is the correct import path

CHECK_INTERVAL = 60

def set_check_interval(interval: int):
    global CHECK_INTERVAL
    CHECK_INTERVAL = interval


async def schedule_balance_check(bot: ExtBot, chat_id: str):
    wallet = Wallet()  # Initialize your wallet object

    while True:
        try:
            # Call the main method of the wallet object
            changes = await wallet.check_and_report_changes()

            if changes:
                message = "Significant balance changes detected:\n\n" + "\n".join(changes)
                await bot.send_message(chat_id=chat_id, text=message)
            
        except Exception as e:
            error_message = f"Error during scheduled balance check: {str(e)}"
            await bot.send_message(chat_id=chat_id, text=error_message)

        await asyncio.sleep(CHECK_INTERVAL)