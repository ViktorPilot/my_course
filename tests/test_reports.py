import datetime
from unittest.mock import patch

import pandas as pd

from src.reports import spending_by_weekday


def test_spending_by_weekday_valid_1(spending_by_weekday_valid, spending_by_weekday_valid_result):
    """Тестирование функции, возвращающей средние траты в каждый из дней недели за три месяца при валидных значениях"""
    assert spending_by_weekday(spending_by_weekday_valid,
                               "2026-02-16 12:49:52").to_dict() == spending_by_weekday_valid_result
    assert spending_by_weekday(spending_by_weekday_valid,
                               "2026-04-01 12:49:52").to_dict() == spending_by_weekday_valid_result


def test_spending_by_weekday_empty(spending_by_weekday_valid):
    """Тестирование функции, возвращающей средние траты в каждый из дней недели за три месяца при отсутствии транзакций в заданном периоде"""
    assert spending_by_weekday(spending_by_weekday_valid, "2025-02-16 12:49:52").to_dict() == pd.DataFrame([]).to_dict()


@patch("src.reports.datetime.datetime")
def test_spending_by_weekday_now(mock_datetime, spending_by_weekday_valid, spending_by_weekday_valid_result):
    mock_datetime.now.return_value = datetime.datetime(year=2026, month=2, day=16, hour=13, minute=28,
                                                                second=12)
    mock_datetime.now.return_value.month = 2
    mock_datetime.datetime.strptime.side_effect = ['10.01.2026 13:01:22', '10.01.2026 13:00:04', '10.01.2026 12:59:23',
                                                   '09.01.2026 12:43:34', '09.01.2026 12:42:44', '09.01.2026 12:41:24',
                                                   '08.01.2026 21:29:43', '07.01.2026 14:21:23', '07.01.2026 13:38:08',
                                                   '07.01.2026 15:28:22']
    assert spending_by_weekday(spending_by_weekday_valid,
                               "2026-02-16 12:49:52").to_dict() == spending_by_weekday_valid_result
