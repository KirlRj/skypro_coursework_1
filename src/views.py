import json
from datetime import datetime

from src.utils import (calculate_cards, get_currency_rates, get_greeting, get_stock_price, read_excel_by_date,
                       read_json, top_transactions)


def structure_data(in_date: str) -> str:
    """Функция для страницы "Главная" """
    df = read_excel_by_date(r"C:\Users\Kirill\Desktop\Learning\coursework_1\data\operations.xlsx", in_date)
    ud = read_json(r"C:\Users\Kirill\Desktop\Learning\coursework_1\data\user_settings.json")
    data = {
        "greeting": get_greeting(dt=datetime.now()),
        "cards": calculate_cards(df),
        "top_transaction": top_transactions(df),
        "currency_rates": get_currency_rates(ud),
        "stock_prices": get_stock_price(ud),
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=2)
    return json_data
