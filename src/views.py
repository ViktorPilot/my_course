import json
import logging
import os.path
from typing import Any

from src.utils import get_cards_data, get_greeting, get_rate, get_stock_prices, get_top_transactions

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if not os.path.exists(os.path.join(BASE_DIR, "logs")):
    os.makedirs(os.path.join(BASE_DIR, "logs"))

logger_views = logging.getLogger("views")
logger_views.setLevel("INFO")
handler = logging.FileHandler(filename=os.path.join(BASE_DIR, "logs/logger_views.log"), mode="w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s/%(funcName)s:%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger_views.addHandler(handler)


def root_function(input_date: str) -> Any:
    """Функция, объединяющая функциональность бэкэнда главной страницы приложения
    и возвращающая json-ответ с данными по транзакциям, курсу валют и акций за месяц на текущую дату"""
    logger_views.info("Начало работы функции..")
    result = {
        "greeting": get_greeting(),
        "cards": get_cards_data(input_date, os.path.join(BASE_DIR, "data/operations.xlsx")),
        "top_transactions": get_top_transactions(input_date, os.path.join(BASE_DIR, "data/operations.xlsx")),
        "currency_rates": get_rate(os.path.join(BASE_DIR, "user_settings.json"), type_currency="RUB"),
        "stock_prices": get_stock_prices(
            os.path.join(BASE_DIR, "user_settings.json"), base_currency="USD", convert_currency="RUB"
        ),
    }
    result_json = json.dumps(result, indent=4, ensure_ascii=False)
    logger_views.info("Результат успешно получен. Завершение работы функции.")
    return result_json


if __name__ == "__main__":
    print(root_function("2020-01-21 12:49:52"))
