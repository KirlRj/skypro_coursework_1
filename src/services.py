import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from src.utils import read_excel_by_date

dir = Path(__file__).resolve().parent.parent
log_path = dir / "log.txt"
services_logger = logging.getLogger("services.py")
services_logger.setLevel(logging.DEBUG)
services_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
services_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
services_handler.setFormatter(services_formatter)
services_logger.addHandler(services_handler)


def cashback_categories(file_path: str, year: int, month: int) -> str:
    """Функция определяющая категории повышенного кэшбэка"""

    services_logger.info("Запуск функции cashback_categories")

    data_file = read_excel_by_date(file_path)

    r_columns = {"Дата платежа", "Кэшбэк", "Категория"}
    if not r_columns.issubset(data_file.columns):
        missing = r_columns - set(data_file.columns)
        services_logger.error(f"В файле отсутствуют колонки: {missing}")
        raise ValueError(f"В файле отсутствуют колонки: {missing}")

    data_file["Дата платежа"] = pd.to_datetime(data_file["Дата платежа"].astype(str), errors="coerce", dayfirst=True)
    filtered_data_file = data_file[
        (data_file["Дата платежа"].dt.year == year) & (data_file["Дата платежа"].dt.month == month)
    ]

    cashback_by_category: Dict[str, float] = {}

    services_logger.info("Формирование данных по категориям кэшбэка")
    for key, value in filtered_data_file.iterrows():
        category = value.get("Категория", "Без категории")
        cashback = value.get("Кэшбэк")
        if pd.notna(cashback):
            cashback_by_category[category] = cashback_by_category.get(category, 0) + float(cashback)

    services_logger.info("Формирование json файла. Функция завершена без ошибок")
    return json.dumps(cashback_by_category, ensure_ascii=False, indent=2)


print(cashback_categories(r"C:\Users\Kirill\Desktop\Learning\coursework_1\data\operations.xlsx", 2021, 11))
