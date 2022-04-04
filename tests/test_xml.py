import datetime
from pathlib import Path
import logging
from typing import Union

from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing
from springloading_insider_trades.sec_api.helpers.scraping import (
    scrape_form4filing_from_xml,
)

logger = logging.getLogger(__name__)


def test_xml():
    fake_url = "fake-url.com"
    fake_date = datetime.date(1999, 1, 1)
    for p in Path("tests/xml").glob("**/*.xml"):
        with p.open() as f:
            xml = f.read()
            filing: Union[Form4Filing, None] = scrape_form4filing_from_xml(
                xml, fake_date, fake_url
            )

            if "error" in p.name.lower():
                assert filing is None, "Form4Filing is not None but should be"
                continue

            assert filing is not None, "Form4Filing is None"
