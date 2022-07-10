from telegram.update import Update
import os

# My modules
import expenses
import incomes
import balance
import exchange
import month
import deleting
import utils


@utils.authorize
def start(update: Update, context):
    update.message.reply_text("""
    Бот для учета расходов и доходов.
    """)

@utils.authorize
def help(update: Update, context):
    update.message.reply_text("""
    Список команд:
/start  -> Начало работы.
/help   -> Это сообщение.
bl  -> Посмотреть баланс.
bl {число}  -> Установить новый баланс.
bl {валюта}  -> Перевести баланс в другую валюту.
{число} {категория} {описание}  -> Добавить расход. Описание опционально.
del {номер}  -> Удалить расход по номеру в списке месяца. -1 или \"last\" удаляет последний.
+ {число} {источник}  -> Добавить доход.
месяц   -> Список всех расходов за текущий месяц.
месяц YYYY.MM  ->  Статистика расходов за месяц YYYY.MM
cv {из} {в}  -> Курс первой валюты ко второй.
cv {число} {из} {в}  -> Перевод суммы из одной валюты в другую.
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

@utils.authorize
def delete_expense(update: Update, context):
    deleting.handle_expense_deleting(update)

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
        case "delete":
            deleting.handle_expense_deleting(update)
        case _:
            update.message.reply_text("Неизвестная команда😐")