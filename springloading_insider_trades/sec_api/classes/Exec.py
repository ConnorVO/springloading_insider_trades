class Exec:
    def __init__(
        self,
        cik: int,
        name: str,
        num_trades: int = None,
        num_correct: int = None,
        ninety_day_return: float = None,
    ):
        self.cik = cik
        self.name = name
        self.num_trades = num_trades
        self.num_correct = num_correct
        self.ninety_day_return = ninety_day_return

    def get_db_json(self):
        obj = {
            "cik": self.cik,
            "name": self.name,
            "num_trades": self.num_trades,
            "num_correct": self.num_correct,
            "ninety_day_return": self.ninety_day_return,
        }

        return obj
