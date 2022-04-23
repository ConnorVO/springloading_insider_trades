from typing import NewType
from enum import Enum


class Frequencies(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


Frequency = NewType("Frequency", Frequencies)
