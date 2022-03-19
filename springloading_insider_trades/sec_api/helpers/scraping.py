from bs4 import BeautifulSoup
import logging


def scrape_form4filing_from_xml(text: str):
    # $save
    soup = BeautifulSoup(text, "lxml")

    import pprint

    pprint.PrettyPrinter.pprint(soup)
