import pandas as pd
import datetime
import logging
from typing import Optional, Callable
from functools import wraps
import json
import os


logger = logging.getLogger('reports')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(
    "C:/Users/2B/PycharmProjects/Transaction_Analize/logs/reports.log", encoding="utf-8", mode="w"
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def report_decorator(filename: Optional[str] = None):
    """
    Декоратор для функций-отчетов, который записывает результат в файл.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Получаю результат работы функции spending_by_category
            result = func(*args, **kwargs)

            dirname = 'data'

            # Если передано имя файла
            if filename:
                file_path = os.path.join(
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dirname), f"{filename}.json")
            else:
                # Если не передали имя файла, генерируем свое
                func_name = func.__name__
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(
                    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), dirname), f"{func_name}_{timestamp}.json"
                )

            try:

                if isinstance(result, pd.DataFrame):
                    result_for_json = result.to_json(orient="records", force_ascii=False) #Преобразуем в JSON строку
                else:
                    result_for_json = result

                # Записываем результата в файл (формат JSON)
                with open(file_path, 'w', encoding='utf-8') as f:
                     if isinstance(result_for_json, str):
                         f.write(result_for_json)
                     else:
                         json.dump(result_for_json, f, indent=4, ensure_ascii=False)

                logger.info(f"Отчет '{func.__name__}' успешно записан в файл: {file_path}")
            except Exception as e:
                logger.error(f"Ошибка при записи отчета '{func.__name__}' в файл: {e}")

            return result # Возвращаем результат, чтобы не сломать логику работы функции
        return wrapper
    return decorator


@report_decorator() #Здесь можно передать имя файла
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """Рассчитывает траты по заданной категории за последние три месяца."""
    try:
        if date:
            report_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        else:
            report_date = datetime.date.today()

        # Вычисляем дату начала периода (три месяца назад)
        start_date = report_date - datetime.timedelta(days=90)

        # Преобразуюм столбец "Дата операции" в datetime.date
        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], format='%d.%m.%Y %H:%M:%S').dt.date


        # Фильтрую транзакции по категории и дате
        filtered_transactions = transactions[
            (transactions['Категория'] == category) &
            (transactions['Дата операции'] >= start_date) &
            (transactions['Дата операции'] <= report_date)
        ]

        # Группирую по категории и суммируем траты
        spending = filtered_transactions.groupby('Категория')['Сумма операции'].sum().reset_index()

        logger.info(f"Отчет 'spending_by_category' для категории '{category}' сформирован.")
        return spending

    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка при формировании отчета 'spending_by_category': {e}")
        return pd.DataFrame()


# Пример использования (в другом файле или в этом же для демонстрации)
if __name__ == '__main__':
    # Создаем пример датафрейма
    data = [{
        "Дата операции": "04.01.2018 15:00:41",
        "Статус": "OK",
        "Категория": "Каршеринг",
        "Номер карты": "*7199",
        "Сумма операции": 1025.0,
        "Сумма платежа": 1025.0,
        "Описание": "Оплата денег",
        "Кэшбэк": 'nan',
        "Бонусы (включая кэшбэк)": 20,
    },
    {
        "Дата операции": "04.01.2018 15:00:41",
        "Статус": "OK",
        "Категория": "Каршеринг",
        "Номер карты": "*7199",
        "Сумма операции": -25.0,
        "Сумма платежа": -25.0,
        "Описание": "Оплата денег",
        "Кэшбэк": 'nan',
        "Бонусы (включая кэшбэк)": 20,
    },
    {
        "Дата операции": "04.01.2018 14:05:08",
        "Статус": "OK",
        "Категория": "Каршеринг",
        "Номер карты": "*7197",
        "Сумма операции": -1065.9,
        "Сумма платежа": -1065.9,
        "Описание": "Оплата денег",
        "Кэшбэк": 'nan',
        "Бонусы (включая кэшбэк)": 21,
    },
    {
        "Дата операции": "03.01.2018 15:03:35",
        "Статус": "OK",
        "Категория": "Каршеринг",
        "Номер карты": "*7197",
        "Сумма операции": -73.06,
        "Сумма платежа": -73.06,
        "Описание": "Перевод денег",
        "Кэшбэк": 'nan',
        "Бонусы (включая кэшбэк)": 1,
    },
    {
        "Дата операции": "03.01.2018 14:55:21",
        "Статус": "OK",
        "Категория": "Каршеринг",
        "Номер карты": "*7197",
        "Сумма операции": -21.0,
        "Сумма платежа": -21.0,
        "Описание": "Оплата за товар",
        "Кэшбэк": 'nan',
        "Бонусы (включая кэшбэк)": 0,
    },
    {
        "Дата операции": "01.01.2018 20:27:51",
        "Статус": "OK",
        "Категория": "Каршеринг",
        "Номер карты": "*7197",
        "Сумма операции": -316.0,
        "Сумма платежа": -316.0,
        "Описание": "Перевод денег",
        "Кэшбэк": 'nan',
        "Бонусы (включая кэшбэк)": 6,
    },
    {
        "Дата операции": "01.01.2018 12:49:53",
        "Статус": "Failed",
        "Категория": "Каршеринг",
        "Номер карты": 'nan',
        "Сумма операции": -3000.0,
        "Сумма платежа": -3000.0,
        "Описание": "Перевод денег",
        "Кэшбэк": 'nan',
        "Бонусы (включая кэшбэк)": 0,
    }]

    df = pd.DataFrame(data)

    # Пример вызова функции с датой
    spending_report = spending_by_category(df, 'Каршеринг', '2018-01-04') #Указываем дату в формате ГГГГ-ММ-ДД
    print("Отчет по тратам (Каршеринг, с датой):")
    print(spending_report)