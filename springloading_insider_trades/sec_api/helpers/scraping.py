from bs4 import BeautifulSoup
from datetime import datetime
import logging

from ..classes.Form4Filing import Form4Filing

logger = logging.getLogger()


def scrape_form4filing_from_xml(text: str, filing_date: datetime):
    # $save
    soup = BeautifulSoup(text, "lxml")

    # issuer_cik = soup.issuer.issuercik
    # issuer_name = soup.issuer.issuername
    # issuer_ticker = soup.issuer.issuertradingsymbol
    form4Filing: Form4Filing = Form4Filing.from_xml(soup, filing_date)

    import pprint

    pprint.PrettyPrinter().pprint(form4Filing.__dict__)

    return form4Filing
