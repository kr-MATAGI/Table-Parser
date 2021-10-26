from dataclasses import dataclass

@dataclass
class TottoTableCell:
    value: str = ""
    colSpan: int = -1
    rowSpan: int = -1

@dataclass
class TottoSentences:
    origin: str = ""
    afterDeletion: str = ""
    afterAmbiguity: str = ""
    final: str = ""

@dataclass
class TottoSection:
    table = list() # TottoTableCell
    highlightInfo = list() # list( pair(a, b) )
    sentences = list() # Elem: TottoSentences