import json
from typing import Any

import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category_filtering() -> None:
    df = pd.DataFrame(
        {
            "Дата платежа": [
                "01.01.2024",
                "15.02.2024",
                "01.04.2024",
            ],
            "Категория": ["Еда", "Еда", "Транспорт"],
            "Сумма платежа": [100, 200, 300],
        }
    )

    result = spending_by_category(
        transactions=df,
        category="Еда",
        date="01.03.2024",
    )

    assert len(result) == 2
    assert (result["Категория"] == "Еда").all()


def test_save_report_creates_json_file(tmp_path: Any, monkeypatch: Any) -> None:
    df = pd.DataFrame(
        {
            "Дата платежа": ["01.01.2024"],
            "Категория": ["Еда"],
            "Сумма платежа": [100],
        }
    )

    monkeypatch.chdir(tmp_path)

    fixed_time = pd.Timestamp("2024-03-01 12:00:00")

    class FixedDatetime:
        @classmethod
        def now(cls: Any) -> Any:
            return fixed_time.to_pydatetime()

    monkeypatch.setattr("src.reports.datetime", FixedDatetime)

    spending_by_category(
        transactions=df,
        category="Еда",
        date="01.03.2024",
    )

    files = list(tmp_path.glob("spending_by_category_*.json"))
    assert len(files) == 1

    content = json.loads(files[0].read_text(encoding="utf-8"))
    assert content[0]["Категория"] == "Еда"
