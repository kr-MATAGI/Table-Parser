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

    # Rows
    divideRowTableList = []
    for table in tableList:
        newTable = []
        for element in table:
            if re.search(WIKI_RE.TABLE_START.value, element):
                newTable.append(element)

            elif re.search(WIKI_RE.TABLE_ROW.value, element):
                newTable.append(element)

            elif re.search(WIKI_RE.TABLE_END.value, element):
                divideRowTableList.append(newTable)
                newTable = []

            else:
                newTable.append(element)

    # Cols
    for table in divideRowTableList:

        newTable = []
        newRow = []
        for rdx, row in enumerate(table):
            if re.search(WIKI_RE.TABLE_DOUBLE_COL.value, row):
                splitRow = re.split(WIKI_RE.TABLE_DOUBLE_COL.value, row)
                if 0 < len(splitRow):
                    newTable.append(splitRow)

            elif re.search(WIKI_RE.TABLE_ROW.value, row):
                newTable.append(newRow)
                newRow = []

            elif re.search(WIKI_RE.TABLE_NEWLINE_COL.value, row):
                if 0 < len(row):
                    newRow.append(row)

        if 0 != len(newRow):
            newTable.append(newRow)
        retTableList.append(newTable)

    return retTableList