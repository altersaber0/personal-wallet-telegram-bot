from telegram.update import Update

from expenses import Expense
from db import delete_expense, MonthParseError
from balance import get_balance, set_balance


class InvalidDeleteQuery(Exception):
    """Custom exception to be thrown in case of incorrect delete command syntax"""
    pass


def get_index_of_expense(message: str) -> int:
    """Checking syntax validity and returning the index of expense to be deleted"""

    if message == "del" or message == "/del" or len(message.split()) != 2:
        raise InvalidDeleteQuery
    
    index_string = message.split()[1]
    if index_string == "last":
        return -1

    try:
        index = int(index_string)
        if index > 0:
            return index
        elif index == -1:
            return -1
        else:   
            raise InvalidDeleteQuery

    except ValueError:
        raise InvalidDeleteQuery


def handle_expense_deletion(update: Update) -> None:
    """
    Delete requested expense from database by provided index
    and reset the balance accordingly
    """

    try:
        index = get_index_of_expense(update.message.text)

        # Getting required Expense from database and deleting it
        deleted_expense = delete_expense(index)
        deleted_expense = Expense(*deleted_expense.values())

        # Calaculating and setting new balance
        balance = get_balance()
        new_balance = balance + deleted_expense.money
        set_balance(new_balance)

        # Reply
        update.message.reply_text(f"""Удален расход:
{deleted_expense.category} {deleted_expense.money}
🎇 Описание: {deleted_expense.description}
🗓 Дата: {deleted_expense.date}
🌠 Баланс: {new_balance}
""")
    

    except (InvalidDeleteQuery, ValueError):
        update.message.reply_text("❗️ Номер расхода должен быть целым положительным числом, не превышающим общее число расходов. Или же быть равным -1 или слову \"last\", для удаления последнего расхода.")
    except MonthParseError:
        update.message.reply_text("❌ В этом месяце еще не было расходов.\nФайла не существует.")
