import datetime
import json
import logging
import os
from os import getenv

import pandas as pd
import requests
from dotenv import load_dotenv

logger_utils = logging.getLogger("utils")


def get_transactions(path_to_xlsx: str) -> pd.DataFrame:
    """Функция, преобразующая файл транзакций из формата xlsx в объект dataframe"""
    logger_utils.info("Начало работы функции..")
    if os.path.exists(path_to_xlsx):
        df_transactions = pd.read_excel(path_to_xlsx)
    else:
        logger_utils.error(f"Файл {os.path.basename(path_to_xlsx)} не найден. Проверьте путь к файлу.")
        raise FileNotFoundError(f"Файл {os.path.basename(path_to_xlsx)} не найден. Проверьте путь к файлу.")
    logger_utils.info(
        f"Файл {os.path.basename(path_to_xlsx)} успешно преобразован в объект dataframe. Завершение работы функции."
    )
    return df_transactions


def get_greeting() -> str:
    """Функция, возвращающая приветствие в зависимости от времени суток"""
    logger_utils.info("Начало работы функции..")
    current_time = datetime.datetime.now().hour
    if 0 <= current_time < 6:
        greeting = "Доброй ночи"
    elif 6 <= current_time < 12:
        greeting = "Доброе утро"
    elif 12 <= current_time < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"
    logger_utils.info("Приветствие успешно сформировано. Завершение работы функции.")
    return greeting


def get_filtred_dict(input_date: str, path_to_xlsx: str) -> list[dict]:
    """Функция, возвращающая отфильтрованный по дате и статусу список словарей транзакций"""
    logger_utils.info("Начало работы функции..")
    try:
        input_date_obj = datetime.datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
        data_start_month = input_date_obj.replace(day=1, hour=00, minute=00, second=00)
        dict_transactions = get_transactions(path_to_xlsx).to_dict(orient="records")
        list_transactions_date = [
            transactions
            for transactions in dict_transactions
            if data_start_month
               <= datetime.datetime.strptime(transactions.get("Дата операции", ""), "%d.%m.%Y %H:%M:%S")
               <= input_date_obj
               and transactions.get("Статус") == "OK"
        ]
        logger_utils.info(
            "Список словарей транзакций успешно отфильтрован по дате и статусу. Завершение работы функции."
        )
        return list_transactions_date
    except Exception as e:
        print(f"При выполнении операции произошла ошибка: {e}.")
        logger_utils.error(f"При выполнении операции произошла ошибка: {e}. Завершение работы функции.")
        return [{}]


def get_cards_data(input_date: str, path_to_xlsx: str) -> list[dict]:
    """Функция, возвращающая список словарей крайних цифр, сумм расходов и сумм кэшбека по каждой карте"""
    logger_utils.info("Начало работы функции..")
    try:
        df_transactions = pd.DataFrame(get_filtred_dict(input_date, path_to_xlsx))
        not_null_df_transactions = df_transactions[["Номер карты", "Сумма платежа", "Дата операции"]].loc[
            (df_transactions["Номер карты"].notnull())
            & (df_transactions["Сумма платежа"].notnull())
            & (df_transactions["Дата операции"].notnull() & (df_transactions["Сумма платежа"] < 0))
            ]
        group_df_transactions = not_null_df_transactions.groupby("Номер карты")["Сумма платежа"].sum()
        dict_transactions_filtred = group_df_transactions.to_dict()
        result = [
            {"last_digits": k[1:], "total_spent": round(abs(v), 2), "cashback": round(abs(v * 0.01), 2)}
            for k, v in dict_transactions_filtred.items()
        ]
        logger_utils.info("Список словарей данных по каждой карте успешно сформирован. Завершение работы функции.")
        return result
    except KeyError:
        logger_utils.error("В выбранном периоде транзакции не производились. Завершение работы функции.")
        return [{}]
    except Exception as e:
        print(f"При выполнении операции произошла ошибка: {e}.")
        logger_utils.error(f"При выполнении операции произошла ошибка: {e}. Завершение работы функции.")
        return [{}]


def get_top_transactions(input_date: str, path_to_xlsx: str) -> list[dict]:
    """Функция, возвращающая топ пять транзакций по сумме платежа"""
    logger_utils.info("Начало работы функции..")
    list_transactions = get_filtred_dict(input_date, path_to_xlsx)
    if list_transactions:
        df_transactions = pd.DataFrame(list_transactions)
        df_transactions_not_nan = df_transactions[["Дата платежа", "Сумма платежа", "Категория", "Описание"]].loc[
            (df_transactions["Дата платежа"].notnull()) & (df_transactions["Сумма платежа"].notnull())
            ]
        dict_transactions_not_null = df_transactions_not_nan.to_dict(orient="records")
        if len(dict_transactions_not_null) >= 5:
            top_dict_transactions = sorted(
                dict_transactions_not_null, key=lambda x: abs(x.get("Сумма платежа", "")), reverse=True
            )[:5]
        else:
            logger_utils.info("В выбранном периоде произведено менее 5 транзакций.")
            top_dict_transactions = sorted(
                dict_transactions_not_null, key=lambda x: abs(x.get("Сумма платежа", "")), reverse=True
            )
        result = [
            {
                "date": transaction.get("Дата платежа", ""),
                "amount": transaction.get("Сумма платежа", ""),
                "category": transaction.get("Категория", ""),
                "description": transaction.get("Описание", ""),
            }
            for transaction in top_dict_transactions
        ]
    else:
        logger_utils.info("В выбранном периоде транзакции не производились.")
        result = [{}]
    logger_utils.info("Результат 'топ 5 транзакций' успешно сформирован. Завершение работы функции.")
    return result


def get_rate(path_to_json: str, type_currency: str) -> list[dict]:
    """Получение списка актуального курса для заданных валют"""
    logger_utils.info("Начало работы функции..")
    if os.path.exists(path_to_json):
        with open(path_to_json, "r", encoding="utf-8") as file:
            dict_of_rate = json.load(file)
    else:
        logger_utils.error(f"Файл {os.path.basename(path_to_json)} не найден. Проверьте путь к файлу.")
        raise FileNotFoundError(f"Файл {os.path.basename(path_to_json)} не найден. Проверьте путь к файлу.")

    list_response_currency = []
    for symbol in dict_of_rate["user_currencies"]:
        response = requests.get(f"https://currencyrateapi.com/api/latest?base={symbol}&codes={type_currency}")
        if response.status_code == 200:
            response_currency = response.json()
            list_response_currency.append(
                {"currency": symbol, "rate": round(float(response_currency.get("rates", {}).get("rub", "")), 2)}
            )
        else:
            print(f"Ошибка при запросе на сервер: {response.status_code}")
            logger_utils.error(f"Ошибка при запросе на сервер: {response.status_code}")
            continue
    logger_utils.info("Актуальный курс заданных валют успешно получен. Завершение работы функции.")
    return list_response_currency


def get_stock_prices(path_to_json: str, base_currency: str, convert_currency: str) -> list[dict]:
    """Получение списка актуального курса акций S&P500"""
    logger_utils.info("Начало работы функции..")
    load_dotenv()
    apikey = getenv("APIKEY_FOR_FINANCIALMODELINGPREP_COM")
    if os.path.exists(path_to_json):
        with open(path_to_json, "r", encoding="utf-8") as file:
            dict_of_prices = json.load(file)
    else:
        logger_utils.error(f"Файл {os.path.basename(path_to_json)} не найден. Проверьте путь к файлу.")
        raise FileNotFoundError(f"Файл {os.path.basename(path_to_json)} не найден. Проверьте путь к файлу.")
    response_rate = (
        requests.get(f"https://currencyrateapi.com/api/latest?base={base_currency}&codes={convert_currency}")
        .json()
        .get("rates", {})
        .get("rub", "")
    )
    response_rate_float = float(response_rate)
    list_response_price = []
    for symbol in dict_of_prices["user_stocks"]:
        response_price = requests.get(
            f"https://financialmodelingprep.com/stable/quote-short?symbol={symbol}&apikey={apikey}"
        )
        if response_price.status_code == 200:
            response_price_str = response_price.json()
            for i in response_price_str:
                list_response_price.append(
                    {"stock": symbol, "price": round(i.get("price", "") * response_rate_float, 2)}
                )
        else:
            print(f"Ошибка при запросе на сервер: {response_price.status_code}")
            logger_utils.error(f"Ошибка при запросе на сервер: {response_price.status_code}")
            continue
    logger_utils.info("Актуальный курс акций S&P500 успешно получен. Завершение работы функции.")
    return list_response_price


if __name__ == "__main__":
    # print(get_greeting())
    # print(get_cards_data("2020-05-02 10:50:03", "../data/operations.xlsx"))
    # print(get_top_transactions("2020-05-02 10:50:03", "../data/operations.xlsx"))
    # print(get_rate("../user_settings.json", type_currency="RUB"))
    print(get_stock_prices("../user_settings.json", base_currency="USD", convert_currency="RUB"))
