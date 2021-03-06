from telegram.update import Update

from typing import NamedTuple
import datetime
import json

from balance import get_balance, set_balance
import db


def fix_category(category: str):
    """
    Replace category with a proper name if it's an alias or with \"Other\" if not, or, if categories file doesn't exist, create one and add \"Other\" to it.
    """
    # If categories.json file exists
    try:
        with open("categories.json", "r", encoding="utf8") as f:
            categories: dict[str, list[str]] = json.load(f)

        for k, v in categories.items():
            if category.lower() in v:
                fixed_category = k
                return fixed_category
    # Create file and insert "Other" in it, if it doens't already exist
    except FileNotFoundError:
        with open("categories.json", "a", encoding="utf8") as f:
            categories = json.dumps({"Другое": ["другое"]}, indent=4, ensure_ascii=False)
            f.write(categories)

    fixed_category = "Другое"
    return fixed_category


class InvalidExpenseError(Exception):
    """Custom exception to be thrown if expense message has invalid syntax"""
    pass

class Expense(NamedTuple):
    date: str
    money: int
    category: str
    description: str = ""

def includes_digits(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        for char in string:
            if char.isdigit():
                return True

    return False

def capitalize_string(string: str) -> str:
    """Capitalize first letter of a string"""
    first_char, rest = string[0], string[1:]
    first_char_capitalized = first_char.upper()
    fixed_string = first_char_capitalized + rest
    return fixed_string


def is_valid_expense(message: str) -> tuple[bool, int]:
    """
    Checking syntax validity of an expense message. Examples:\n
    \"250 taxi\" -> True,\n
    \"250 cafe mcdonalds\" -> True,\n
    \"250 250\" -> False,\n
    \"250\" -> False,\n
    \"bla bla\" -> False
    """
    words = message.split()
    if len(words) == 1:
        return (False, 0)
    money, category = words[:2]
    try:
        if int(money) != 0 and (not includes_digits(category)):
            if len(words) == 2:
                return (True, 2)
            else:
                return (True, 3)
    except ValueError:
        return (False, 0)

    return (False, 0)


def parse_expense(message: str) -> Expense:
    """Constructing Expense object or throwing an error, depending on syntax validity"""
    if (validity := is_valid_expense(message))[0] == True:
        # If no description:
        if validity[1] == 2:
            money, category = message.split()
            fixed_description = ""
        # If there is a description (first letter will be capitalized)
        elif validity[1] == 3:
            money, category, *description = message.split()
            # If description is a single word:
            if len(description) == 1:
                description = description[0]
                fixed_description = description
            # If description consists of multiple words:
            else:
                description = " ".join(description)
                fixed_description = description
        
        fixed_category = fix_category(category)
        capitalized_category = capitalize_string(category)
        fixed_description = f"{capitalized_category} {fixed_description}".rstrip()

        date = ".".join(str(datetime.date.today()).split("-"))

        expense = Expense(date, int(money), fixed_category, fixed_description)
        return expense
    else:
        raise InvalidExpenseError("Invalid expense syntax")


def handle_expense(update: Update) -> None:
    """Check message validity, add expense to database and set new balance"""
    try:
        message = update.message.text    

        # Checking if function is called by Command Handler instead of Message Handler
        if message == "/expense":
            update.message.reply_text("❌ Ошибка в записи расхода")
            return
        if message.split()[0] == "/expense":
            message = " ".join(message.split()[1:])

        # Getting Expense Object
        expense: Expense = parse_expense(message)

        # Calculating and setting new balance
        new_balance = get_balance() - expense.money
        set_balance(new_balance)

        # Add the expense to the database (csv file of the current month)
        db.add_expense(expense)

        # Construct the reply depending on the description
        exp = f"Добавлен расход:\n-{expense.money} {expense.category}\n"
        bl = f"🌠 Баланс: {new_balance} грн"
        desc = ""
        if expense.description == "":
            desc = "🎇 Без описания.\n"
        else:
            desc = f"🎇 Описание: {expense.description}\n"
        update.message.reply_text(exp + desc + bl)

    except InvalidExpenseError:
        update.message.reply_text("❌ Ошибка в записи расхода")