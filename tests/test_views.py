import json
from unittest.mock import patch, Mock

from src.views import root_function


@patch("src.views.get_greeting")
@patch("src.views.get_cards_data")
@patch("src.views.get_top_transactions")
@patch("src.views.get_rate")
@patch("src.views.get_stock_prices")
def test_root_function_valid(
    mock_get_stock_prices: Mock,
    mock_get_rate: Mock,
    mock_get_top_transactions: Mock,
    mock_get_cards_data: Mock,
    mock_get_greeting: Mock,
    test_root_function_valid_1: dict,
) -> None:
    """Тестирование главной функции, объединяющая функциональность приложения с валидными значениями"""
    mock_get_greeting.return_value = "Добрый день"
    mock_get_cards_data.return_value = [
        {"last_digits": "4556", "total_spent": 8541.02, "cashback": 85.41},
        {"last_digits": "7197", "total_spent": 3158.03, "cashback": 31.58},
    ]
    mock_get_top_transactions.return_value = [
        {
            "date": "16.01.2020",
            "amount": 3100.0,
            "category": "Пополнения",
            "description": "Внесение наличных через банкомат Тинькофф",
        },
        {"date": "16.01.2020", "amount": 2130.0, "category": "Пополнения", "description": "Перевод с карты"},
        {"date": "15.01.2020", "amount": -2127.32, "category": "Другое", "description": "ГУП ВЦКП ЖХ"},
        {"date": "19.01.2020", "amount": 2100.0, "category": "Пополнения", "description": "Перевод с карты"},
        {"date": "17.01.2020", "amount": -2100.0, "category": "Переводы", "description": "Перевод на карту"},
    ]
    mock_get_rate.return_value = [{"currency": "USD", "rate": 77.25}, {"currency": "EUR", "rate": 91.58}]
    mock_get_stock_prices.return_value = [
        {"stock": "AAPL", "price": 20218.14},
        {"stock": "AMZN", "price": 15418.72},
        {"stock": "GOOGL", "price": 23869.66},
        {"stock": "MSFT", "price": 31041.37},
        {"stock": "TSLA", "price": 32217.86},
    ]

    assert root_function("2020-01-21 12:49:52") == json.dumps(test_root_function_valid_1, indent=4, ensure_ascii=False)
