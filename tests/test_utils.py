import datetime
import os
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.utils import (
    card_list,
    currency_convert,
    currency_list,
    file_reader,
    filter_transactions_in_data,
    greeting,
    stock_price,
    top_transactions,
)


@pytest.fixture
def transactions_list_test():

    transactions = [
        {
            "Дата операции": "31.01.2023 15:00:41",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7199",
            "Сумма операции": 1025.0,
            "Сумма платежа": 1025.0,
            "Валюта платежа": "RUB",
            "Описание": "Оплата денег",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 20,
        },
        {
            "Дата операции": "04.01.2018 15:00:41",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7199",
            "Сумма операции": -25.0,
            "Сумма платежа": -25.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 20,
        },
        {
            "Дата операции": "04.01.2018 14:05:08",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -1065.9,
            "Сумма платежа": -1065.9,
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 21,
        },
        {
            "Дата операции": "03.01.2018 15:03:35",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -73.06,
            "Сумма платежа": -73.06,
            "Валюта платежа": "USD",
            "Описание": "Перевод денег",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 1,
        },
        {
            "Дата операции": "31.01.2023 14:55:21",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -21.0,
            "Сумма платежа": -21.0,
            "Валюта платежа": "USD",
            "Описание": "Оплата за товар",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 0,
        },
        {
            "Дата операции": "31.01.2023 20:27:51",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -316.0,
            "Сумма платежа": -316.0,
            "Описание": "Перевод денег",
            "Кэшбэк": "nan",
            "Валюта платежа": "RUB",
            "Бонусы (включая кэшбэк)": 6,
        },
        {
            "Дата операции": "31.01.2023 12:49:53",
            "Статус": "Failed",
            "Категория": "Каршеринг",
            "Номер карты": "nan",
            "Сумма операции": -3000.0,
            "Сумма платежа": -3000.0,
            "Описание": "Перевод денег",
            "Кэшбэк": "nan",
            "Валюта платежа": "RUB",
            "Бонусы (включая кэшбэк)": 0,
        },
    ]
    return transactions


@pytest.fixture
def mock_xlsx_transactions_file(tmp_path):
    filename = "transactions_test.xlsx"
    file_path = tmp_path / filename
    data = [
        {
            "Дата операции": "04.01.2018 15:00:41",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7199",
            "Сумма операции": 1025.0,
            "Сумма платежа": 1025.0,
            "Описание": "Оплата денег",
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 20,
        },
        {
            "Дата операции": "04.01.2018 15:00:41",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7199",
            "Сумма операции": -25.0,
            "Сумма платежа": -25.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 20,
        },
        {
            "Дата операции": "04.01.2018 14:05:08",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -1065.9,
            "Сумма платежа": -1065.9,
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 21,
        },
        {
            "Дата операции": "03.01.2018 15:03:35",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -73.06,
            "Сумма платежа": -73.06,
            "Валюта платежа": "RUB",
            "Описание": "Перевод денег",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 1,
        },
        {
            "Дата операции": "31.01.2023 14:55:21",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -21.0,
            "Сумма платежа": -21.0,
            "Описание": "Оплата за товар",
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 0,
        },
        {
            "Дата операции": "31.01.2023 20:27:51",
            "Статус": "OK",
            "Категория": "Каршеринг",
            "Номер карты": "*7197",
            "Сумма операции": -316.0,
            "Сумма платежа": -316.0,
            "Описание": "Перевод денег",
            "Валюта платежа": "RUB",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 6,
        },
        {
            "Дата операции": "31.01.2023 12:49:53",
            "Статус": "Failed",
            "Категория": "Каршеринг",
            "Номер карты": "nan",
            "Сумма операции": -3000.0,
            "Сумма платежа": -3000.0,
            "Валюта платежа": "USD",
            "Описание": "Перевод денег",
            "Кэшбэк": "nan",
            "Бонусы (включая кэшбэк)": 0,
        },
    ]
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return str(file_path)


@patch("requests.get")
def test_stock_price_success(mock_get):
    '''Успешный тест получения цен на акции'''

    mock_json_result = {"p": 156.3}

    mock_json = Mock(return_value=mock_json_result)
    mock_get.return_value.json = mock_json
    mock_get.return_value.status_code = 200

    # Вызываем функцию currency_convert
    result = stock_price()
    expected = [
        {"price": 156.3, "stock": "AAPL"},
        {"price": 156.3, "stock": "GOOG"},
        {"price": 156.3, "stock": "TSLA"},
    ]
    assert result == expected


@patch("requests.get")
def test_stock_price_error(mock_get):
    '''Неуспешный тест получения цен на акции'''

    mock_json_result = {"ошибка авторизации"}

    mock_json = Mock(return_value=mock_json_result)
    mock_get.return_value.json = mock_json
    mock_get.return_value.status_code = 401

    # Вызываем функцию currency_convert
    result = stock_price()
    expected = []
    assert result == expected


def test_stock_price_file_not_find():
    '''Тест файл настроек не найден'''
    result = stock_price(filename="HEHEHE", dirname="data")
    assert result == []


def test_file_reader_success(mock_xlsx_transactions_file):
    """Тест успешного чтения файла и извлечения данных."""
    transactions = file_reader(
        filename=os.path.basename(mock_xlsx_transactions_file), dirname=os.path.dirname(mock_xlsx_transactions_file)
    )
    assert transactions[0]["Категория"] == "Каршеринг"
    assert transactions[0]["Сумма операции"] == 1025.0


def test_file_reader_error(tmp_path):
    """Тест файл не найден."""
    result = file_reader(filename="ololol.csv", dirname=str(tmp_path))
    assert result == []


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (0, "Доброй ночи!"),
        (5, "Доброй ночи!"),
        (6, "Доброе утро!"),
        (11, "Доброе утро!"),
        (12, "Добрый день!"),
        (17, "Добрый день!"),
        (18, "Добрый вечер!"),
        (23, "Добрый вечер!"),
    ],
)
def test_greeting(hour, expected_greeting):
    """Тест успешный функции greeting."""
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, hour, 0, 0)
        result = greeting()
        assert result == expected_greeting


def test_greeting_morning_boundary():
    '''Тест успешный на проверуку пограничного значения'''
    with patch("src.utils.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = datetime.datetime(2023, 1, 1, 6, 0, 0)
        result = greeting()
        assert result == "Доброе утро!"


def test_filter_transactions_valid_date(transactions_list_test):
    """Тест фильтрации транзакций с корректной датой."""
    filter_date_str = "31.01.2023 00:00:00"
    filtered = filter_transactions_in_data(transactions_list_test, filter_date_str)
    assert len(filtered) == 4
    assert all(
        datetime.datetime.strptime(t["Дата операции"].split()[0], "%d.%m.%Y").date()
        <= datetime.datetime(2023, 1, 31).date()
        for t in filtered
    )


def test_filter_transactions_empty_list():
    """Тест фильтрации пустого списка транзакций."""
    filtered = filter_transactions_in_data([], "15.05.2023")
    assert len(filtered) == 0


@patch("src.utils.currency_convert")  # Patch currency_convert
def test_top_transactions_success(mock_currency_convert, transactions_list_test):
    """Тест успешный возврат топ 5 операций по сумме."""
    mock_currency_convert.return_value = 8500.0

    result = top_transactions(transactions_list_test)
    assert len(result) == 5
    assert result[0]["amount"] == -3000
    assert result[1]["amount"] == -1065.9
    assert result[2]["amount"] == 1025.0


def test_top_transactions_success_no_curr_amount():
    """Тест успешный возврат топ 5 операций с пропуском операции без суммы и вылюты"""

    transactions_list_test = [
        {"Сумма платежа": "Привет", "Валюта платежа": "RUB"},
        {"Сумма платежа": 22, "Валюта платежа": "RUB"},
        {"Сумма платежа": 55},
    ]

    result = top_transactions(transactions_list_test)
    assert len(result) == 1
    assert result[0]["amount"] == 22


def test_top_transactions_error():
    """Тест неуспешный возврат топ 5 операций с пропуском операции без суммы и вылюты"""

    transactions_list_test = {"Сумма платежа": "Привет", "Валюта платежа": "RUB"}

    result = top_transactions(transactions_list_test)
    assert result == []


@patch("requests.request")
def test_currency_convert_success(mock_get):
    """Успешный тест с расчетом суммы валюты"""
    mock_json_result = {
        "success": True,
        "query": {"from": "USD", "to": "RUB", "amount": 100},
        "info": {"timestamp": 1745788084, "quote": 82.589353},
        "result": 8258.9353,
    }

    mock_json = Mock(return_value=mock_json_result)
    mock_get.return_value.json = mock_json
    mock_get.return_value.status_code = 200

    # Вызываем функцию currency_convert
    result = currency_convert("USD", 100)
    assert result == 8258.94


@patch("requests.request")
def test_currency_convert_error_code(mock_get):
    """Неуспешный тест с расчетом кодом ответа валюты"""
    mock_json_result = None

    mock_json = Mock(return_value=mock_json_result)
    mock_get.return_value.json = mock_json
    mock_get.return_value.status_code = 401

    # Вызываем функцию currency_convert
    result = currency_convert("USD", 100)
    assert result is None


@patch("requests.request")
def test_currency_convert_error_amount(result):
    """Неуспешный тест с расчетом суммы валюты"""

    result = currency_convert("USD", "Привет")
    assert result is None


@patch("src.utils.currency_convert")  # Patch currency_convert
def test_card_list_success(mock_currency_convert, transactions_list_test):
    """Тест успешный по формированию списка карт."""
    mock_currency_convert.return_value = 8500.0

    result = card_list(transactions_list_test)
    expected = [
        {"cashback": 0.25, "last_digits": "7199", "total_spent": -25.0},
        {"cashback": 183.82, "last_digits": "7197", "total_spent": -18381.9},
    ]
    assert result == expected


def test_card_list_error():
    """Тест неуспешный по формированию списка карт."""
    transactions_list_test = {"Сумма платежа": "Привет", "Валюта платежа": "RUB"}

    result = card_list(transactions_list_test)
    assert result == []


@patch("requests.request")
def test_currency_list_success(mock_request):
    """Тест успешный по формированию списка валют"""

    mock_json_result_usd = {
        "success": True,
        "source": "USD",
        "quotes": {"USDRUB": 83.211592},
    }
    mock_response_usd = Mock()
    mock_response_usd.json.return_value = mock_json_result_usd
    mock_response_usd.status_code = 200

    mock_json_result_eur = {
        "success": True,
        "source": "EUR",
        "quotes": {"EURRUB": 99.211592},
    }
    mock_response_eur = Mock()
    mock_response_eur.json.return_value = mock_json_result_eur
    mock_response_eur.status_code = 200

    def side_effect(method, url, headers=None, data=None):
        if "USD" in url:
            return mock_response_usd
        elif "EUR" in url:
            return mock_response_eur
        else:
            return Mock(status_code=404)

    mock_request.side_effect = side_effect

    result = currency_list()

    expected = [{"currency": "USD", "rate": 83.211592}, {"currency": "EUR", "rate": 99.211592}]
    assert result == expected


@patch("requests.request")
def test_currency_list_error(mock_request):
    """Тест неуспешный по формированию списка валют"""

    mock_json_result_usd = {"Ошибка авторизации"}
    mock_response_usd = Mock()
    mock_response_usd.json.return_value = mock_json_result_usd
    mock_response_usd.status_code = 401

    mock_json_result_eur = {"Ошибка авторизации"}
    mock_response_eur = Mock()
    mock_response_eur.json.return_value = mock_json_result_eur
    mock_response_eur.status_code = 401

    def side_effect(method, url, headers=None, data=None):
        if "USD" in url:
            return mock_response_usd
        elif "EUR" in url:
            return mock_response_eur
        else:
            return Mock(status_code=404)

    mock_request.side_effect = side_effect

    result = currency_list()

    expected = []
    assert result == expected
