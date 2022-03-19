from datetime import datetime
from typing import List


class Form4Filing:
    def __init(self):
        self.name = "Form4"

    # def __init__(
    #     self,
    #     date: datetime,
    #     value: float,
    #     cashflow: float,
    #     daily_twr: float,
    #     weekly_twr: float,
    #     monthly_twr: float,
    #     quarterly_twr: float,
    #     yearly_twr: float,
    #     cumulative_twr: float,
    #     observed: bool,
    # ):
    #     self.date = date
    #     self.value = value
    #     self.cashflow = cashflow
    #     self.daily_twr = daily_twr
    #     self.weekly_twr = weekly_twr
    #     self.monthly_twr = monthly_twr
    #     self.quarterly_twr = quarterly_twr
    #     self.yearly_twr = yearly_twr
    #     self.cumulative_twr = cumulative_twr
    #     self.observed = observed

    # @classmethod
    # def from_stripped_line(cls, stripped_line: List[str]):
    #     return cls(
    #         datetime.strptime(stripped_line[0], "%Y-%m-%d"),
    #         float(stripped_line[1]),
    #         float(stripped_line[2]),
    #         float(stripped_line[3]),
    #         float(stripped_line[4]),
    #         float(stripped_line[5]),
    #         float(stripped_line[6]),
    #         float(stripped_line[7]),
    #         float(stripped_line[8]),
    #         stripped_line[9],
    #     )
