from typing import List
import requests
import logging
from datetime import datetime

from settings import LOGGER_NAME, SEC_API_DATETIME_FORMAT
from .classes.Form4Filing import Form4Filing
from .helpers.edgar import fetch_edgar_data, get_xml_url
from .helpers.api import get_sec_query_results
from .helpers.scraping import scrape_form4filing_from_xml

logger = logging.getLogger(LOGGER_NAME)


def get_filings(start_date_string: str, end_date_string: str):
    logger.info("Getting sec_query result")
    try:
        sec_api_result = get_sec_query_results(start_date_string, end_date_string)
        sec_api_filings = sec_api_result["filings"]
    except Exception as e:
        logger.exception(f"Error getting SEC Query Results: {e}")
        raise SystemExit(e)

    # Skip if there is a ticker because that is a company filing, not an exec. If there is a company filing, there will also be an exec filing that we want
    urls = [
        (
            datetime.strptime(x["filedAt"], SEC_API_DATETIME_FORMAT),
            x["linkToFilingDetails"],
        )
        for x in sec_api_filings
        if not x["ticker"]
    ]

    logger.info("Getting edgar form4 info for each sec_query result")
    for url in urls:
        try:
            edgar_res = fetch_edgar_data(get_xml_url(url[1]))
        except requests.exceptions.HTTPError as err:
            logger.exceptionf(f"Error fetching edgar data: {err}\nurl => {url[1]}")
            continue

        try:
            filing_text = edgar_res.text
        except Exception as err:
            logger.exception(
                f"Error getting text from Edgar Response: {err}\nurl => {url[1]}"
            )
            continue

        form4_filings: List[Form4Filing] = []
        error_urls: List[str] = []
        form4Filing = scrape_form4filing_from_xml(filing_text, url[0], url[1])
        if form4Filing:
            form4_filings.append(form4Filing)
        else:
            error_urls.append(url)

    return form4_filings, error_urls
