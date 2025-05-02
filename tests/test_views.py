import json
from unittest.mock import patch

from src.views import main_page_info


def test_main_page_info():
    @patch("__main__.filter_transactions_in_data")
    @patch("__main__.file_reader")
    @patch("__main__.greeting")
    @patch("__main__.card_list")
    @patch("__main__.top_transactions")
    @patch("__main__.currency_list")
    @patch("__main__.stock_price")
    def test_main_page_info_success(
        self,
        mock_stock_price,
        mock_currency_list,
        mock_top_transactions,
        mock_card_list,
        mock_greeting,
        mock_file_reader,
        mock_filter_transactions,
    ):
        """Тест успешного формирования главной страницы."""

        mock_file_reader.return_value = [{"transaction": "data"}]
        mock_filter_transactions.return_value = [{"filtered": "transaction"}]
        mock_greeting.return_value = "Доброй ночи!"
        mock_card_list.return_value = [{"last_digits": "4556", "total_spent": -362.0, "cashback": 3.62}]
        mock_top_transactions.return_value = [
            {"date": "01.01.2020 14:47:42", "amount": -362.0, "category": "Красота", "description": "OOO Balid"}
        ]
        mock_currency_list.return_value = [
            {"currency": "USD", "rate": 82.269106},
            {"currency": "EUR", "rate": 92.883878},
        ]
        mock_stock_price.return_value = [
            {"stock": "AAPL", "price": 204.67},
            {"stock": "GOOG", "price": 163.5},
            {"stock": "TSLA", "price": 278.25},
        ]

        result = main_page_info("01.01.2020")

        expected_result = json.dumps(
            {
                "greeting": "Доброй ночи!",
                "cards": [{"last_digits": "4556", "total_spent": -362.0, "cashback": 3.62}],
                "top_transactions": [
                    {
                        "date": "01.01.2020 14:47:42",
                        "amount": -362.0,
                        "category": "Красота",
                        "description": "OOO Balid",
                    }
                ],
                "currency_rates": [{"currency": "USD", "rate": 82.269106}, {"currency": "EUR", "rate": 92.883878}],
                "stock_prices": [
                    {"stock": "AAPL", "price": 204.67},
                    {"stock": "GOOG", "price": 163.5},
                    {"stock": "TSLA", "price": 278.25},
                ],
            },
            indent=4,
            ensure_ascii=False,
        )

        assert result == expected_result
