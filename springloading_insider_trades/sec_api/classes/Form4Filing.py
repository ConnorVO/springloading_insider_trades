from datetime import datetime
from typing import List

from .Company import Company
from .Transaction import Transaction


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
        non_deriv_transactions: List[Transaction],
        deriv_transactions: List[Transaction],
        footnotes: List[str],
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

    @classmethod
    def from_xml(cls, xml, filing_date: datetime):
        company: Company = Company.from_issuer_xml(xml.find("issuer"))

        # only get the first reporting owner. If there are multiple, then it is a hedge fund and we don't care about the individuals, just the hedge fund
        xml_reporting_owner = xml.find("reportingowner")
        owner_cik: str = xml_reporting_owner.reportingownerid.rptownercik.text
        owner_name: str = xml_reporting_owner.reportingownerid.rptownername.text
        is_director: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.isdirector == 1
            else False
        )
        is_officer: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.isofficer == 1
            else False
        )
        is_ten_percent_owner: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.istenpercentowner == 1
            else False
        )
        is_other: bool = (
            True
            if xml_reporting_owner.reportingownerrelationship.isother == 1
            else False
        )
        owner_title = xml_reporting_owner.reportingownerrelationship.officertitle.text

        xml_footnotes = xml.footnotes.find_all("footnote")
        footnotes: List[str] = []
        for footnote in xml_footnotes:
            footnotes.append(footnote.text)

        non_deriv_transactions: List[Transaction] = []
        if xml.nonderivativetable and xml.nonderivativetable.find_all(
            "nonderivativetransaction"
        ):
            xml_non_deriv_transactions = xml.nonderivativetable.find_all(
                "nonderivativetransaction"
            )
            for xml_transaction in xml_non_deriv_transactions:
                non_deriv_transactions.append(
                    Transaction.from_transaction_xml(xml_transaction, xml_footnotes)
                )

        deriv_transactions: List[Transaction] = []
        if xml.derivativetable and xml.derivativetable.find_all(
            "derivativetransaction"
        ):
            xml_deriv_transactions = xml.derivativetable.find_all(
                "derivativetransaction"
            )
            for xml_transaction in xml_deriv_transactions:
                deriv_transactions.append(
                    Transaction.from_transaction_xml(xml_transaction, xml_footnotes)
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
        )
