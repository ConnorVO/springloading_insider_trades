from bs4 import BeautifulSoup
from datetime import datetime
import logging

from settings import LOGGER_NAME

from ..classes.Form4Filing import Form4Filing

logger = logging.getLogger(LOGGER_NAME)


def scrape_form4filing_from_xml(text: str, filing_date: datetime, url: str):
    # $save
    soup = BeautifulSoup(text, "lxml")
    form4Filing: Form4Filing = Form4Filing.from_xml(soup, filing_date, url)

    import pprint

    for t in form4Filing.deriv_transactions:
        pprint.PrettyPrinter().pprint(t.__dict__)

    return form4Filing
