import requests
from dataclasses import dataclass
from telegram.update import Update

currencies = ["usd", "eur", "uah"]

symbols = {
    "EUR": "€",
    "USD": "$",
    "UAH": "₴"
}

class InvalidExchangeQueryError(Exception):
    """Custom exception to be thrown if the exchange query has invalid syntax"""
    pass

@dataclass
class Exchange_Query():
    """
    Respresents an Exchange Query object.
    Method convert() retrieves the exchange the information from an API.
    """
    from_currency: str
    to_currency: str
    amount: str = ""
    # Calling the API
    def convert(self, API_KEY: str) -> dict:
        URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{self.from_currency}/{self.to_currency}/{self.amount}"
        response = requests.get(URL)
        return response.json()


def is_valid_exchange_query(message: str) -> tuple[bool, int]:
    """Validating the syntax of an exchange query"""
    if len(message.split()) == 4:
        command, amount, from_currency, to_currency = [x.lower() for x in message.split()]
        if (from_currency in currencies) and (to_currency in currencies):
            if from_currency != to_currency:
                try: 
                    float(amount)
                    return (True, 4)
                except ValueError:
                    return (False, 0)
    if len(message.split()) == 3:
        command, from_currency, to_currency = [x.lower() for x in message.split()]
        if (from_currency in currencies) and (to_currency in currencies):
            if from_currency != to_currency:
                return (True, 3)

    return (False, 0)


def parse_exchange_query(message: str) -> Exchange_Query:
    """
    Constructing an Exchange_Query object or throwing an error, 
    depending on the syntax validity
    """
    if (validity := is_valid_exchange_query(message))[0] == True:
        if validity[1] == 4:
            command, amount, from_currency, to_currency = [x.upper() for x in message.split()]
            return Exchange_Query(from_currency, to_currency, str(float(amount)))
        else:
            command, from_currency, to_currency = [x.upper() for x in message.split()]
            return Exchange_Query(from_currency, to_currency)
    else:
        raise InvalidExchangeQueryError("Invalid exchange query")


def handle_exchange_query(update: Update, API_KEY: str) -> None:

    try:
        query: Exchange_Query = parse_exchange_query(update.message.text)
        result_obj = query.convert(API_KEY)
        base_symbol = f"{symbols[query.from_currency]}"
        target_symbol = f"{symbols[query.to_currency]}"
        conversion_rate = f"{float(result_obj['conversion_rate'])}"
        if query.amount == "":
            update.message.reply_text(f"{base_symbol}1 = {target_symbol}{float(conversion_rate):.2f}")
        else:
            conversion_result = f"{float(result_obj['conversion_result'])}"
            update.message.reply_text(f"{base_symbol}{query.amount} = {target_symbol}{float(conversion_result):.1f}" + f" ({base_symbol}1 = {target_symbol}{float(conversion_rate):.2f})")
        
    except (InvalidExchangeQueryError):
        update.message.reply_text("❌Ошибка в записи запроса❌")
    except (requests.ConnectionError, requests.Timeout):
        update.message.reply_text("❌Ошибка при подключении к API курсов валют. Попробуйте позже.")

