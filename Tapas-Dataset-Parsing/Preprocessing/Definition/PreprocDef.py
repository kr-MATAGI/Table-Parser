from dataclasses import dataclass
from enum import Enum

@dataclass
class QueryRelation:
    table2D = list()
    labelTags = list() # element is tuple()
    query: str = "" # Question
    answer = list()

class QueryType(Enum):
    NONE = 0
    COUNT = 1
    MAX = 2
    MIN = 3
    SUM = 4
    AVG = 5