from dataclasses import dataclass

@dataclass
class WikiPage:
    title:str
    text:str

@dataclass
class WikiTable:
    title:str
    tableList:list