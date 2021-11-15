# Regex
from Definition.WikiRegexDef import *

# Built-in
import re

def ParseWikiTableRegex(pageText:str):
    retTableList = []

    lineText = pageText.split("\n")

    table = []
    isTableLine = False
    for line in lineText:
        # Table Start
        if re.search(WIKI_RE.TABLE_START.value, line):
            isTableLine = True

        # Table Contents
        if isTableLine:
            table.append(line)

        # Table End
        if re.search(WIKI_RE.TABLE_END.value, line):
            isTableLine = False
            retTableList.append(table)
            table = []

    return retTableList



def DivideTableRowColBySyntax(tableList=list):
    retTableList = []

    for table in tableList:
        # Rows
        newTable = []
        for element in table:
            if re.search(WIKI_RE.TABLE_START.value, element):
                newTable.append(element)

            elif re.search(WIKI_RE.TABLE_ROW.value, element):
                continue

            elif re.search(WIKI_RE.TABLE_END.value, element):
                retTableList.append(newTable)
                newTable = []

            else:
                newTable.append(element)

        # Cols
        newTable = []
        for tdx, table in enumerate(retTableList):
            for row in table:
                newRow = re.split(WIKI_RE.TABLE_COL.value, row)
                newTable.append(newRow)
            retTableList[tdx] = newTable

    return retTableList