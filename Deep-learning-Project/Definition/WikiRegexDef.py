from enum import Enum

class WIKI_RE(Enum):
    TABLE_START = r"{\|"
    TABLE_ROW = r"\|-"
    TABLE_COL = r"\|\|"
    TABLE_END = r"\|}"