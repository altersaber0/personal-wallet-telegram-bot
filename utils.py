from telegram.update import Update
from os import getenv


def authorize(func):
    """Decorator for all command and message handlers, ensures responding only to given User ID (my)"""
    def wrapper(update: Update, *args, **kwargs):
        if update.effective_user.id != int(getenv("TELEGRAM_USER_ID")):
            update.message.reply_text("Access denied")
            return
        return func(update, *args, **kwargs)
    
    return wrapper


def get_type_of_message(message: str) -> str:
    """Parse first word of a message to determine its type"""
    command = message.split()[0]
    try:
        int(command[0])
        return "expense"
    except ValueError:
        pass
    if command[0] == "+":
        return "income"
    if command in ["bl", "balance", "total", "Баланс", "баланс", "Всего", "всего"]:
        return "balance"
    if command == "cv" or command == "convert":
        return "exchange_query"
    if command.lower() in ["месяц", "month"]:
        return "month"
    # if command[0] == ".":
    #     return "todo"
    # if command[0] == "?":
    #     return "search"
    return "nonsense"
