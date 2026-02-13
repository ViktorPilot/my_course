import datetime
import os.path
from unittest.mock import patch, Mock
import pytest
from src.utils import (
    get_greeting,
    get_transactions,
    get_filtred_dict,
    get_cards_data,
    get_top_transactions,
    get_rate,
    get_stock_prices,
)
from src.views import BASE_DIR


def test_get_transactions_valid() -> None:
    """Тестирование функции, преобразующей файл транзакций из формата xlsx в объект dataframe с валидными значениями"""
    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = {"Дата": "2020-05-01 10:50:03", "Описание": "Тинькофф", "Кэшбэк": 1120}
        assert get_transactions(os.path.join(BASE_DIR, "data/operations.xlsx")) == {
            "Дата": "2020-05-01 10:50:03",
            "Описание": "Тинькофф",
            "Кэшбэк": 1120,
        }


def test_get_transactions_not_valid_path() -> None:
    """Тестирование функции, преобразующей файл транзакций из формата xlsx
    в объект dataframe при отсутствии файла транзакций в указанном пути"""
    with pytest.raises(FileNotFoundError):
        get_transactions("../data/oper.xlsx")


def test_get_greeting() -> None:
    """Тестирование функции, возвращающей приветствие пользователю при разном времени суток"""
    with patch("src.utils.datetime") as mock_greeting:
        mock_greeting.datetime.now.return_value = datetime.datetime(
            year=2025, month=2, day=4, hour=5, minute=50, second=43
        )
        assert get_greeting() == "Доброй ночи"
        mock_greeting.datetime.now.return_value = datetime.datetime(
            year=2025, month=2, day=4, hour=7, minute=50, second=43
        )
        assert get_greeting() == "Доброе утро"
        mock_greeting.datetime.now.return_value = datetime.datetime(
            year=2025, month=2, day=4, hour=14, minute=56, second=43
        )
        assert get_greeting() == "Добрый день"
        mock_greeting.datetime.now.return_value = datetime.datetime(
            year=2025, month=2, day=4, hour=21, minute=50, second=43
        )
        assert get_greeting() == "Добрый вечер"


@patch("src.utils.get_transactions")
def test_get_filtred_dict_valid(mock_get_transactions: Mock, get_filtred_dict_valid: list[dict]) -> None:
    """"Тестирование функции, возвращающей отфильтрованный по дате и статусу список словарей
        транзакций при валидных значениях"""
    mock_get_transactions.return_value.to_dict.return_value = get_filtred_dict_valid
    assert get_filtred_dict("2025-02-04 21:50:03", os.path.join(BASE_DIR, "data/operations.xlsx")) == [
        {"Дата операции": "04.02.2025 21:00:00", "Статус": "OK", "Банк": "Тинькофф"},
        {"Дата операции": "03.02.2025 12:00:00", "Статус": "OK", "Банк": "Тинькофф"},
    ]


@patch("src.utils.get_transactions")
def test_get_filtred_dict_not_date(mock_get_transactions: Mock, get_filtred_dict_valid: list[dict]) -> None:
    """Тестирование функции, возвращающей отфильтрованный по дате и статусу список словарей
         транзакций при отсутствии операций в заданном периоде"""
    mock_get_transactions.return_value.to_dict.return_value = get_filtred_dict_valid
    assert get_filtred_dict("2025-02-01 21:50:03", os.path.join(BASE_DIR, "data/operations.xlsx")) == []


def test_get_filtred_dict_error() -> None:
    """Тестирование функции, возвращающей отфильтрованный по дате и статусу список словарей
        транзакций при ошибках в программе"""
    assert get_filtred_dict("2025/02/01 21:50:03", os.path.join(BASE_DIR, "data/operations.xlsx")) == [{}]


@patch("src.utils.get_filtred_dict")
def test_get_cards_data_valid(mock_get_cards_data, get_cards_data_valid):
    mock_get_cards_data.return_value = get_cards_data_valid
    assert get_cards_data("2025-02-04 21:50:03", os.path.join(BASE_DIR, "data/operations.xlsx")) == [
        {"last_digits": "9998", "total_spent": 200, "cashback": 2.0}
    ]


@pytest.mark.parametrize(
    "date, adress, result",
    [
        ("2021-01-01 04:50:03", os.path.join(BASE_DIR, "data/operations.xlsx"), [{}]),
        ("2021/01/21 04:50:03", os.path.join(BASE_DIR, "data/operations.xlsx"), [{}]),
        ("2021-01-21 04:50:03", "../data/operat.xlsx", [{}]),
    ],
)
def test_get_cards_data_not_transaction(date, adress, result):
    assert get_cards_data(date, adress) == result


@patch("src.utils.get_filtred_dict")
def test_get_top_transactions_valid(
    mock_get_top_transactions, get_top_transactions_valid, get_top_transactions_valid_result
):
    mock_get_top_transactions.return_value = get_top_transactions_valid
    assert (
        get_top_transactions("2025-02-05 21:50:03", os.path.join(BASE_DIR, "data/operations.xlsx"))
        == get_top_transactions_valid_result
    )


@patch("src.utils.get_filtred_dict")
def test_get_top_transactions_one(mock_get_top_transactions):
    mock_get_top_transactions.return_value = [
        {
            "Дата платежа": "05.02.2025 12:01:00",
            "Категория": "OK",
            "Описание": "Тинькофф",
            "Номер карты": "*9998",
            "Сумма платежа": -112,
        }
    ]
    assert get_top_transactions("2025-02-05 21:50:03", os.path.join(BASE_DIR, "data/operations.xlsx")) == [
        {"date": "05.02.2025 12:01:00", "amount": -112, "category": "OK", "description": "Тинькофф"}
    ]


@patch("src.utils.get_filtred_dict")
def test_get_top_transactions_empty(mock_get_top_transactions):
    mock_get_top_transactions.return_value = []
    assert get_top_transactions("2025-02-05 21:50:03", os.path.join(BASE_DIR, "data/operations.xlsx")) == [{}]


@patch("json.load")
@patch("requests.get")
def test_get_rate_valid(mock_requests, mock_json_load, currency_and_stock, get_rate_valid):
    mock_json_load.return_value = currency_and_stock
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.side_effect = get_rate_valid
    assert get_rate(os.path.join(BASE_DIR, "user_settings.json"), type_currency="RUB") == [
        {"currency": "USD", "rate": 77.46},
        {"currency": "EUR", "rate": 92.03},
    ]


@patch("json.load")
@patch("requests.get")
def test_get_rate_sc_400(mock_requests, mock_json_load, currency_and_stock, get_rate_valid):
    mock_json_load.return_value = currency_and_stock
    mock_requests.return_value.status_code = 400
    mock_requests.return_value.json.side_effect = get_rate_valid
    assert get_rate(os.path.join(BASE_DIR, "user_settings.json"), type_currency="RUB") == []


def test_get_rate_not_valid_path():
    with pytest.raises(FileNotFoundError):
        get_rate("src/log.json", type_currency="RUB")


@patch("json.load")
@patch("requests.get")
def test_get_stock_prices_valid(mock_requests_get_1, mock_json_load, currency_and_stock):
    mock_json_load.return_value = currency_and_stock
    mock_requests_get_1.return_value.json.side_effect = [
        {
            "success": True,
            "base": "usd",
            "date": "2026-02-11",
            "rates": {"rub": "77.505285388243220481"},
            "last_update_unix": "1770925203",
        },
        [{"symbol": "AAPL", "price": 260.5345, "change": -14.9655, "volume": 34506985}],
        [{"symbol": "AMZN", "price": 199.4, "change": -4.68, "volume": 50936702}],
    ]
    mock_requests_get_1.return_value.status_code = 200
    assert get_stock_prices(os.path.join(BASE_DIR, "user_settings.json"), "USD", "RUB") == [
        {"stock": "AAPL", "price": 20192.8},
        {"stock": "AMZN", "price": 15454.55},
    ]


@patch("json.load")
@patch("requests.get")
def test_get_stock_prices_empty(mock_requests_get_1, mock_json_load, currency_and_not_stock):
    mock_json_load.return_value = currency_and_not_stock
    mock_requests_get_1.return_value.json.side_effect = [
        {
            "success": True,
            "base": "usd",
            "date": "2026-02-11",
            "rates": {"rub": "77.505285388243220481"},
            "last_update_unix": "1770925203",
        },
        [],
    ]
    mock_requests_get_1.return_value.status_code = 200
    assert get_stock_prices(os.path.join(BASE_DIR, "user_settings.json"), "USD", "RUB") == []


@patch("json.load")
@patch("requests.get")
def test_get_stock_prices_sc_400(mock_requests_get_1, mock_json_load, currency_and_stock):
    mock_json_load.return_value = currency_and_stock
    mock_requests_get_1.return_value.json.side_effect = [
        {
            "success": True,
            "base": "usd",
            "date": "2026-02-11",
            "rates": {"rub": "77.505285388243220481"},
            "last_update_unix": "1770925203",
        },
        [{"symbol": "AAPL", "price": 260.5345, "change": -14.9655, "volume": 34506985}],
        [{"symbol": "AMZN", "price": 199.4, "change": -4.68, "volume": 50936702}],
    ]
    mock_requests_get_1.return_value.status_code = 400
    assert get_stock_prices(os.path.join(BASE_DIR, "user_settings.json"), "USD", "RUB") == []


def test_get_stock_prices_not_valid_path():
    with pytest.raises(FileNotFoundError):
        get_stock_prices("data/user_setting.json", "USD", "RUB")
