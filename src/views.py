import json

from src.utils import get_greeting, get_cards_data, get_top_transactions, get_rate, get_stock_prices


def root_function(input_date):
    """Функция, объединяющая функциональность бэкэнда главной страницы приложения
    и возвращающая json-ответ с данными по транзакциям, курсу валют и акций за месяц на текущую дату"""
    result = {
        "greeting": get_greeting(),
        "cards": get_cards_data(input_date),
        "top_transactions": get_top_transactions(input_date),
        "currency_rates": get_rate(),
        "stock_prices": get_stock_prices(),
    }
    return json.dumps(result, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # input_date_ = input("Введите дату в формате '2020-03-15 10:50:03':\n")
    # root_function(input_date_)
    print(root_function("2020-03-15 10:50:03"))
