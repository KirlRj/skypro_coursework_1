import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv


def get_greeting(dt: datetime) -> str:
    """Функция определения приветствия и формирования списка словарей"""
    hour = dt.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def read_excel_by_date(file_path: str, in_date: str, sheet_name: int = 0) -> pd.DataFrame:
    """Функция считывает Excel-файл по дате"""

    end_date = datetime.strptime(in_date, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    try:
        excel_data = pd.read_excel(file_path, sheet_name=sheet_name)
        excel_data["Дата операции"] = pd.to_datetime(excel_data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_excel_data = excel_data[
            (excel_data["Дата операции"] >= start_date) & (excel_data["Дата операции"] <= end_date)
        ]
        return filtered_excel_data

    except Exception as e:
        print(f"Ошибка чтения Excel: {e}")
        raise


def calculate_cards(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Функция считающая сумму и кэшбэк и выводит список словарей"""
    cards = []
    for card, group in df.groupby("Номер карты"):
        total_spent = float(group["Сумма платежа"].abs().sum())
        cashback = float(total_spent / 100)
        cards.append(
            {
                "last_digits": str(card)[-4:],
                "total_spent": round(total_spent, 2),
                "cashback": round(cashback, 2),
            }
        )
    return cards


def top_transactions(df: pd.DataFrame, count_tr: int = 5) -> List[Dict[str, str]]:
    """Возвращает топ транзакций по абсолютной сумме платежа. По умолчанию 5"""
    top_count = df.iloc[df["Сумма платежа"].abs().argsort()[::-1]].head(count_tr)
    top_transaction = []
    for transaction, group in top_count.iterrows():
        top_transaction.append(
            {
                "date": group["Дата платежа"],
                "amount": group["Сумма платежа"],
                "category": group["Категория"],
                "description": group["Описание"],
            }
        )

    return top_transaction


def read_json(filename: Path | str) -> Dict[str, Any]:
    """функция читает json файл. Если есть ошибки, то выводит пустой файл"""
    try:

        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {}

        return data

    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_currency_rates(user_data: Dict[str, Any], base: str = "RUB") -> list[Any] | dict[Any, Any]:
    """Функция возвращает курсы валют из списка user_currencies относительно base валюты."""
    load_dotenv()
    api_key = os.getenv("API_KEY_CURR")
    api_url = os.getenv("API_URL_CURR")

    if not api_url:
        raise ValueError("API_URL не определен!")
    if not api_key:
        raise ValueError("API_KEY не определен")

    currencies = ",".join(user_data["user_currencies"])
    params = {"access_key": api_key, "currencies": currencies, "source": base}

    headers = {"apikey": api_key} if api_key else {}

    try:
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        rates = data.get("quotes", {})

        currency_rates = []

        for key, value in rates.items():
            currency = key[len(base) :]
            if value != 0:
                rate = round(1 / value, 4)
            else:
                rate = 0
            currency_rates.append({"currency": currency, "rate": rate})
        return currency_rates
    except requests.RequestException as e:
        print(f"Ошибка при получении курса валют: {e}")
        return {}


def get_stock_price(user_data: Dict[str, Any]) -> List[Any] | dict[Any, Any]:
    """Функция возвращает цену акций из списка user_stocks относительно валюты RUB."""
    load_dotenv()
    api_key = os.getenv("API_KEY_STOCK")
    api_url = os.getenv("API_URL_STOCK")

    if not api_url:
        raise ValueError("API_URL не определен!")
    if not api_key:
        raise ValueError("API_KEY не определен")

    price_stock = []
    stocks = user_data.get("user_stocks", [])

    for stock in stocks:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": api_key}
        try:
            response = requests.get(api_url, params=params)
            data = response.json()

            quote = data.get("Global Quote", {})
            price_str = quote.get("05. price")

            if price_str is None or price_str.strip() == "":
                price = None
                price_stock.append({"stock": stock, "price": price})
            else:
                price = float(price_str)
                price_stock.append({"stock": stock, "price": price})

        except requests.RequestException as e:
            print(f"Ошибка при получении цены {stock}: {e}")
            continue
    return price_stock
