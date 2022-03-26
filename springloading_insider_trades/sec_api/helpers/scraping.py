from bs4 import BeautifulSoup
from datetime import datetime
import logging

from settings import LOGGER_NAME

from ..classes.Form4Filing import Form4Filing

logger = logging.getLogger(LOGGER_NAME)


def scrape_form4filing_from_xml(text: str, filing_date: datetime, url: str):
    # $save
    soup = BeautifulSoup(text, "lxml")
    try:
        form4Filing: Form4Filing = Form4Filing.from_xml(soup, filing_date, url)
    except AttributeError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(f"Unknown error creating Form4Filing:\n{e}")

    return form4Filing if form4Filing else None
