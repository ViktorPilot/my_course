import pandas as pd

from src.reports import spending_by_weekday
from src.services import get_transactions_tel
from src.utils import get_transactions
from src.views import root_function

if __name__ == "__main__":
    input_date_1 = input(
        "Введите дату на которую необходимо получить данные по транзакциям"
        " за указанный месяц в формате '2020-03-15 10:50:03':\n"
    )
    input_date_2 = input(
        "Введите дату на которую необходимо получить средние траты в каждый из дней недели "
        "за последние три месяца в формате '2020-03-15 10:50:03':\n"
    )
    path_to_xlsx = "data/operations.xlsx"
    dict_transactions_ = pd.read_excel(path_to_xlsx).to_dict(orient="records")
    print(root_function(input_date_1))
    print(get_transactions_tel(dict_transactions_))
    print(spending_by_weekday(get_transactions(path_to_xlsx), input_date_2))
