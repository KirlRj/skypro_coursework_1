import json
from typing import Any

import pandas as pd
import pytest

from src.services import cashback_categories


def test_cashback_categories_success(mocker: Any) -> None:
    df = pd.DataFrame(
        {
            "Дата платежа": [
                "15.03.2024",
                "20.03.2024",
                "01.04.2024",
            ],
            "Категория": ["Еда", "Транспорт", "Еда"],
            "Кэшбэк": [100, 50, 999],
        }
    )

    mocker.patch(
        "src.services.read_excel_by_date",
        return_value=df,
    )

    result = cashback_categories(
        file_path="fake.xlsx",
        year=2024,
        month=3,
    )

    result_dict = json.loads(result)

    assert result_dict == {
        "Еда": 100.0,
        "Транспорт": 50.0,
    }


def test_cashback_categories_missing_columns(mocker: Any) -> None:
    df = pd.DataFrame(
        {
            "Дата платежа": ["15.03.2024"],
            "Категория": ["Еда"],
            # нет колонки "Кэшбэк"
        }
    )

    mocker.patch(
        "src.services.read_excel_by_date",
        return_value=df,
    )

    with pytest.raises(ValueError) as exc:
        cashback_categories(
            file_path="fake.xlsx",
            year=2024,
            month=3,
        )

    assert "В файле отсутствуют колонки" in str(exc.value)
