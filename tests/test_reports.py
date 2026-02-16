import pandas as pd

from src.reports import spending_by_weekday


def test_spending_by_weekday_valid(
    spending_by_weekday_valid: pd.DataFrame, spending_by_weekday_valid_result: dict
) -> None:
    """Тестирование функции, возвращающей средние траты в каждый из дней недели за три месяца при валидных значениях"""
    assert (
        spending_by_weekday(spending_by_weekday_valid, "2026-02-16 12:49:52").to_dict()
        == spending_by_weekday_valid_result
    )
    assert (
        spending_by_weekday(spending_by_weekday_valid, "2026-04-01 12:49:52").to_dict()
        == spending_by_weekday_valid_result
    )


def test_spending_by_weekday_empty(spending_by_weekday_valid: pd.DataFrame) -> None:
    """Тестирование функции, возвращающей средние траты в каждый из дней недели за три месяца
    при отсутствии транзакций в заданном периоде"""
    assert (
        spending_by_weekday(spending_by_weekday_valid, "2025-02-16 12:49:52").to_dict() == pd.DataFrame([]).to_dict()
    )
