import datetime
from typing import Tuple, Union
from springloading_insider_trades.db.db import (
    # delete_company,
    delete_error_url,
    delete_filing,
    insert_error_url,
    insert_filing_data,
)

from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing
from springloading_insider_trades.sec_api.helpers.scraping import (
    scrape_form4filing_from_xml,
)


class TestDB:
    def _conv_xml(self, xml) -> Tuple[Union[Form4Filing, None], str]:
        fake_url = "fake-url.com"
        fake_date = datetime.date(1999, 1, 1)
        filing: Union[Form4Filing, None] = scrape_form4filing_from_xml(
            xml, fake_date, fake_url
        )

        return filing, fake_url

    # testing xml that has timestamp with hour offset
    def test_xml_timestamp(self):
        with open("./tests/xml/xml_timestamp.xml", "r") as f:
            xml = f.read()

        filing, _ = self._conv_xml(xml)
        assert (
            filing is not None
        ), "Form4Filing is None while running test_xml_timestamp"

        try:
            is_inserted = insert_filing_data(filing)
            assert (
                is_inserted
            ), f"Form4Filing {filing.id} not inserted while running test_xml_timestamp"
        except Exception as e:
            assert (
                False
            ), f"Form4Filing {filing.id} not inserted while running test_xml_timestamp"

        is_filing_deleted = delete_filing(filing)
        assert (
            is_filing_deleted
        ), f"Form4Filing {filing.id} not deleted while running test_xml_timestamp"

        ## NOTE: DO NOT DELETE COMPANY BECAUSE IT MAY BE REFERENCED BY LIVE FILINGS
        # is_company_deleted = delete_company(filing.company)
        # assert (
        #     is_company_deleted
        # ), f"Company {filing.company.cik} not deleted while running test_xml_timestamp"

    def test_xml_deriv_and_nonderiv(self):
        with open("./tests/xml/xml_deriv_and_nonderiv.xml", "r") as f:
            xml = f.read()

        filing, _ = self._conv_xml(xml)
        assert (
            filing is not None
        ), "Form4Filing is None while running test_xml_deriv_and_nonderiv"

        try:
            is_inserted = insert_filing_data(filing)
            assert (
                is_inserted
            ), f"Form4Filing {filing.id} not inserted while running test_xml_deriv_and_nonderiv"
        except Exception as e:
            assert (
                False
            ), f"Form4Filing {filing.id} not inserted while running test_xml_deriv_and_nonderiv"

        is_filing_deleted = delete_filing(filing)
        assert (
            is_filing_deleted
        ), f"Form4Filing {filing.id} not deleted while running test_xml_deriv_and_nonderiv"

    def test_error_xml(self):
        with open("./tests/xml/xml_error.xml", "r") as f:
            xml = f.read()

        filing, error_url = self._conv_xml(xml)
        assert filing is None, "Form4Filing is not None while running text_error_xml"

        is_inserted = insert_error_url(error_url)
        assert (
            is_inserted
        ), f"Error URL (url: {error_url}) not inserted while running test_error_xml"

        is_error_url_deleted = delete_error_url(error_url)
        assert (
            is_error_url_deleted
        ), f"Error URL (url: {error_url}) not deleted while running test_error_xml"
