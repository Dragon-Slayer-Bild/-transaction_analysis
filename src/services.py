import re

def transaction_search(transactions_list: list[dict], search_string: str) -> str | list[dict]:
    """Поиск транзакции  по описанию (Простой поиск)"""

    if not isinstance(transactions_list, list):
        return "Неверный формат операций, должен быть список"

    try:
        transactions = []
        for transaction in transactions_list:
            description = transaction.get("Описание")
            if isinstance(description, str):
                if re.search(search_string, description, flags=re.IGNORECASE):
                    transactions.append(transaction)
        return transactions

    except (TypeError, AttributeError):
        return "Произошла ошибка при поиске. Убедитесь, что формат данных верен."
