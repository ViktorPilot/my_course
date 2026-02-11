import json
import logging
import os.path
from typing import Any

from src.utils import get_cards_data, get_greeting, get_rate, get_stock_prices, get_top_transactions

if not os.path.exists("../logs"):
    os.makedirs("../logs")
logging.basicConfig(
    filename="../logs/logger_views.log",
    filemode="w",
    format="%(asctime)s - %(name)s/%(funcName)s:%(levelname)s: %(message)s",
    level="INFO",
    encoding="utf-8",
)
logger_views = logging.getLogger("views")


def root_function(input_date: str) -> Any:
    """Функция, объединяющая функциональность бэкэнда главной страницы приложения
    и возвращающая json-ответ с данными по транзакциям, курсу валют и акций за месяц на текущую дату"""
    logger_views.info("Начало работы функции..")
    result = {
        "greeting": get_greeting(),
        "cards": get_cards_data(input_date),
        "top_transactions": get_top_transactions(input_date),
        "currency_rates": get_rate("../user_settings.json", type_currency="RUB"),
        "stock_prices": get_stock_prices("../user_settings.json", base_currency="USD", convert_currency="RUB"),
    }
    logger_views.info("Результат успешно получен. Завершение работы функции.")
    return json.dumps(result, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # input_date_ = input("Введите дату в формате '2020-03-15 10:50:03':\n")
    # root_function(input_date_)
    print(root_function("2020-01-21 12:49:52"))
