from typing import List
import requests
import logging
from datetime import datetime

from settings import LOGGER_NAME, SEC_API_DATETIME_FORMAT, SEC_QUERY_SIZE
from .classes.Form4Filing import Form4Filing
from .helpers.edgar import fetch_edgar_data, get_xml_url
from .helpers.api import get_sec_query_results
from .helpers.scraping import scrape_form4filing_from_xml

logger = logging.getLogger(LOGGER_NAME)


def _get_form_4_filing_from_url(url):
    try:
        logger.info(f"Fetching Edgar URL => {url}")
        edgar_res = fetch_edgar_data(get_xml_url(url[1]))
    except requests.exceptions.HTTPError as err:
        logger.exceptionf(f"Error fetching edgar data: {err}\nurl => {url[1]}")
        return

    # Make sure the XML response is valid
    try:
        filing_text = edgar_res.text
    except Exception as err:
        logger.exception(
            f"Error getting text from Edgar Response: {err}\nurl => {url[1]}"
        )
        return

    # Scrape the data we need from the Form 4s
    form4Filing = scrape_form4filing_from_xml(filing_text, url[0], url[1])

    return form4Filing


def get_filings(
    start_date_string: str, end_date_string: str, size: int = SEC_QUERY_SIZE
):
    """Returns filings and error_urls

    Args:
        start_date_string (str): start_date
        end_date_string (str): end_date
        size (int, optional): number of filings to get from SEC API query. Defaults to SEC_QUERY_SIZE.

    Raises:
        SystemExit: Error getting sec_api_result

    Returns:
        Tuple[List[Form4Filing], List[str]]: tuple of filings and error urls
    """
    logger.info(f"Getting sec_query result for {start_date_string} - {end_date_string}")

    # Get a list of all the filings from SEC_API
    sec_api_filings = []
    is_more_filings = True
    while is_more_filings:
        logger.info(
            f"Getting SEC Query Results numbers {len(sec_api_filings)} - {len(sec_api_filings) + 200}"
        )
        try:
            sec_api_result = get_sec_query_results(
                start_date_string,
                end_date_string,
                start=len(sec_api_filings),
                size=size,
            )
            sec_api_filings.extend(sec_api_result["filings"])
            if len(sec_api_result["filings"]) < SEC_QUERY_SIZE:
                is_more_filings = False
        except Exception as e:
            logger.exception(f"Error getting SEC Query Results: {e}")
            raise SystemExit(e)

    logger.info(f"Returned {len(sec_api_filings)} SEC API Filings")

    # Get all the urls for execs/directors to scrape
    ## Skip if there is a ticker because that is a company filing, not an exec. If there is a company filing, there will also be an exec filing that we want
    urls = [
        (
            datetime.strptime(x["filedAt"], SEC_API_DATETIME_FORMAT),
            x["linkToFilingDetails"],
        )
        for x in sec_api_filings
        if not x["ticker"]
    ]

    form4_filings: List[Form4Filing] = []
    error_urls: List[str] = []

    # Get the XML from each filing
    logger.info("Getting edgar form4 info for each sec_query result")
    for url in urls:
        form4_filing = _get_form_4_filing_from_url(url)
        if form4_filing:
            form4_filings.append(form4_filing)
        else:
            error_urls.append(url)

    return form4_filings, error_urls
