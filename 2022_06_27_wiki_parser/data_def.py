from dataclasses import dataclass, field
from typing import List

#=============================================
@dataclass
class SPLIT_PARAG:
    sym_cnt: int = 0
    title: str = ""
    text_list: List[str] = field(default_factory=list)

#=============================================
@dataclass
class TT_Pair: # text and table pair
    title: str = "" # paragraph title
    text: List[str] = field(default_factory=list)
    table: List[List[str]] = field(default_factory=list)

@dataclass
class Wiki_Page:
    title: str = "" # wiki page title
    only_text_list: List[str] = field(default_factory=list)
    text_table_pair: List[TT_Pair] = field(default_factory=list)