# Defintion
from Definition.WikiDef import *

# Utils
from Utils.DataLoader import *
from Utils.WikiRegexUtil import *

### Method
def ParseWikipedia(wikiPage:WikiPage):
    wikiTable = WikiTable(title=wikiPage.title, tableList=[])

    # Parse table from text
    tableList = ParseWikiTableRegex(wikiPage.text)

    # Divide rows and cols by Table Syntax
    tableList = DivideTableRowColBySyntax(tableList)



    return wikiTable

if "__main__" == __name__:
    # Parse Wikipedia
    for pageData in ReadWikiDataset("../Dataset/kor-wiki/test.xml"):
        wikipage = WikiPage(title=pageData[0], text=pageData[1])

        wikiTable = ParseWikipedia(wikipage)