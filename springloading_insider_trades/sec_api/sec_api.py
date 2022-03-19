from typing import List
import requests
import logging

from .classes.Form4Filing import Form4Filing
from .helpers.edgar_request import fetch_edgar_data
from .helpers.api import get_sec_query_results
from .helpers.scraping import scrape_form4filing_from_xml

logger = logging.getLogger()


def get_filings(start_date_string: str, end_date_string: str):
    try:
        sec_api_result = get_sec_query_results(start_date_string, end_date_string)
        sec_api_filings = sec_api_result["filings"]
    except Exception as e:
        logger.exception(f"Error getting SEC Query Results: {e}")
        raise SystemExit(e)

    # Skip if there is a ticker because that is a company filing, not an exec. If there is a company filing, there will also be an exec filing that we want
    xml_urls = [x["linkToFilingDetails"] for x in sec_api_filings if not x["ticker"]]

    for url in xml_urls:
        try:
            edgar_res = fetch_edgar_data(url)
        except requests.exceptions.HTTPError as err:
            logger.exceptionf("Error fetching edgar data: {err}\nurl => {url}")
            continue

        try:
            filing_text = edgar_res.text
        except Exception as err:
            logger.exception(
                f"Error getting text from Edgar Response: {err}\nurl => {url}"
            )
            continue

        form4_filings: List[Form4Filing] = scrape_form4filing_from_xml(filing_text)
