from enum import Enum
from dataclasses import dataclass

@dataclass
class POS:
    row: int = -1
    col: int = -1

class StateArg(Enum):
    # Common (String, Numeric)
    IS = "is"

    DIFF = "is different with"
    SAME = "is same with"

    FIRST = "is first"
    LAST = "is last"

    COUNT = "is count of"

    # Numeric
    GREATER = "is greater than"
    LESS = "is less than"

    SUM = "is sum of"
    AVG = "is average of"

    GREATEST = "is greatest of "
    LOWEST = "is lowest of "

class WhenArg(Enum):
    IS = "is"
    GREATER = "is greater than"
    LESS = "is less than"