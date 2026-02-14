import json

from src.services import get_transactions_tel


def test_get_transactions_tel_valid(
    get_transactions_tel_valid: list[dict], get_transactions_tel_valid_result: list[dict]
) -> None:
    """Тестирование функции, фильтрующей транзакции по наличию в описании телефонных номеров с валидными значениями"""
    assert get_transactions_tel(get_transactions_tel_valid) == json.dumps(
        get_transactions_tel_valid_result, ensure_ascii=False
    )


def test_get_transactions_tel_empty() -> None:
    """Тестирование функции, фильтрующей транзакции по наличию в описании телефонных номеров
    с пустым списком транзакций"""
    assert get_transactions_tel([]) == json.dumps([], ensure_ascii=False)


def test_get_transactions_not_tel(get_transactions_not_tel: list[dict]) -> None:
    """Тестирование функции, фильтрующей транзакции по наличию в описании телефонных номеров
    при отсутствии транзакций с номерами"""
    assert get_transactions_tel(get_transactions_not_tel) == json.dumps([], ensure_ascii=False)
