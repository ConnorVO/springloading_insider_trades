from datetime import datetime
from typing import List


class Transaction:
    def __init__(
        self,
        date: datetime,
        security_type: str,
        code: str,
        num_shares: float,
        share_price: float,
        num_shares_after: float,
        acquired_disposed_code: str,
        direct_or_indirect_ownership: str,
        footnotes: List[str],
        filing_id: str,
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
        self.filing_id = filing_id

        # composite primary key for ensuring only unique items in db
        self.id = date.isoformat() + str(num_shares) + str(num_shares_after)

    def get_share_pct_increase(self):
        return self.num_shares_after / self.num_shares - 1

    @classmethod
    def from_transaction_xml(cls, xml, footnote_xml, filing_id):
        date = None
        for fmt in ["%Y-%m-%d", "%Y-%m-%d%z", "%Y-%m-%d-%I:%M", "%Y-%m-%d+%I:%M"]:
            try:
                date = (
                    datetime.strptime(xml.transactiondate.value.text, fmt)
                    if xml.transactiondate and xml.transactiondate.value
                    else None
                )
            except ValueError:
                pass

        security_type = (
            xml.securitytitle.value.text
            if xml.securitytitle and xml.securitytitle.value
            else None
        )
        code = (
            xml.transactioncoding.transactioncode.text
            if xml.transactioncoding and xml.transactioncoding.transactioncode
            else None
        )

        num_shares = (
            float(xml.transactionamounts.transactionshares.value.text)
            if xml.transactionamounts
            and xml.transactionamounts.transactionshares
            and xml.transactionamounts.transactionshares.value
            else None
        )
        share_price = (
            float(xml.transactionamounts.transactionpricepershare.value.text)
            if xml.transactionamounts
            and xml.transactionamounts.transactionpricepershare
            and xml.transactionamounts.transactionpricepershare.value
            else None
        )

        num_shares_after = (
            float(xml.posttransactionamounts.sharesownedfollowingtransaction.value.text)
            if xml.posttransactionamounts
            and xml.posttransactionamounts.sharesownedfollowingtransaction
            and xml.posttransactionamounts.sharesownedfollowingtransaction.value
            else None
        )
        acquired_disposed_code = (
            (xml.transactionamounts.transactionacquireddisposedcode.value.text.strip())
            if xml.transactionamounts
            and xml.transactionamounts.transactionacquireddisposedcode
            and xml.transactionamounts.transactionacquireddisposedcode.value
            else None
        )

        direct_or_indirect_ownership = (
            (xml.ownershipnature.directorindirectownership.text.strip())
            if xml.ownershipnature and xml.ownershipnature.directorindirectownership
            else None
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
            filing_id,
        )


class NonDerivTransaction(Transaction):
    transaction_type = "non-derivative"

    @classmethod
    def from_transaction_xml(cls, xml, footnote_xml, filing_id: str):
        execution_date = None
        for fmt in ["%Y-%m-%d", "%Y-%m-%d%z", "%Y-%m-%d-%I:%M", "%Y-%m-%d+%I:%M"]:
            try:
                execution_date = (
                    datetime.strptime(xml.deemedexecutiondate.value.text, fmt)
                    if xml.deemedexecutiondate
                    and xml.deemedexecutiondate.value
                    and xml.deemedexecutiondate.value.text
                    else None
                )
            except ValueError:
                pass

        res = super().from_transaction_xml(xml, footnote_xml, filing_id)
        res.__dict__["execution_date"] = execution_date
        res.__dict__["transaction_type"] = cls.transaction_type

        return res

    def get_db_json(self):
        obj = {
            "id": self.id,
            "date": self.date.isoformat(),
            "security_type": self.security_type,
            "code": self.code,
            "num_shares": self.num_shares,
            "share_price": self.share_price,
            "num_shares_after": self.num_shares_after,
            "acquired_disposed_code": self.acquired_disposed_code,
            "direct_or_indirect_ownership": self.direct_or_indirect_ownership,
            "footnotes": self.footnotes,
            "filing_id": self.filing_id,
            "footnotes": self.footnotes,
            "transaction_type": self.transaction_type,
            "execution_date": self.execution_date.isoformat()
            if self.execution_date
            else None,
            # must mark missing as None because Supabase doesn't let you upload different types in one insert
            "exercise_price": None,
            "exercise_date": None,
            "expiration_date": None,
            "underlying_security_type": None,
            "underlying_security_num_shares": None,
        }

        return obj


class DerivTransaction(Transaction):
    transaction_type = "derivative"

    @classmethod
    def from_transaction_xml(cls, xml, footnote_xml, filing_id: str):
        exercise_price = (
            float(xml.conversionorexerciseprice.value.text)
            if xml.conversionorexerciseprice and xml.conversionorexerciseprice.value
            else None
        )

        exercise_date = None
        for fmt in ["%Y-%m-%d", "%Y-%m-%d%z", "%Y-%m-%d-%I:%M", "%Y-%m-%d+%I:%M"]:
            try:
                exercise_date = (
                    datetime.strptime(xml.transactiondate.value.text, fmt)
                    if xml.transactiondate
                    and xml.transactiondate.value
                    and xml.transactiondate.value.text
                    else None
                )
            except ValueError:
                pass

        expiration_date = None
        for fmt in ["%Y-%m-%d", "%Y-%m-%d%z", "%Y-%m-%d-%I:%M", "%Y-%m-%d+%I:%M"]:
            try:
                expiration_date = (
                    datetime.strptime(xml.expirationdate.value.text, fmt)
                    if xml.expirationdate
                    and xml.expirationdate.value
                    and xml.expirationdate.value.text
                    else None
                )
            except ValueError:
                pass

        underlying_security_type = (
            (xml.underlyingsecurity.underlyingsecuritytitle.value.text)
            if xml.underlyingsecurity
            and xml.underlyingsecurity.underlyingsecuritytitle
            and xml.underlyingsecurity.underlyingsecuritytitle.value
            else None
        )
        underlying_security_num_shares = (
            float(xml.underlyingsecurityshares.value.text)
            if xml.underlyingsecurityshares and xml.underlyingsecurityshares.value
            else None
        )

        res = super().from_transaction_xml(xml, footnote_xml, filing_id)
        res.__dict__["exercise_price"] = exercise_price
        res.__dict__["exercise_date"] = exercise_date
        res.__dict__["expiration_date"] = expiration_date
        res.__dict__["underlying_security_type"] = underlying_security_type
        res.__dict__["underlying_security_num_shares"] = underlying_security_num_shares
        res.__dict__["transaction_type"] = cls.transaction_type

        return res

    def get_db_json(self):
        obj = {
            "id": self.id,
            "date": self.date.isoformat(),
            "security_type": self.security_type,
            "code": self.code,
            "num_shares": self.num_shares,
            "share_price": self.share_price,
            "num_shares_after": self.num_shares_after,
            "acquired_disposed_code": self.acquired_disposed_code,
            "direct_or_indirect_ownership": self.direct_or_indirect_ownership,
            "footnotes": self.footnotes,
            "filing_id": self.filing_id,
            "footnotes": self.footnotes,
            "transaction_type": self.transaction_type,
            "exercise_price": self.exercise_price,
            "exercise_date": self.exercise_date.isoformat()
            if self.exercise_date
            else None,
            "expiration_date": self.expiration_date.isoformat()
            if self.expiration_date
            else None,
            "underlying_security_type": self.underlying_security_type,
            "underlying_security_num_shares": self.underlying_security_num_shares,
            # must mark missing as None because Supabase doesn't let you upload different types in one insert
            "execution_date": None,
        }

        return obj
