from typing import NamedTuple
from telegram.update import Update
from balance import get_balance, set_balance


class InvalidIncomeError(Exception):
    pass

class Income(NamedTuple):
    money: int
    source: str


def is_valid_income(message: str) -> bool:
    """
    Checking syntax validity of the income message. Example:\n
    \"+ 250 from someone\" -> True
    """
    try:
        money = message.split()[1]
    except IndexError:
        return False
    try:
        if float(money) != 0:
            return True
    except ValueError:
        return False
    
    return False


def parse_income(message: str) -> Income:
    """Construct an Income object or throw an error, depending on syntax validity"""
    if is_valid_income(message):
        money = message.split()[1]

        # Get part of a message after a number and remove useless whitespaces from it
        source = " ".join(message.partition(money)[2].split())
        return Income(int(float(money)), source)
    else:
        raise InvalidIncomeError("Invalid income syntax")


def handle_income(update: Update) -> None:
    try:
        # Getting Income object
        income: Income = parse_income(update.message.text)

        # Calculating and setting new balance
        new_balance = get_balance() + income.money
        set_balance(new_balance)

        update.message.reply_text(f"Добавлен доход:\n+{income.money} {income.source}\n🌠 Баланс: {new_balance} грн")

    except InvalidIncomeError:
        update.message.reply_text("❌Ошибка в записи дохода❌")
