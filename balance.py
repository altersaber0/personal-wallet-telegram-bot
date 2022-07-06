from typing import Dict
from telegram.update import Update
from requests import ConnectionError, Timeout
import exchange


class InvalidBalanceQuery(Exception):
    """Custom exception to be thrown in case of an invalid balance query"""
    pass


def get_balance() -> int:
    """Getting current balance or throw IOError if file doesn't exist yet"""

    with open("balance.txt", "r") as f:
        balance = f.read()
    return int(balance)


def set_balance(new_balance: int) -> None:
    """Overriding (or creating) balance by a new value"""
    with open("balance.txt", "w") as f:
        f.write(f"{new_balance}")


def convert_balance(message: str, API_KEY: str) -> Dict:
    """Converting balance to another currency"""
    command, currency = message.split()
    balance = get_balance()
    query = exchange.Exchange_Query("UAH", currency.upper(), balance)
    result_obj = query.convert(API_KEY)
    base_symbol = "₴"
    try:
        target_symbol = f"{exchange.symbols[query.to_currency]}"
    except:
        raise exchange.InvalidExchangeQueryError
    conversion_rate = f"{float(result_obj['conversion_rate'])}"
    conversion_result = f"{float(result_obj['conversion_result'])}"
    return {
        "base_symbol": base_symbol,
        "target_symbol": target_symbol,
        "conversion_rate": conversion_rate,
        "conversion_result": conversion_result
    }


def get_type_of_balance_query(message: str) -> str:
    words = message.split()
    if len(words) > 2:
        raise InvalidBalanceQuery
    if len(words) == 2:
        if words[1] in exchange.currencies:
            return "convert"
        try:
            int(words[1])
            return "set"
        except ValueError:
            pass
    if len(words) == 1:
        return "get"
    raise InvalidBalanceQuery


def handle_balance_query(update: Update, API_KEY: str) -> None:
    """Send, set new, or convert balance to another currency depending on the command syntax"""
    try:
        query_type = get_type_of_balance_query(update.message.text)
        # Getting
        if query_type == "get":
            try:
                balance = get_balance()
                update.message.reply_text(f"🌠 Баланс: {balance} грн")
            except IOError:
                update.message.reply_text(
                    "Баланс еще не определен.\nСначала определите его (bl {число}).")
        # Updating
        if query_type == "set":
            new_balance = int(update.message.text.split()[1])
            set_balance(new_balance)
            update.message.reply_text(f"⚡️ Баланс: {new_balance} грн")
        # Converting
        if query_type == "convert":
            result_obj = convert_balance(update.message.text, API_KEY)
            # result_obj["base_symbol"]
            update.message.reply_text(f"{result_obj['base_symbol']}{get_balance()} = {result_obj['target_symbol']}{float(result_obj['conversion_result']):.2f}" + f" ({result_obj['base_symbol']}1 = {result_obj['target_symbol']}{float(result_obj['conversion_rate'])})")
    except InvalidBalanceQuery:
        update.message.reply_text("❌Ошибка в записи запроса❌")
    except (ConnectionError, Timeout):
        update.message.reply_text("❌Ошибка при подключении к API курсов валют. Попробуйте позже.")