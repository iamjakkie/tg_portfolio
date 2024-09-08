import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from bot.handlers import start, list_accounts, add_account, edit_account, remove_account, check_balance, cancel
from bot.scheduler import schedule_balance_check


async def main():
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    account_handler = ConversationHandler(
        entry_points = [
            CommandHandler("add", add_account),
            CommandHandler("edit", edit_account),
            CommandHandler("delete", delete_account),
        ],
        states = {
            ADD_ACCOUNT: [MessageHandler(filters.TEXT, add_account)],
            EDIT_ACCOUNT: [MessageHandler(filters.TEXT, edit_account)],
            DELETE_ACCOUNT: [MessageHandler(filters.TEXT, delete_account)],
        },
        fallbacks = [CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_accounts))
    application.add_handler(CommandHandler("check", check_balance))
    application.add_handler(account_handler)
    
    await application.initialize()
    await application.start()
    
    asyncio.create_task(schedule_balance_check(application.bot))
    
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

