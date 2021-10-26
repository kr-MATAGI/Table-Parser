from dataclasses import dataclass

@dataclass
class QueryRelation:
    table2D = list()
    labelTags = list() # element is tuple()
    query: str = "" # Question
    answer = list()