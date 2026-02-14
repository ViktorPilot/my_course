import json
import logging
import os
import re
from typing import Any

from src.views import BASE_DIR

logger_services = logging.getLogger("services")
logger_services.setLevel("INFO")
handler = logging.FileHandler(filename=os.path.join(BASE_DIR, "logs/logger_services.log"), mode="w", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(name)s/%(funcName)s:%(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger_services.addHandler(handler)


def get_transactions_tel(all_transactions: list[dict]) -> Any:
    """Функция, фильтрующая транзакции по наличию в описании телефонных номеров"""
    logger_services.info("Начало работы функции..")
    filtred_transactions = [
        transaction
        for transaction in all_transactions
        if re.search(r"\+\d \d{3} \d+-\d+-\d+", transaction.get("Описание", ""))
    ]
    logger_services.info(
        "Список словарей транзакций, содержащий в описании мобильные номера успешно сформирован. "
        "Завершение работы функции."
    )
    return json.dumps(filtred_transactions, ensure_ascii=False)


if __name__ == "__main__":
    dict_transactions_ = [
        {
            "Дата операции": "01.01.2018 20:27:51",
            "Дата платежа": "04.01.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -316.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -316.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Категория": "Красота",
            "MCC": 5977.0,
            "Описание": "OOO Balid",
            "Бонусы (включая кэшбэк)": 6,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 316.0,
        },
        {
            "Дата операции": "01.01.2018 12:49:53",
            "Дата платежа": "01.01.2018",
            "Номер карты": "nan",
            "Статус": "OK",
            "Сумма операции": -3000.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -3000.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Категория": "Переводы",
            "MCC": "nan",
            "Описание": "Я МТС +7 921 11-22-33",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 3000.0,
        },
    ]
    print(get_transactions_tel(dict_transactions_))
