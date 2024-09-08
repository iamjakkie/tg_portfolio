import asyncio
from telegram.ext import ExtBot
from .config import CHECK_INTERVAL, CHAT_ID
from core.wallet import Wallet  # Assuming this is the correct import path

async def schedule_balance_check(bot: ExtBot):
    wallet = Wallet()  # Initialize your wallet object

    while True:
        try:
            # Call the main method of the wallet object
            changes = await wallet.check_and_report_changes()

            if changes:
                message = "Significant balance changes detected:\n\n" + "\n".join(changes)
                await bot.send_message(chat_id=CHAT_ID, text=message)
            
        except Exception as e:
            error_message = f"Error during scheduled balance check: {str(e)}"
            await bot.send_message(chat_id=CHAT_ID, text=error_message)

        await asyncio.sleep(CHECK_INTERVAL)