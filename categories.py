# -*- coding: utf-8 -*-
import json
import os
from telegram.update import Update

from deleting import InvalidDeleteQuery


def parse_message(message: str) -> tuple[str, list[str]]:
    """Extract new category name and all aliases from message"""
    message = " ".join(message.split()[1:])

    if not (":" in message):
        raise InvalidDeleteQuery
    
    # Split by first ":"
    name_substring, sep, aliases_substring = message.partition(":")

    # Get list of all aliases from substring
    aliases = []
    current_word = ""
    for char in aliases_substring:
        if char.isalpha():
            current_word += char
        else:
            if current_word == "":
                continue
            aliases.append(current_word)
            current_word = ""
    if current_word != "":
        aliases.append(current_word)

    # Prettify
    name = name_substring.lower().capitalize()
    aliases = [alias.lower() for alias in aliases]

    return (name, aliases)


def add_category(name, aliases) -> None:
    """Add new category to categories.json (create if doesn't exist)."""

    path_to_categories_file = os.path.join(os.getcwd(), "categories.json")

    # Add "Other" if first time creating file
    if not os.path.exists(path_to_categories_file):
        with open("categories.json", "a", encoding="utf8") as f:
            categories = json.dumps({"Другое": ["другое"], name: aliases}, indent=4, ensure_ascii=False)
            f.write(categories)
            return

    # Actual addition
    with open("categories.json", "r+", encoding="utf8") as f:
        categories = json.load(f)
        categories[name] = aliases
        new_categories = json.dumps(categories, indent=4, ensure_ascii=False)
        f.truncate()
        f.seek(0)
        f.write(new_categories)
        return
    

def delete_category(name: str) -> None:
    """Delete category by its name (key in the dictionary)."""

    # Turn name into normal form
    name = name.lower().capitalize()
    
    # Can raise KeyError and FileNotFoundError
    with open("categories.json", "r+", encoding="utf8") as f:
        categories = json.load(f)
        del categories[name]
        new_categories = json.dumps(categories, indent=4, ensure_ascii=False)

        f.truncate(0)
        f.seek(0)
        f.write(new_categories)
        return


def handle_addition(update: Update) -> None:
    """Check message validity, then add category and aliases to categories.json"""
    try:
        name, aliases = parse_message(update.message.text)
        add_category(name, aliases)

        reply = f"Добавлена новая категория \"{name}\"\nСинонимы: "
        reply += ", ".join(aliases)

        update.message.reply_text(reply)
    
    except InvalidDeleteQuery:
        update.message.reply_text("❌ Неправильный формат записи категории. Должно быть:\n{Имя}:{синоним}, {синоним}, ...")
    
def handle_deletion(update: Update) -> None:
    """Delete category by name in message"""
    try:
        name = update.message.text.partition(" ")[2]
        delete_category(name)

        update.message.reply_text(f"Удалена категория: {name.lower().capitalize()}")
    except KeyError:
        update.message.reply_text("❌ Указанная категория не существует.")
    except FileNotFoundError:
        update.message.reply_text("❌ Категории еще не добавлены. Файла на существует.")

def show_categories(update: Update) -> None:
    """Reply with all available categories or warn that file doesn't exist."""
    try:
        with open("categories.json", "r", encoding="utf8") as f:
            categories = json.load(f)
        
        reply = "Категории:\n"
        for name, aliases in categories:
            reply += f"{name}: "
            reply += ", ".join(aliases)
            reply += "\n"
        
        update.message.reply_text(reply)
    except FileNotFoundError:
        update.message.reply_text("❌ Категории еще не добавлены. Файла на существует.")