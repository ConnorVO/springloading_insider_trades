import datetime
from typing import Tuple, Union
from springloading_insider_trades.email.email import send_error_urls_email

from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing
from springloading_insider_trades.sec_api.helpers.scraping import (
    scrape_form4filing_from_xml,
)

SEND_EMAIL = False

fake_url = "fake-url.com"
fake_date = datetime.date(1999, 1, 1)


def _conv_xml(xml) -> Union[Form4Filing, None]:
    filing: Union[Form4Filing, None] = scrape_form4filing_from_xml(
        xml, fake_date, fake_url
    )

    return filing


def test_email():
    with open("./tests/xml/xml_error.xml", "r") as f:
        xml = f.read()

    filing: Form4Filing = _conv_xml(xml)
    assert filing is None, "Form4Filing is not None while running text_error_xml"

    if SEND_EMAIL:
        did_send = send_error_urls_email(
            fake_date.strftime("%Y-%m-%d"), [fake_url, fake_url]
        )
        assert did_send, "Test Email didn't send"

    assert True
