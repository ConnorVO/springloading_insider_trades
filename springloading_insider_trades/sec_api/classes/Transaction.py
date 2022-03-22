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
        num_shares_after: float,
        acquired_disposed_code: str,
        footnotes: List[str],
    ):
        self.date = date
        self.security_type = security_type
        self.code = code
        self.num_shares = num_shares
        self.share_price = (share_price,)
        self.num_shares_after = (num_shares_after,)
        self.acquired_disposed_code = acquired_disposed_code
        self.footnotes = footnotes

    @classmethod
    def from_transaction_xml(cls, xml, footnote_xml):
        date = datetime.strptime(xml.transactiondate.value.text, "%Y-%m-%d")
        security_type = xml.securitytitle.value.text
        code = xml.transactioncoding.transactioncode.text
        num_shares = int(xml.transactionamounts.transactionshares.value.text)
        share_price = float(xml.transactionamounts.transactionpricepershare.value.text)
        num_shares_after = float(
            xml.posttransactionamounts.sharesownedfollowingtransaction.value.text
        )
        acquired_disposed_code = (
            xml.transactionamounts.transactionacquireddisposedcode.value.text
        )

        footnote_ids = xml.find_all("footnote_id")
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
            footnotes,
        )
