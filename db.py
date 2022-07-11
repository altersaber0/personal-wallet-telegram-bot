import datetime
import os.path
from os import getcwd
import json
import pandas as pd
import matplotlib.pyplot as plt


class MonthParseError(Exception):
    """Custom exception to be thrown if requsted {month}.csv file doesn't exist"""
    pass


def fixed_month(date: datetime.date) -> str:
    """Replace the "-" by "." in date and cut the day to leave only YYYY.MM"""

    return ".".join(str(date).split("-")[:2])


def path_of_month(month: str) -> str:
    """Getting absolute path to the {month}.csv file"""

    cwd = getcwd()
    expenses_dir_path = os.path.join(cwd, "expenses")
    month_file_path = os.path.join(expenses_dir_path, month + ".csv")
    return month_file_path


def add_expense(expense) -> None:
    """Add expense to a csv file of the current month"""
    month = fixed_month(datetime.date.today())
    month_file_path = path_of_month(month)

    # Creating {month}.csv file if it doesn't exist yet and add the headers
    if not os.path.exists(month_file_path):
        with open(month_file_path, "a", encoding="utf8") as f:
            f.write("Номер|Дата|Сумма|Категория|Описание\n")

    # Calculating index for expense
    new_index = ""
    with open(month_file_path, "r", encoding="utf8") as f:
        if (last_number := f.readlines()[-1].split("|")[0]) == "Номер":
            new_index = "1"
        elif last_number.isdigit():
            new_index = int(last_number) + 1
    
    # Full list of parameters for writing into file
    full_list = [str(x) for x in (new_index, *expense._asdict().values())]
    
    # Appending the expense in following format: "...|...|...|...|..."
    with open(month_file_path, "a", encoding="utf8") as f:
        new_line = "|".join(full_list) + "\n"
        f.write(new_line)


def delete_expense(index: int):
    """Delete expense from database by its index in the current month"""

    # Getting path to file of the current month
    month = fixed_month(datetime.date.today())
    month_file_path = path_of_month(month)

    # Creating DataFrame
    try:
        df = pd.read_csv(month_file_path, sep="|")
    except FileNotFoundError:
        raise MonthParseError

    if index > df.tail(1).index + 1:
        raise ValueError

    if index > 0:
        # Getting the expense to be deleted for returning from the function
        row = df.iloc[index-1]
        deleted_expense = {
            "date": row["Дата"],
            "money": int(row["Сумма"]),
            "category": row["Категория"],
            "description": row["Описание"]
        }

        # Deleting the expense
        df.drop(index=index-1, axis=0, inplace=True)

        # Resetting new index for every left expense
        df.reset_index(drop=True, inplace=True)
        for i in range(len(list((df.iterrows())))):
            df.loc[i, ["Номер"]] = i + 1
    
    if index == -1:
        # Getting the expense to be deleted for returning from the function
        row = df.iloc[index]
        deleted_expense = {
            "date": row["Дата"],
            "money": int(row["Сумма"]),
            "category": row["Категория"],
            "description": row["Описание"]
        }
    
        # Deleting the expense
        df.drop(df.tail(1).index, axis=0, inplace=True)

    # Saving file
    df.to_csv(month_file_path, sep="|", index=False)

    return deleted_expense


def current_month_expenses() -> list[list[str]]:
    """Get all current month expenses as a list"""
    expenses = []

    # Constructing path to the file
    month = fixed_month(datetime.date.today())
    month_file_path = path_of_month(month)

    # Opening the file if it exists or throwing FileNotFoundError
    try:
        with open(month_file_path, "r", encoding="utf8") as file:
            # Skip headers (first line)
            next(file)
            for line in file:
                expense_attributes_list = line.split("|")[1:]
                expenses.append(expense_attributes_list)
    except FileNotFoundError:
        raise MonthParseError

    return expenses

def month_stat(month: str):
    """Get requsted month statistic in dictionary form."""
    # Creating DataFrame from {month}.csv file
    month_file_path = path_of_month(month)
    try:
        df = pd.read_csv(month_file_path, sep="|")
    except:
        raise MonthParseError("Файла не существует")
    
    # Total number of expenses
    quantity = int(df.tail(1)["Номер"])

    # Total money spent in this month:
    total = 0
    for index, row in df.iterrows():
        total += row["Сумма"]


    # Single biggest expenses:

    sorted_df = df.sort_values("Сумма", ascending=False, inplace=False)
    # Turning empty descriptions (NaN) into empty strings ""
    sorted_notnull_df = sorted_df.where(pd.notnull(sorted_df), "")
    biggest_expenses = []
    for i in range(5):
        expense_df = sorted_notnull_df.iloc[i]
        expense = {
            "date": expense_df["Дата"],
            "money": expense_df["Сумма"],
            "category": expense_df["Категория"],
            "description": expense_df["Описание"]
        }
        biggest_expenses.append(expense)


    # Total money spent in each category:

    # Getting all category names
    with open("categories.json", "r", encoding="utf8") as f:
        categories = json.load(f)
        categories = categories.keys()
    # Creating dictionary with all 0 values as counters for each category
    each_category_total = {cat: 0 for cat in categories}
    for index, row in df.iterrows():
        money = row["Сумма"]
        category = row["Категория"]
        each_category_total[category] += money

    return {
        "month": month,
        "total": total,
        "quantity": quantity,
        "biggest_expenses": biggest_expenses,
        "each_category_total": each_category_total
    }

def generate_bar_chart_img(month_statistic):
    """Generate Matplotlib barchart based on month statistic and save it to {month}.png"""
    data: dict = month_statistic["each_category_total"]
    categories = list(data.keys())
    values = list(data.values())

    # Creating the diagram and signing both axis with labels
    plt.figure(figsize=(10,6))
    plt.xticks(range(len(data)), categories)
    plt.xlabel("Категории расходов", labelpad=10)
    plt.ylabel("Общая сумма, грн")

    # Title will be the english name of the month + year in number form
    full_date = [int(x) for x in f"{month_statistic['month']}.01".split(".")]
    date_obj = datetime.datetime(*full_date)
    plt.title(date_obj.strftime("%B %Y"))

    # Creating bars on the diagram, height is based on the total spending in each category
    bar_chart = plt.bar(range(len(data)), values, width=0.5)
    for index, rect in enumerate(bar_chart):
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2, height + 8, values[index], ha="center")

    # Saving as {month}.png for future reply and following removal
    plt.savefig(f"{month_statistic['month']}.png")