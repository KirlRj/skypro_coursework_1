import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils import read_excel_by_date

dir = Path(__file__).resolve().parent.parent
log_path = dir / "log.txt"
reports_logger = logging.getLogger("reports.py")
reports_logger.setLevel(logging.DEBUG)
reports_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
reports_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
reports_handler.setFormatter(reports_formatter)
reports_logger.addHandler(reports_handler)


def save_report(filename: Any) -> Any:

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if filename:
                file_path = filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{func.__name__}_{timestamp}.json"

            if isinstance(result, pd.DataFrame):
                result.to_json(file_path, orient="records", force_ascii=False, indent=2)

            return result

        return wrapper

    return decorator


@save_report(filename=None)
def spending_by_category(transactions: pd.DataFrame, category: str, date: str | None = None) -> pd.DataFrame:
    reports_logger.info("Запуск функции spending_by_category")
    end_date = pd.to_datetime(date, dayfirst=True) if date else pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(months=3)

    df = transactions.copy()
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], errors="coerce", dayfirst=True)
    reports_logger.info("Работа функции get_stock_price завершена без ошибок.")
    return df[(df["Категория"] == category) & (df["Дата платежа"] >= start_date) & (df["Дата платежа"] <= end_date)]


print(
    spending_by_category(
        read_excel_by_date(r"C:\Users\Kirill\Desktop\Learning\coursework_1\data\operations.xlsx"),
        "Супермаркеты",
        "25.12.2020",
    )
)
