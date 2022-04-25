import logging
from typing import List, Union
from settings import LOGGER_NAME
from springloading_insider_trades.intrinio_api.types.Frequency import (
    Frequencies,
    Frequency,
)
import intrinio_sdk as intrinio
from intrinio_sdk import ApiResponseSecurityStockPrices, StockPriceSummary
from intrinio_sdk.rest import ApiException

logger = logging.getLogger(LOGGER_NAME)


def get_prices_between_dates(
    ticker: str,
    start_date: str = "",
    end_date: str = "",
    frequency: Frequency = Frequencies.DAILY,
    page_size: int = 100,
    next_page: str = "",
    stock_prices: List[StockPriceSummary] = None,
) -> List[StockPriceSummary]:
    if not stock_prices:
        stock_prices = []

    try:
        response: ApiResponseSecurityStockPrices = (
            intrinio.SecurityApi().get_security_stock_prices(
                ticker,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency.value,
                page_size=page_size,
                next_page=next_page,
            )
        )
        stock_prices.extend(response.stock_prices)
        if response.next_page:
            logger.info(f"Getting next page: {response.next_page}")
            return get_prices_between_dates(
                ticker,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                page_size=page_size,
                next_page=response.next_page,
                stock_prices=stock_prices,
            )
    except ApiException as e:
        logger.error(
            "Exception when calling SecurityApi->get_security_intraday_prices: %s\n" % e
        )

    return stock_prices
