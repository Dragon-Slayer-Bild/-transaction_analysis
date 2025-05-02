import json

import pytest

from src.services import transaction_search


@pytest.fixture
def sample_transactions():
    """Фикстура для создания списка транзакций."""
    return [
        {"Описание": "Покупка в магазине ABC", "Сумма": 100},
        {"Описание": "Оплата счета DEF", "Сумма": 50},
        {"Описание": "Перевод в магазин ABC", "Сумма": 25},
        {"Описание": "Что-то другое", "Сумма": 75},
    ]


def test_transaction_search_success(sample_transactions):
    """Тест успешного поиска транзакций."""
    search_string = "ABC"
    expected_json = json.dumps(
        [
            {"Описание": "Покупка в магазине ABC", "Сумма": 100},
            {"Описание": "Перевод в магазин ABC", "Сумма": 25},
        ],
        indent=4,
        ensure_ascii=False,
    )
    result = transaction_search(sample_transactions, search_string)
    assert result == expected_json


def test_transaction_search_no_match(sample_transactions):
    """Тест, когда нет совпадений в поиске."""
    search_string = "XYZ"
    result = transaction_search(sample_transactions, search_string)
    expected_json = json.dumps([], indent=4, ensure_ascii=False)
    assert result == expected_json
