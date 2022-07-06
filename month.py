from os import getcwd, remove
import os.path
import datetime

from telegram.update import Update

import db
from expenses import Expense


def is_valid_month(message: str) -> bool:
    """YYYY.MM -> True"""
    date = message.split()[1]
    try:
        year, month = date.split(".")
        if (len(year) != 4) or (len(month) != 2):
            return False
        for char in year:
            if not char.isdigit():
                return False
        for char in month:
            if not char.isdigit():
                return False
    except:
        return False
    
    return True


def handle_month_query(update: Update):

    # Get all expenses in current month
    if update.message.text.lower() == "месяц" or update.message.text.lower() == "month":
        try:
            expenses = db.current_month_expenses()
            expenses = [Expense(*expense) for expense in expenses]
            msg = ""
            for index, expense in enumerate(expenses):
                msg += f"{index+1}. {expense.money} {expense.category}\nОписание: {expense.description}Дата: {expense.date}\n"
            update.message.reply_text(msg)
            current_month = db.fixed_month(datetime.date.today())
            current_month_file_path = db.path_of_month(current_month)
            update.message.reply_document(document=open(current_month_file_path, encoding="utf8"))
        except db.MonthParseError:
            update.message.reply_text("В этом месяце еще не было расходов.\nФайла не существует")
        return
    if not is_valid_month(update.message.text):
        update.message.reply_text("Ошибка в записи месяца.\nФормат должен быть YYYY.MM")
        return

    # Get statistic and barchart of the given month
    month = update.message.text.split()[1]
    try:
        month_stat = db.month_stat(month)
    except db.MonthParseError:
        update.message.reply_text("В данном месяце не было расходов.\nФайла не существует")
        return

    msg = f"""
Месяц: {month_stat["month"]}
Всего потрачено: {month_stat["total"]}
Количество расходов: {month_stat["quantity"]}\n
Самые большие расходы:
"""
    for index, expense in enumerate(month_stat['biggest_expenses']):
        msg += f"""{index+1}. {expense['money']} {expense['category']}
Описание: {expense['description']}
Дата: {expense['date']}
"""

    db.generate_bar_chart_img(month_stat)
    update.message.reply_text(msg)

    photo_path = os.path.join(getcwd(), f"{month}.png")
    update.message.reply_photo(photo=open(photo_path, "rb"))

    month_file_path = db.path_of_month(month)
    update.message.reply_document(document=open(month_file_path, encoding="utf8"))

    # Delete the png
    remove(photo_path)