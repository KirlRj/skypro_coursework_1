from src.reports import spending_by_category
from src.services import cashback_categories
from src.utils import read_excel_by_date
from src.views import structure_data

if __name__ == "__main__":
    # Запуск страницы "Главная"
    print(structure_data("2020-01-10 20:15:10"))

    # Запуск сервиса определения повышенного кэшбэка
    print(cashback_categories(r"C:\Users\Kirill\Desktop\Learning\coursework_1\data\operations.xlsx", 2021, 11))

    # Запуск отчета "Траты по категории"
    print(
        spending_by_category(
            read_excel_by_date(r"C:\Users\Kirill\Desktop\Learning\coursework_1\data\operations.xlsx"),
            "Супермаркеты",
            "25.12.2020",
        )
    )
