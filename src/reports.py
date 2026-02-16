import datetime
import json
import logging
import os.path
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

from src.utils import get_transactions

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if not os.path.exists(os.path.join(BASE_DIR, "logs")):
    os.makedirs(os.path.join(BASE_DIR, "logs"))

logger_reports = logging.getLogger("reports")
logger_reports.setLevel("INFO")
handler_reports = logging.FileHandler(os.path.join(BASE_DIR, "logs/logger_reports.log"), "w", encoding="utf-8")
formatter_reports = logging.Formatter("%(asctime)s - %(name)s/%(funcName)s:%(levelname)s: %(message)s")
handler_reports.setFormatter(formatter_reports)
logger_reports.addHandler(handler_reports)


def write_to_file(path_to_json: str | None = None) -> Callable:
    """Декоратор, выполняющий запись json-данных в файл по умолчанию или по указанному в аргументе пути"""
    logger_reports.info("Начало работы декоратора..")

    def wrapper(func: Callable) -> Callable:
        @wraps(func)
        def inner(*args: pd.DataFrame | str | None, **kwargs: dict | None) -> Any:
            result = func(*args, **kwargs)
            if not path_to_json:
                with open(os.path.join(BASE_DIR, "data/report.json"), "w", encoding="utf-8") as file:
                    json.dump(result.to_dict(), file, indent=4, ensure_ascii=False)
                    logger_reports.info(
                        f"Данные успешно записаны в файл: {os.path.join(BASE_DIR, "data/report.json")}. "
                        f"Завершение работы декоратора."
                    )
                    return result
            with open(path_to_json, "w", encoding="utf-8") as file:
                json.dump(result.to_dict(), file, indent=4, ensure_ascii=False)
                logger_reports.info(f"Данные успешно записаны в файл: {path_to_json}. Завершение работы декоратора.")
                return result

        return inner

    return wrapper


@write_to_file()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Функция, возвращающая средние траты в каждый из дней недели за последние три месяца (от переданной даты)"""
    if not date:
        date_obj = datetime.datetime.now()
    else:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    if date_obj.month > 3:
        start_date = datetime.datetime(
            date_obj.year, date_obj.month - 3, date_obj.day, date_obj.hour, date_obj.minute, date_obj.second
        )
    else:
        start_date = datetime.datetime(date_obj.year - 1, date_obj.month + 9, date_obj.day)
    filtred_transactions_date = [
        transaction
        for transaction in transactions.to_dict(orient="records")
        if start_date
        <= datetime.datetime.strptime(transaction.get("Дата операции", ""), "%d.%m.%Y %H:%M:%S")
        <= date_obj
        and transaction.get("Сумма операции", 0) < 0
    ]
    for transaction in filtred_transactions_date:
        transaction["День недели"] = datetime.datetime.strftime(
            datetime.datetime.strptime(transaction.get("Дата операции", ""), "%d.%m.%Y %H:%M:%S"), "%A"
        )
        transaction["Номер дня недели"] = datetime.datetime.strftime(
            datetime.datetime.strptime(transaction.get("Дата операции", ""), "%d.%m.%Y %H:%M:%S"), "%w"
        )
    transactions_df = pd.DataFrame(filtred_transactions_date)
    try:
        filtred_transactions_df = transactions_df[["Сумма операции", "День недели", "Номер дня недели"]].loc[
            (transactions_df["Статус"] == "OK")
            & (transactions_df["Дата операции"].notnull())
            & (transactions_df["Сумма операции"].notnull())
        ]
        transactions_mean = abs(round(filtred_transactions_df.groupby(["Номер дня недели", "День недели"]).mean(), 2))
        transactions_mean["Средние траты в каждый из дней недели за последние три месяца"] = transactions_mean[
            "Сумма операции"
        ]
        transactions_mean.reset_index("Номер дня недели", inplace=True)
        transactions_mean.drop(["Номер дня недели", "Сумма операции"], axis=1, inplace=True)
    except KeyError:
        print("В заданном периоде транзакции не проводились.")
        transactions_mean = pd.DataFrame([])
    return transactions_mean


if __name__ == "__main__":
    print(spending_by_weekday(get_transactions(os.path.join(BASE_DIR, "data/operations.xlsx")), "2020-02-16 12:49:52"))
