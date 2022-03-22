class Company:
    def __init__(self, cik: str, name: str, ticker: str):
        self.cik = cik
        self.name = name
        self.ticker = ticker

    @classmethod
    def from_issuer_xml(cls, xml):
        return cls(
            xml.issuercik.text,
            xml.issuername.text,
            xml.issuertradingsymbol.text,
        )
