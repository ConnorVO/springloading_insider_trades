import datetime
from pathlib import Path
import logging

from springloading_insider_trades.sec_api.helpers.scraping import (
    scrape_form4filing_from_xml,
)

logger = logging.getLogger(__name__)


def test_xml():
    fake_url = "fake-url.com"
    fake_date = datetime.date(2022, 1, 13)
    for p in Path("tests/xml").glob("**/*.xml"):
        with p.open() as f:
            xml = f.read()
            scrape_form4filing_from_xml(xml, fake_date, fake_url)
