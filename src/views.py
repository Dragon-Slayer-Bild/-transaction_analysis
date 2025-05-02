import json

from src.utils import (
    card_list,
    currency_list,
    file_reader,
    filter_transactions_in_data,
    greeting,
    stock_price,
    top_transactions,
)


def main_page_info(date_search):
    """Функция для формирования Главной страницы"""

    # Вызываем функцию с чтением списка транзакций из файла и функцию с фильтрацией по дате
    transactions_list = filter_transactions_in_data(file_reader(), date_search)

    # Вызываем функции для формирования главной страницы
    main_info = json.dumps(
        {
            "greeting": greeting(),
            "cards": card_list(transactions_list),
            "top_transactions": top_transactions(transactions_list),
            "currency_rates": currency_list(),
            "stock_prices": stock_price(),
        },
        indent=4,
        ensure_ascii=False,
    )
    return main_info
