import os
import datetime
import pandas as pd
import json
import requests
import logging
from dotenv import load_dotenv

from typing import List, Dict


load_dotenv()

def greeting():
    '''Приветствие на основании времени суток'''
    date_obj = datetime.datetime.now()
    date_string = int(date_obj.strftime("%H"))
    if 0 <= date_string < 6:
        return "Доброй ночи!"
    elif 6 <= date_string < 12:
        return "Доброе утро!"
    elif 12 <= date_string < 18:
        return "Добрый день!"
    elif 18 <= date_string <= 24:
        return "Добрый вечер!"


def file_reader(filename="operations.xlsx", dirname="data"):
    '''Чтение файла и вывод списка операций только необходимых столбцов'''

    # Путь до файла с транзакциями
    file_path = os.path.join(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dirname), filename
    )

    # Чтение файла с транзакциями
    data_file = pd.read_excel(file_path)

    # Отбираем необходимые столбцы
    data_transactions = data_file.loc[
        :,
        [
            "Дата операции",
            "Статус",
            "Номер карты",
            "Сумма операции",
            "Сумма платежа",
            "Кэшбэк",
            "Бонусы (включая кэшбэк)",
            "Категория",
            "Валюта платежа",
            "Описание"
        ],
    ]

    data_transactions_dict = data_transactions.to_dict(orient="records")

    return data_transactions_dict


def filter_transactions_in_data(transactions_list: List[Dict], filter_date_str: str = datetime.datetime.now()) -> List[Dict]:
    """
    Фильтрует список транзакций, возвращая транзакции за период с 1-го числа месяца входящей даты до самой входящей даты включительно.
    """
    # Преобразуем строку с датой фильтра в объект datetime
    try:
        filter_date = datetime.datetime.strptime(filter_date_str.split()[0], "%d.%m.%Y").date()
    except ValueError:
        print("Ошибка: Неверный формат даты фильтра. Используйте формат ДД.ММ.ГГГГ.")
        return []

    # Вычисляем начало месяца для фильтрации
    start_date = datetime.date(filter_date.year, filter_date.month, 1)

    # Преобразуем даты транзакций и фильтруем
    filtered_transactions = []
    for transaction in transactions_list:
        try:
            transaction_date_str = transaction.get('Дата операции', '').split()[0]
            transaction_date = datetime.datetime.strptime(transaction_date_str, "%d.%m.%Y").date()
        except ValueError:
            print(f"Ошибка: Неверный формат даты операции: {transaction.get('Дата операции')}. Транзакция пропущена.")
            continue

        if start_date <= transaction_date <= filter_date:
            filtered_transactions.append(transaction)

    return filtered_transactions


def top_transactions(transactions_list, top_n: int = 5):
    '''Топ 5 транзакций'''

    logger = logging.getLogger("top_transactions")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(
        "C:/Users/2B/PycharmProjects/Transaction_Analize/logs/top_transactions.log", encoding="utf-8", mode="w"
    )
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    sorted_transactions = sorted(transactions_list, key=lambda x: x.get("Сумма операции", 0), reverse=True)

    new_sorted_transactions = []
    for transaction in sorted_transactions:
        currency = transaction.get('Валюта платежа')
        amount = transaction.get('Сумма платежа')

        if not isinstance(amount, (int, float)):
            logger.info(f"Ошибка: Некорректный формат суммы платежа: {amount}. Транзакция пропущена - {transaction}.")
            continue

        if currency == None:
            print(f'Нет валюты платажа')
            continue

        if currency == 'RUB':
            new_transaction = {
            'date':transaction.get('Дата операции'),
            'amount': amount,
            'category': transaction.get('Категория'),
            'description': transaction.get('Описание')
            }
            new_sorted_transactions.append(new_transaction)

        elif currency != 'RUB':
            is_sum_below_zero = amount < 0
            abs_amount = abs(amount)

            try:
                amount_to_rub = currency_convert(currency, abs_amount)
                logger.info(f'ответ от вызова: {amount_to_rub}')

                if is_sum_below_zero:
                    amount_to_rub = -amount_to_rub

                new_transaction = {
                    'date': transaction.get('Дата операции'),
                    'amount': amount_to_rub,
                    'category': transaction.get('Категория'),
                    'description': transaction.get('Описание')
                }
                new_sorted_transactions.append(new_transaction)

            except Exception as e:
                logger.info(f"Ошибка конвертации валюты ({currency}, {amount}): {e}. Транзакция пропущена - {transaction}.")
                continue

    return new_sorted_transactions[:top_n]


def currency_convert(curr_from: str, amount: int|float|str) -> float|None:
    '''Пересчет суммы иностранной валюты в рубли'''

    logger = logging.getLogger("currency_convert")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(
        "C:/Users/2B/PycharmProjects/Transaction_Analize/logs/currency_convert.log", encoding="utf-8", mode="w"
    )
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    try:
        curr_to = 'RUB'
        payload = {}
        api_key = os.getenv('API_KEY_FOR_CURRENCY_CONVERT')
        headers = {
            "apikey": f"{api_key}"
        }
        logger.info(f"Вызов стороннего api для пересчета суммы c параметрами {curr_from},{amount}")
        url = f"https://api.apilayer.com/currency_data/convert?to={curr_to}&from={curr_from}&amount={amount}"
        r = requests.request("GET", url, headers=headers, data=payload)
        status_code = r.status_code
        json_r = r.json()
        rub_amount = float(round(json_r.get('result'),2))
        logger.info(f'сумма в руб {json_r} {rub_amount}')

        if status_code == 200:
            logger.info(f"Код ответа: {status_code} Ответ: {r.json()}")
            return rub_amount
        else:
            logger.info(f"Код ответа http: {status_code} Ответ: {r.json()}")
            return None
    except Exception as e:
        logger.error(f"Произошла ошибка при обращении к API: {e}")
        return None

def card_list(transactions_list):
    '''Получение списка карт с суммой расходов и кешбеком по карте за период'''
    logger = logging.getLogger("card_list")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(
        "C:/Users/2B/PycharmProjects/Transaction_Analize/logs/card_list.log", encoding="utf-8", mode="w"
    )
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    card_sums = {}
    for transaction in transactions_list:
        card_number = str(transaction.get("Номер карты"))[1:]
        currency = transaction.get('Валюта платежа')
        operation_amount = float(transaction.get("Сумма операции"))

        # Убираем операции без использования карты
        if not card_number or card_number == 'an':
            continue

        # Убираем операции сумма не состоит из цифр
        if not isinstance(operation_amount, (int, float)):
            continue

        # Убираем операции сумма больше 0, так как суммируем расходы
        if operation_amount >= 0:
            continue

        if currency == 'RUB':
            card_operation_amount_rub = operation_amount

        elif currency != 'RUB':
            logger.info(f"Вызов функции для пересчета суммы в рубли по транзакции - {transaction}")
            convert_operation_amount = currency_convert(currency, abs(operation_amount))
            card_operation_amount_rub = -convert_operation_amount
        if card_number in card_sums:
            card_sums[card_number] += card_operation_amount_rub
        else:
            card_sums[card_number] = card_operation_amount_rub

    card_sums_list= []
    for card, total in card_sums.items():
        round_total = round(total, 2)
        card_sums_list.append({"last_digits": card, "total_spent": round_total ,"cashback": abs(round(round_total/100, 2))})

    return card_sums_list


def currency_list(filename="user_settings.json", dirname="data"):
    '''Получение курсов из внешнего АПИ, по валютам из файла-настроек'''

    logger = logging.getLogger("currency_list")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(
        "C:/Users/2B/PycharmProjects/Transaction_Analize/logs/currency_list.log", encoding="utf-8", mode="w"
    )
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    #Путь до файла
    file_path = os.path.join (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dirname), filename)

    #Чтение файла настроек
    logger.info("Чтение файла настроек")
    with open(file_path) as f:
        data = json.load(f)

    settings_list_currency = data.get('user_currencies')
    logger.info(f"Настройки валют: {settings_list_currency}")

    quotes = []
    try:
        for currency in settings_list_currency:
            api_key = os.getenv('API_KEY_FOR_CURRENCY_CONVERT')
            logger.info(f"Вызов внешнего API для получения курса валют с параметрами {currency}")
            url = f"https://api.apilayer.com/currency_data/live?source={currency}"

            payload = {}
            headers = {
                "apikey": f"{api_key}"
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            response_data = response.json()
            logger.info(f"Ответ от API {response_data}")

            for currency_in_response, rate in response_data.get('quotes').items():
                val = currency_in_response[3:]

                # Из списка пар различных валют к переданной, отбираем пару к рублю
                if 'RUB' == val:
                    quotes.append({"currency":currency_in_response[:3],"rate": rate})
                else:
                    continue
    except Exception as e:
        logger.info(f"возникла ошибка при вызове currency_list {e}")

    return quotes


def stock_price(filename="user_settings.json", dirname="data"):
    '''Функция получения цен акций по акциям из файла-настроек'''

    file_path = os.path.join (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dirname), filename)

    with open(file_path) as f:
        data = json.load(f)

    stock_list = []
    settings_list_stock = data.get('user_stocks')

    for stock in settings_list_stock:
        apikey = os.getenv('API_KEY_FOR_STOCKS')
        url = f'https://api.finazon.io/latest/finazon/us_stocks_essential/price?ticker={stock}&apikey={apikey}'
        response = requests.get(url)
        data = response.json()
        stock_list.append({"stock": stock,'price':data.get('p')})

    return stock_list

