import os
import datetime

import pandas as pd


def get_transactions():
    """Функция, преобразующая файл транзакций из формата xlsx в объект dataframe"""
    if os.path.exists("../data/operations.xlsx"):
        df_transactions = pd.read_excel("../data/operations.xlsx")
    else:
        raise FileNotFoundError(f"Файл не существует. Проверьте путь к файлу.")
    return df_transactions


def get_greeting():
    """Функция, возвращающая приветствие в зависимости от времени суток"""
    current_time = datetime.datetime.now().hour
    if 0 <= current_time < 6:
        greeting = "Доброй ночи"
    elif 6 <= current_time < 12:
        greeting = "Доброе утро"
    elif 12 <= current_time < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"
    return greeting


def get_cards_data(input_date):
    """Функция, преобразующая dataframe транзакций в список словарей сводных данных по каждой карте"""
    input_date_obj = datetime.datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
    if datetime.datetime.strptime("01.01.2018 12:49:53",
                                  "%d.%m.%Y %H:%M:%S") <= input_date_obj < datetime.datetime.strptime(
        "31.12.2021 16:44:00", "%d.%m.%Y %H:%M:%S"):
        data_start_month = input_date_obj.replace(day=1, hour=00, minute=00, second=00)

        dict_transactions = get_transactions().to_dict(orient="records")
        dict_transactions_date = [transactions for transactions in dict_transactions if
                                  data_start_month <= datetime.datetime.strptime(transactions.get("Дата операции", ""),
                                                                                 "%d.%m.%Y %H:%M:%S") <= input_date_obj and transactions.get(
                                      "Статус") == "OK"]
        df_transactions = pd.DataFrame(dict_transactions_date)
        not_null_df_transactions = df_transactions[["Номер карты", "Сумма операции", "Дата операции"]].loc[
            (df_transactions["Номер карты"].notnull()) & (df_transactions["Сумма операции"].notnull()) & (
                    df_transactions["Дата операции"].notnull() & (df_transactions["Сумма операции"] < 0))]
        group_df_transactions = not_null_df_transactions.groupby("Номер карты")["Сумма операции"].sum()
        dict_transactions_filtred = group_df_transactions.to_dict()
        result = [{"last_digits": k[1:], "total_spent": abs(v), "cashback": abs(v * 0.01)} for k, v in
                  dict_transactions_filtred.items()]
        return result
    else:
        return [{}]


if __name__ == "__main__":
    get_greeting()
    get_cards_data("2020-05-29 10:50:03")
