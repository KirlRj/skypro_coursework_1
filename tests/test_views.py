import json
from typing import Any

import pandas as pd

from src.views import structure_data


def test_structure_data_success(mocker: Any) -> None:

    test_df = pd.DataFrame(
        {
            "Номер карты": ["1234567812345678"],
            "Сумма платежа": [-100],
            "Дата платежа": ["01.01.2024"],
            "Категория": ["Еда"],
            "Описание": ["Кафе"],
        }
    )

    test_user_data = {
        "user_currencies": ["USD"],
        "user_stocks": ["AAPL"],
    }

    mocker.patch(
        "src.views.read_excel_by_date",
        return_value=test_df,
    )

    mocker.patch(
        "src.views.read_json",
        return_value=test_user_data,
    )

    mocker.patch(
        "src.views.get_greeting",
        return_value="Добрый день",
    )

    mocker.patch(
        "src.views.calculate_cards",
        return_value=[
            {
                "last_digits": "5678",
                "total_spent": 100.0,
                "cashback": 1.0,
            }
        ],
    )

    mocker.patch(
        "src.views.top_transactions",
        return_value=[
            {
                "date": "01.01.2024",
                "amount": -100,
                "category": "Еда",
                "description": "Кафе",
            }
        ],
    )

    mocker.patch(
        "src.views.get_currency_rates",
        return_value=[{"currency": "USD", "rate": 0.01}],
    )

    mocker.patch(
        "src.views.get_stock_price",
        return_value=[{"stock": "AAPL", "price": 123.45}],
    )

    result = structure_data("2024-01-31 23:59:59")

    result_dict = json.loads(result)

    assert result_dict == {
        "greeting": "Добрый день",
        "cards": [
            {
                "last_digits": "5678",
                "total_spent": 100.0,
                "cashback": 1.0,
            }
        ],
        "top_transaction": [
            {
                "date": "01.01.2024",
                "amount": -100,
                "category": "Еда",
                "description": "Кафе",
            }
        ],
        "currency_rates": [{"currency": "USD", "rate": 0.01}],
        "stock_prices": [{"stock": "AAPL", "price": 123.45}],
    }
