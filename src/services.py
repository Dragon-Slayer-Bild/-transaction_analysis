import json
import logging
import re

logger = logging.getLogger("transaction_search")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(
    "C:/Users/2B/PycharmProjects/Transaction_Analize/logs/transaction_search.log", encoding="utf-8", mode="w"
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def transaction_search(transactions_list: list[dict], search_string: str) -> str | list[dict]:
    """Поиск транзакции  по описанию (Простой поиск)"""

    if not isinstance(transactions_list, list):
        logger.info("Неверный формат операций, должен быть список")
        return "Неверный формат операций, должен быть список"

    try:
        transactions = []

        for transaction in transactions_list:
            description = transaction.get("Описание")
            if isinstance(description, str):
                if re.search(search_string, description, flags=re.IGNORECASE):
                    transactions.append(transaction)

        json_transactions = json.dumps(transactions, indent=4, ensure_ascii=False)

        return json_transactions

    except (TypeError, AttributeError) as e:
        logger.info(f"Произошла ошибка при поиске {e}")
        return "Произошла ошибка при поиске. Убедитесь, что формат данных верен."
