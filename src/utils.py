import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

dir = Path(__file__).resolve().parent.parent
log_path = dir / "log.txt"
utils_logger = logging.getLogger("utils.py")
utils_logger.setLevel(logging.DEBUG)
utils_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
utils_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
utils_handler.setFormatter(utils_formatter)
utils_logger.addHandler(utils_handler)


def get_greeting(dt: datetime) -> str:
    """Функция определения приветствия и формирования списка словарей"""
    utils_logger.info("Запуск функции get_greeting ")
    hour = dt.hour

    if 6 <= hour < 12:
        utils_logger.info("Работа функции get_greeting завершена без ошибок.")
        return "Доброе утро"
    elif 12 <= hour < 18:
        utils_logger.info("Работа функции get_greeting завершена без ошибок.")
        return "Добрый день"
    elif 18 <= hour < 24:
        utils_logger.info("Работа функции get_greeting завершена без ошибок.")
        return "Добрый вечер"
    else:
        utils_logger.info("Работа функции get_greeting завершена без ошибок.")
        return "Доброй ночи"


def read_excel_by_date(file_path: str, in_date: str | None = None, sheet_name: int = 0) -> pd.DataFrame:
    """Функция считывает Excel-файл по дате. Если даты нет, берет текущую."""
    utils_logger.info("Запуск функции read_excel_by_date ")

    try:
        utils_logger.info("Чтение данных из excel файла...")
        excel_data = pd.read_excel(file_path, sheet_name=sheet_name)
        excel_data["Дата операции"] = pd.to_datetime(excel_data["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        if in_date is None:
            utils_logger.info("Дата не передана. Возвращаем весь файл.")
            utils_logger.info("Работа функции read_excel_by_date завершена без ошибок.")
            return excel_data

        end_date = datetime.strptime(in_date, "%Y-%m-%d %H:%M:%S")
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        filtered_excel_data = excel_data[
            (excel_data["Дата операции"] >= start_date) & (excel_data["Дата операции"] <= end_date)
        ]
        utils_logger.info("Работа функции read_excel_by_date завершена без ошибок.")
        return filtered_excel_data
    except Exception:
        utils_logger.exception("Ошибка чтения Excel. Функция завершена с ошибкой")
        raise


def calculate_cards(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Функция считающая сумму и кэшбэк и выводит список словарей"""
    utils_logger.info("Запуск функции calculate_cards")

    cards = []

    utils_logger.info("Фильтрация данных...")
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
    utils_logger.info("Работа функции calculate_cards завершена без ошибок.")
    return cards


def top_transactions(df: pd.DataFrame, count_tr: int = 5) -> List[Dict[str, str]]:
    """Возвращает топ транзакций по абсолютной сумме платежа. По умолчанию 5"""
    utils_logger.info("Запуск функции top_transaction")

    top_count = df.iloc[df["Сумма платежа"].abs().argsort()[::-1]].head(count_tr)
    top_transaction = []

    utils_logger.info("Фильтрация данных...")
    for transaction, group in top_count.iterrows():
        top_transaction.append(
            {
                "date": group["Дата платежа"],
                "amount": group["Сумма платежа"],
                "category": group["Категория"],
                "description": group["Описание"],
            }
        )
    utils_logger.info("Работа функции top_transactions завершена без ошибок.")
    return top_transaction


def read_json(filename: Path | str) -> Dict[str, Any]:
    """функция читает json файл. Если есть ошибки, то выводит пустой файл"""
    utils_logger.info("Запуск функции tread_json")

    try:
        with open(filename, encoding="utf-8") as f:
            utils_logger.info("Чтение json файла... ")
            data = json.load(f)

        if not isinstance(data, dict):
            utils_logger.error("Некорректный формат JSON файла")
            return {}

        utils_logger.info("Работа функции read_json завершена без ошибок.")
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        utils_logger.error("Файл не найден")
        return {}


def get_currency_rates(user_data: Dict[str, Any], base: str = "RUB") -> list[Any] | dict[Any, Any]:
    """Функция возвращает курсы валют из списка user_currencies относительно base валюты."""
    utils_logger.info("Запуск функции get_currency_rates")

    load_dotenv()
    api_key = os.getenv("API_KEY_CURR")
    api_url = os.getenv("API_URL_CURR")

    if not api_url:
        utils_logger.error("Функция завершена с ошибкой. API_URL не определен!")
        raise ValueError("API_URL не определен!")
    if not api_key:
        utils_logger.error("Функция завершена с ошибкой. API_KEY не определен!")
        raise ValueError("API_KEY не определен")

    currencies = ",".join(user_data["user_currencies"])
    params = {"access_key": api_key, "currencies": currencies, "source": base}
    headers = {"apikey": api_key} if api_key else {}

    try:
        utils_logger.info("Отправка API запроса...")
        response = requests.get(api_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        rates = data.get("quotes", {})
        utils_logger.info(f"Данные валют {currencies} получены")

        currency_rates = []

        utils_logger.info("Фильтрация данных...")
        for key, value in rates.items():
            currency = key[len(base) :]
            if value != 0:
                rate = round(1 / value, 4)
            else:
                rate = 0
            currency_rates.append({"currency": currency, "rate": rate})

        utils_logger.info("Работа функции get_currency_rates завершена без ошибок.")
        return currency_rates

    except requests.RequestException:
        utils_logger.exception("Ошибка при получении курса валют")
        return {}


def get_stock_price(user_data: Dict[str, Any]) -> List[Any] | dict[Any, Any]:
    """Функция возвращает цену акций из списка user_stocks относительно валюты RUB."""
    utils_logger.info("Запуск функции get_stock_price")

    load_dotenv()
    api_key = os.getenv("API_KEY_STOCK")
    api_url = os.getenv("API_URL_STOCK")

    if not api_url:
        utils_logger.error("Функция завершена с ошибкой. API_URL не определен!")
        raise ValueError("API_URL не определен!")
    if not api_key:
        utils_logger.error("Функция завершена с ошибкой. API_KEY не определен!")
        raise ValueError("API_KEY не определен")

    price_stock = []
    stocks = user_data.get("user_stocks", [])

    utils_logger.info("Отправка API запроса и фильтрация данных. Для каждой акции отдельный API запрос")
    for stock in stocks:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": api_key}

        try:
            response = requests.get(api_url, params=params)
            data = response.json()

            quote = data.get("Global Quote", {})
            price_str = quote.get("05. price")

            if price_str is None or price_str.strip() == "":
                utils_logger.info(f"Цена акции {stock} отсутствует")
                price = None
                price_stock.append({"stock": stock, "price": price})
            else:
                utils_logger.info(f"Цена акции {stock} получена")
                price = float(price_str)
                price_stock.append({"stock": stock, "price": price})

        except requests.RequestException:
            utils_logger.exception("Ошибка при получении цены акции")
            continue
    utils_logger.info("Работа функции get_stock_price завершена без ошибок.")
    return price_stock
