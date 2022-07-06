# Environment variables and threading for terminal loop
from ctypes import util
from dotenv import load_dotenv
import os
import threading

# Telegram stuff
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update

# My modules
import expenses
import incomes
import balance
import exchange
import month
import utils
import cli


# Start command handler function
@utils.authorize
def start(update: Update, context):
    update.message.reply_text("""
    Бот для учета расходов и доходов.
    """)

# Help command handler function
@utils.authorize
def help(update: Update, context):
    update.message.reply_text("""
    Список команд:
/start  -> Начало работы
/help   -> Это сообщение
bl  -> Посмотреть баланс
bl {число}  -> Установить новый баланс
bl {валюта}  -> Перевести баланс в другую валюту
{число} {категория} {описание}  -> Добавить расход
+ {число} {источник}  -> Добавить доход
месяц   -> Список всех расходов за текущий месяц
месяц YYYY.MM  ->  Статистика расходов за месяц YYYY.MM
cv {из} {в}  -> Курс первой валюты ко второй
cv {число} {из} {в}  -> Перевод суммы из одной валюты в другую
    """)

@utils.authorize
def expense(update: Update, context):
    expenses.handle_expense(update)

@utils.authorize
def income(update: Update, context):
    incomes.handle_income(update)

@utils.authorize
def balance_query(update: Update, context):
    balance.handle_balance_query(update, API_KEY=os.getenv("EXCHANGE_RATE_API_KEY"))

@utils.authorize
def convert(update: Update, context):
    exchange.handle_exchange_query(update, API_KEY=os.getenv("EXCHANGE_RATE_API_KEY"))

@utils.authorize
def month_query(update: Update, context):
    month.handle_month_query(update)

# Handle message based on its type (first word determines the type)
@utils.authorize
def handle_message(update: Update, context):
    message_type = utils.get_type_of_message(update.message.text)
    match message_type:
        case "expense":
            expenses.handle_expense(update)
        case "income":
            incomes.handle_income(update)
        case "balance":
            balance.handle_balance_query(update, API_KEY=os.getenv("EXCHANGE_RATE_API_KEY"))
        case "exchange_query":
            exchange.handle_exchange_query(update, API_KEY=os.getenv("EXCHANGE_RATE_API_KEY"))
        case "month":
            month.handle_month_query(update)
        case _:
            update.message.reply_text("Неизвестная команда😐")



def main():

    load_dotenv()

    # Initializing the Bot
    updater = Updater(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    dp = updater.dispatcher

    # Custom Filter to filter down any requests from all users except me (my User ID)
    correct_user_filter = Filters.user(user_id=int(os.getenv("TELEGRAM_USER_ID")))

    # All handlers
    dp.add_handler(CommandHandler("start", start, filters=correct_user_filter))
    dp.add_handler(CommandHandler("help", help, filters=correct_user_filter))
    dp.add_handler(CommandHandler("expense", expense, filters=correct_user_filter))
    dp.add_handler(CommandHandler("income", income, filters=correct_user_filter))
    dp.add_handler(CommandHandler("balance", balance_query, filters=correct_user_filter))
    dp.add_handler(CommandHandler("convert", convert, filters=correct_user_filter))
    dp.add_handler(CommandHandler("month", month_query, filters=correct_user_filter))
    dp.add_handler(MessageHandler(Filters.text & correct_user_filter, handle_message))

    print("Bot running...")
  
    # Creating a separate thread for recieving terminal commands
    terminal_thread = threading.Thread(target=cli.terminal_loop)
    terminal_thread.start()

    # Starting connection to Telegram servers
    updater.start_polling(poll_interval=5, timeout=5)
    updater.idle()


if __name__ == "__main__":
    main()