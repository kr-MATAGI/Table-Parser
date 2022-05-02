from dataclasses import dataclass, field
from typing import List


@dataclass
class TABLE_REL:
    doc_title: str = ""
    parag_idx: int = -1
    table: List[List[str]] = field(default_factory=list)
    sent_list: List[str] = field(default_factory=list)