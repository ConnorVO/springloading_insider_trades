from typing import List
from springloading_insider_trades.intrinio_api.get_prices_between_dates import (
    get_prices_between_dates,
)
from intrinio_sdk import StockPriceSummary


class TestIntrinio:
    def test_get_multiple_pages(self):
        stock_prices: List[StockPriceSummary] = get_prices_between_dates(
            "AAPL", start_date="2021-01-01", end_date="2022-01-01"
        )

        assert (
            len(stock_prices) == 252
        ), f"stock_prices should be length of 151 but is {len(stock_prices)} in List[StockPriceSummary]"

    def test_single_page(self):
        stock_prices: List[StockPriceSummary] = get_prices_between_dates(
            "NVDA", start_date="2022-01-04", end_date="2022-02-09"
        )

        assert (
            len(stock_prices) == 26
        ), f"stock_prices should be length of 26 but is {len(stock_prices)} in List[StockPriceSummary]"
