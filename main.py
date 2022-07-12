# Environment variables and threading for terminal loop
from dotenv import load_dotenv
import os
import threading

# Telegram stuff
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# My Modules
import controller
import cli


def main():
        
    load_dotenv()

    # Initializing the Bot
    updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    dp = updater.dispatcher

    # Custom Filter to filter down any requests from all users except me (my User ID)
    correct_user_filter = Filters.user(user_id=int(os.getenv("TELEGRAM_USER_ID")))

    # All handlers
    dp.add_handler(CommandHandler("start", controller.start, filters=correct_user_filter))
    dp.add_handler(CommandHandler("help", controller.help, filters=correct_user_filter))
    dp.add_handler(CommandHandler("expense", controller.expense, filters=correct_user_filter))
    dp.add_handler(CommandHandler("income", controller.income, filters=correct_user_filter))
    dp.add_handler(CommandHandler("balance", controller.balance_query, filters=correct_user_filter))
    dp.add_handler(CommandHandler("convert", controller.convert, filters=correct_user_filter))
    dp.add_handler(CommandHandler("month", controller.month_query, filters=correct_user_filter))
    dp.add_handler(CommandHandler("delete", controller.delete_expense, filters=correct_user_filter))
    dp.add_handler(CommandHandler("categories", controller.show_categories, filters=correct_user_filter))
    dp.add_handler(CommandHandler("add_category", controller.add_category, filters=correct_user_filter))
    dp.add_handler(CommandHandler("delete_category", controller.delete_category, filters=correct_user_filter))
    dp.add_handler(MessageHandler(Filters.text & correct_user_filter, controller.handle_message))

    print("Bot running...")

    # Creating a separate thread for recieving terminal commands
    terminal_thread = threading.Thread(target=cli.terminal_loop)
    terminal_thread.start()

    # Starting connection to Telegram servers
    updater.start_polling(poll_interval=1, timeout=5)

    # Block main thread from dying
    updater.idle()


if __name__ == "__main__":
    main()