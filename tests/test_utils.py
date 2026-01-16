import json
from datetime import datetime
from typing import Any

import pandas as pd
import pytest
import requests

from src import utils


@pytest.mark.parametrize(
    "hour,expected",
    [
        (7, "Доброе утро"),
        (13, "Добрый день"),
        (19, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_get_greeting(hour: Any, expected: Any) -> None:
    dt = datetime(2024, 1, 1, hour, 0, 0)
    assert utils.get_greeting(dt) == expected


def test_read_excel_by_date_without_date(mocker: Any) -> None:
    df = pd.DataFrame(
        {
            "Дата операции": ["01.01.2024 10:00:00"],
            "Сумма платежа": [100],
        }
    )

    mocker.patch("pandas.read_excel", return_value=df)

    result = utils.read_excel_by_date("test.xlsx")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_read_excel_by_date_with_filter(mocker: Any) -> None:
    df = pd.DataFrame(
        {
            "Дата операции": [
                "01.01.2024 10:00:00",
                "15.02.2024 12:00:00",
            ],
            "Сумма платежа": [100, 200],
        }
    )

    mocker.patch("pandas.read_excel", return_value=df)

    result = utils.read_excel_by_date(
        "fake.xlsx",
        in_date="2024-01-31 23:59:59",
    )

    assert len(result) == 1


def test_calculate_cards() -> None:
    df = pd.DataFrame(
        {
            "Номер карты": ["1234567812345678", "1234567812345678"],
            "Сумма платежа": [-100, -200],
        }
    )

    result = utils.calculate_cards(df)

    assert result == [
        {
            "last_digits": "5678",
            "total_spent": 300.0,
            "cashback": 3.0,
        }
    ]


def test_top_transactions() -> None:
    df = pd.DataFrame(
        {
            "Дата платежа": ["2024-01-01", "2024-01-02"],
            "Сумма платежа": [-500, -100],
            "Категория": ["Food", "Taxi"],
            "Описание": ["Cafe", "Uber"],
        }
    )

    result = utils.top_transactions(df, count_tr=1)

    assert len(result) == 1
    assert result[0]["amount"] == -500


def test_read_json_ok(tmp_path: Any) -> None:
    file = tmp_path / "data.json"
    file.write_text(json.dumps({"a": 1}), encoding="utf-8")

    result = utils.read_json(file)

    assert result == {"a": 1}


def test_read_json_file_not_found() -> None:
    result = utils.read_json("not_exists.json")
    assert result == {}


def test_read_json_invalid_format(tmp_path: Any) -> None:
    file = tmp_path / "data.json"
    file.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    result = utils.read_json(file)

    assert result == {}


def test_get_currency_rates_success(mocker: Any) -> None:
    mocker.patch.dict(
        "os.environ",
        {
            "API_KEY_CURR": "key",
            "API_URL_CURR": "http://api.test",
        },
    )

    mock_response = mocker.Mock()
    mock_response.json.return_value = {"quotes": {"RUBUSD": 100}}
    mock_response.raise_for_status.return_value = None

    mocker.patch("requests.get", return_value=mock_response)

    result = utils.get_currency_rates(
        {"user_currencies": ["USD"]},
        base="RUB",
    )

    assert result == [{"currency": "USD", "rate": 0.01}]


def test_get_currency_rates_request_error(mocker: Any) -> None:
    mocker.patch.dict(
        "os.environ",
        {
            "API_KEY_CURR": "key",
            "API_URL_CURR": "http://api.test",
        },
    )

    mocker.patch("requests.get", side_effect=requests.RequestException)

    result = utils.get_currency_rates({"user_currencies": ["USD"]})

    assert result == {}


def test_get_stock_price_success(mocker: Any) -> None:
    mocker.patch.dict(
        "os.environ",
        {
            "API_KEY_STOCK": "key",
            "API_URL_STOCK": "http://api.test",
        },
    )

    mock_response = mocker.Mock()
    mock_response.json.return_value = {"Global Quote": {"05. price": "123.45"}}

    mocker.patch("requests.get", return_value=mock_response)

    result = utils.get_stock_price({"user_stocks": ["AAPL"]})

    assert result == [{"stock": "AAPL", "price": 123.45}]


def test_get_stock_price_no_price(mocker: Any) -> None:
    mocker.patch.dict(
        "os.environ",
        {
            "API_KEY_STOCK": "key",
            "API_URL_STOCK": "http://api.test",
        },
    )

    mock_response = mocker.Mock()
    mock_response.json.return_value = {"Global Quote": {}}

    mocker.patch("requests.get", return_value=mock_response)

    result = utils.get_stock_price({"user_stocks": ["AAPL"]})

    assert result == [{"stock": "AAPL", "price": None}]
