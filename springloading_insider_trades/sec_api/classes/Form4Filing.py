from datetime import datetime
from typing import List

from .Company import Company
from .Transaction import NonDerivTransaction, DerivTransaction


class Form4Filing:
    filing_type = "4"

    def __init__(
        self,
        company: Company,
        filing_date: datetime,
        owner_name: str,
        owner_cik: str,
        is_director: bool,
        is_officer: bool,
        is_ten_percent_owner: bool,
        is_other: bool,
        owner_title: str,
        non_deriv_transactions: List[NonDerivTransaction],
        deriv_transactions: List[DerivTransaction],
        footnotes: List[str],
        url: str,
    ):
        self.company = company
        self.filing_date = filing_date
        self.owner_name = owner_name
        self.owner_cik = owner_cik
        self.is_director = is_director
        self.is_officer = is_officer
        self.is_ten_percent_owner = is_ten_percent_owner
        self.is_other = is_other
        self.owner_title = owner_title
        self.non_deriv_transactions = non_deriv_transactions
        self.deriv_transactions = deriv_transactions
        self.footnotes = footnotes
        self.url = url

        # composite primary key that will be used to guarantee uniqueness and reference from transactions
        self.id = company.cik + filing_date.isoformat() + owner_cik

    def get_all_transactions(self):
        return self.non_deriv_transactions + self.deriv_transactions

    @classmethod
    def from_xml(cls, xml, filing_date: datetime, url: str):
        company: Company = Company.from_issuer_xml(xml.find("issuer"))

        # only get the first reporting owner. If there are multiple, then it is a hedge fund and we don't care about the individuals, just the hedge fund
        xml_reporting_owner = xml.find("reportingowner")
        owner_cik: str = xml_reporting_owner.reportingownerid.rptownercik.text
        owner_name: str = xml_reporting_owner.reportingownerid.rptownername.text
        is_director: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.isdirector.text == "1"
            else False
        )
        is_officer: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.isofficer.text == "1"
            else False
        )
        is_ten_percent_owner: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.istenpercentowner.text
            == "1"
            else False
        )
        is_other: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.isother.text == "1"
            else False
        )
        owner_title = xml_reporting_owner.reportingownerrelationship.officertitle.text

        footnotes: List[str] = []
        if xml.footnotes:
            xml_footnotes = xml.footnotes.find_all("footnote")
            for footnote in xml_footnotes:
                footnotes.append(footnote.text)

        # Probably not the best that I have to recreate here to pass into transactions
        filing_id: str = company.cik + filing_date.isoformat() + owner_cik

        non_deriv_transactions: List[NonDerivTransaction] = []
        if xml.nonderivativetable and xml.nonderivativetable.find_all(
            "nonderivativetransaction"
        ):
            xml_non_deriv_transactions = xml.nonderivativetable.find_all(
                "nonderivativetransaction"
            )
            for xml_transaction in xml_non_deriv_transactions:
                non_deriv_transactions.append(
                    NonDerivTransaction.from_transaction_xml(
                        xml_transaction, xml.footnotes, filing_id
                    )
                )

        deriv_transactions: List[DerivTransaction] = []
        if xml.derivativetable and xml.derivativetable.find_all(
            "derivativetransaction"
        ):
            xml_deriv_transactions = xml.derivativetable.find_all(
                "derivativetransaction"
            )
            for xml_transaction in xml_deriv_transactions:
                deriv_transactions.append(
                    DerivTransaction.from_transaction_xml(
                        xml_transaction, xml.footnotes, filing_id
                    )
                )

        return cls(
            company,
            filing_date,
            owner_name,
            owner_cik,
            is_director,
            is_officer,
            is_ten_percent_owner,
            is_other,
            owner_title,
            non_deriv_transactions,
            deriv_transactions,
            footnotes,
            url,
        )

    def get_db_json(self):
        obj = {
            "id": self.id,
            "company": self.company.cik,
            "filing_date": self.filing_date.isoformat(),
            "owner_name": self.owner_name,
            "owner_cik": self.owner_cik,
            "is_director": self.is_director,
            "is_officer": self.is_officer,
            "is_ten_percent_owner": self.is_ten_percent_owner,
            "is_other": self.is_other,
            "owner_title": self.owner_title,
            "footnotes": self.footnotes,
            "url": self.url,
        }

        return obj
