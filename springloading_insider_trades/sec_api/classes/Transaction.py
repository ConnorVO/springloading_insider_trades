from datetime import datetime
from typing import List


class Transaction:
    def __init__(
        self,
        date: datetime,
        security_type: str,
        code: str,
        num_shares: int,
        share_price: float,
        num_shares_after: int,
        acquired_disposed_code: str,
        direct_or_indirect_ownership: str,
        footnotes: List[str],
    ):
        self.date = date
        self.security_type = security_type
        self.code = code
        self.num_shares = num_shares
        self.share_price = share_price
        self.num_shares_after = num_shares_after
        self.acquired_disposed_code = acquired_disposed_code
        self.direct_or_indirect_ownership = direct_or_indirect_ownership
        self.footnotes = footnotes

    def get_share_pct_increase(self):
        return self.num_shares_after / self.num_shares - 1

    @classmethod
    def from_transaction_xml(cls, xml, footnote_xml):
        date = datetime.strptime(xml.transactiondate.value.text, "%Y-%m-%d")
        security_type = xml.securitytitle.value.text
        code = xml.transactioncoding.transactioncode.text

        num_shares = int(xml.transactionamounts.transactionshares.value.text)
        share_price = float(xml.transactionamounts.transactionpricepershare.value.text)

        num_shares_after = int(
            xml.posttransactionamounts.sharesownedfollowingtransaction.value.text
        )
        acquired_disposed_code = (
            xml.transactionamounts.transactionacquireddisposedcode.value.text.strip()
        )

        direct_or_indirect_ownership = (
            xml.ownershipnature.directorindirectownership.text.strip()
        )

        footnote_ids = xml.find_all("footnoteid")
        footnotes: List[str] = []
        for id in footnote_ids:
            footnote_text = footnote_xml.find("footnote", {"id": id.get("id")}).text
            footnotes.append(footnote_text)

        return cls(
            date,
            security_type,
            code,
            num_shares,
            share_price,
            num_shares_after,
            acquired_disposed_code,
            direct_or_indirect_ownership,
            footnotes,
        )


class NonDerivTransaction(Transaction):
    transaction_type = "non-derivative"

    @classmethod
    def from_transaction_xml(cls, xml, footnote_xml):
        execution_date = (
            datetime.strptime(xml.deemedexecutiondate.value.text, "%Y-%m-%d")
            if xml.deemedexecutiondate.value and xml.deemedexecutiondate.value.text
            else None
        )
        res = super().from_transaction_xml(xml, footnote_xml)
        res.__dict__["execution_date"] = execution_date
        res.__dict__["transaction_type"] = cls.transaction_type

        return res


class DerivTransaction(Transaction):
    transaction_type = "derivative"

    @classmethod
    def from_transaction_xml(cls, xml, footnote_xml):
        exercise_price = float(xml.conversionorexerciseprice.value.text)
        exercise_date = (
            datetime.strptime(xml.transactiondate.value.text, "%Y-%m-%d")
            if xml.transactiondate.value and xml.transactiondate.value.text
            else None
        )
        expiration_date = (
            datetime.strptime(xml.expirationdate.value.text, "%Y-%m-%d")
            if xml.expirationdate.value and xml.expirationdate.value.text
            else None
        )

        underlying_security_type = (
            xml.underlyingsecurity.underlyingsecuritytitle.value.text
        )
        underlying_security_num_shares = int(xml.underlyingsecurityshares.value.text)

        res = super().from_transaction_xml(xml, footnote_xml)
        res.__dict__["exercise_price"] = exercise_price
        res.__dict__["exercise_date"] = exercise_date
        res.__dict__["expiration_date"] = expiration_date
        res.__dict__["underlying_security_type"] = underlying_security_type
        res.__dict__["underlying_security_num_shares"] = underlying_security_num_shares
        res.__dict__["transaction_type"] = cls.transaction_type

        return res
