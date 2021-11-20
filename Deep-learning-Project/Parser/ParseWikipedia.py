# -*- coding: utf-8 -*-

# Defintion
import re

from Definition.WikiDef import *
from Definition.WikiRegexDef import *

# Utils
from Utils.DataLoader import *
from Utils.WikiRegexUtil import *

### Method
def RemoveEmptyRowFromTable(tableList:list):
    retTableList = []

    for table in tableList:
        newTable = []
        for row in table:
            if 0 < len(row):
                newTable.append(row)
        retTableList.append(newTable)

    return retTableList

def RemoveWikipediaSyntax(tableList:list):
    retTableList = []

    for table in tableList:
        newTable = []
        for row in table:
            newRow = []
            isToken_th = False
            for col in row:
                if re.search(WIKI_RE.TABLE_START.value, col):
                    newRow = []
                    break
                if re.search(WIKI_RE.TABLE_TITLE.value, col):
                    newRow = []
                    break

                newCol = col.strip()
                newCol = re.sub(WIKI_RE.TABLE_HEAD.value, "<th> ", newCol)
                newCol = re.sub(WIKI_RE.CLASS.value, "", newCol)
                newCol = re.sub(WIKI_RE.BG_COLOR.value, "<bgc>", newCol)

                newCol = re.sub(WIKI_RE.V_ALIGN.value, "", newCol)
                newCol = re.sub(WIKI_RE.ALIGN.value, "", newCol)

                # Ref
                newCol = re.sub(WIKI_RE.REF.value, "", newCol)
                newCol = re.sub(WIKI_RE.REF_2.value, "", newCol)
                newCol = re.sub(WIKI_RE.REF_3.value, "", newCol)
                newCol = re.sub(WIKI_RE.REF_4.value, "", newCol)
                newCol = re.sub(WIKI_RE.REF_5.value, "", newCol)

                # Comment, Pre
                newCol = re.sub(WIKI_RE.COMMENT.value, "", newCol)
                newCol = re.sub(WIKI_RE.PRE.value, "", newCol)

                # Sentence Align
                newCol = re.sub(WIKI_RE.SENT_ALIGN.value, "", newCol)

                # <BR />
                newCol = re.sub(WIKI_RE.BR.value, "", newCol)

                # File & media
                newCol = re.sub(WIKI_RE.FILE.value, "", newCol)
                newCol = re.sub(WIKI_RE.MEDIA.value, "", newCol)

                # Style
                newCol = re.sub(WIKI_RE.STYLE.value, "", newCol)
                newCol = re.sub(WIKI_RE.WIDTH.value, "", newCol)

                # Font shape
                if re.search(WIKI_RE.FONT_SHAPE_5.value, newCol):
                    fontShape = re.search(WIKI_RE.FONT_SHAPE_5.value, newCol).group(0)
                    convertFontShape = fontShape.replace("'''''", "")
                    newCol = newCol.replace(fontShape, convertFontShape)
                if re.search(WIKI_RE.FONT_SHAPE_3.value, newCol):
                    fontShape = re.search(WIKI_RE.FONT_SHAPE_3.value, newCol).group(0)
                    convertFontShape = fontShape.replace("'''", "")
                    newCol = newCol.replace(fontShape, convertFontShape)
                if re.search(WIKI_RE.FONT_SHAPE_2.value, newCol):
                    fontShape = re.search(WIKI_RE.FONT_SHAPE_2.value, newCol).group(0)
                    convertFontShape = fontShape.replace("''", "")
                    newCol = newCol.replace(fontShape, convertFontShape)

                # Special Character
                newCol = re.sub(WIKI_RE.SPECIAL_CHAR.value, "", newCol)
                newCol = re.sub(WIKI_RE.SUBP_SCRIPT.value, "", newCol)

                # Tag
                newCol = re.sub(WIKI_RE.SPAN_TAG.value, "", newCol)
                newCol = re.sub(WIKI_RE.MATH_TAG.value, "", newCol)

                # Redirect
                if re.search(WIKI_RE.REDIRECT.value, newCol):
                    corresStr = re.search(WIKI_RE.REDIRECT.value, newCol).group(0)
                    convertedStr = corresStr.replace("#넘겨주기 [[", "")
                    convertedStr = convertedStr.replace("]]", "")
                    newCol = newCol.replace(corresStr, convertedStr)

                # Free Link
                if re.search(WIKI_RE.FREE_LINK_ALT.value, newCol):
                    newCol = re.sub(WIKI_RE.FREE_LINK_LHS.value, "", newCol)
                    newCol = re.sub(WIKI_RE.FREE_LINK_CLOSED.value, "", newCol)

                if re.search(WIKI_RE.FREE_LINK_BASIC.value, newCol):
                    newCol = re.sub(WIKI_RE.FREE_LINK_OPEN.value, "", newCol)
                    newCol = re.sub(WIKI_RE.FREE_LINK_CLOSED.value, "", newCol)

                # External link
                if re.search(WIKI_RE.EXT_LINK_ALT.value, newCol):
                    corresStr = re.search(WIKI_RE.EXT_LINK_ALT.value, newCol).group(0)
                    convertedStr = re.sub(WIKI_RE.EXT_LINK_ALT_LHS.value, "", corresStr)
                    convertedStr = re.sub(r"\]", "", convertedStr)
                    newCol = newCol.replace(corresStr, convertedStr)

                # Cite
                if re.search(WIKI_RE.CITE.value, newCol):
                    corresStr = re.search(WIKI_RE.CITE.value, newCol).group(0)
                    convertedStr = re.split(WIKI_RE.VERTICAL_BAR.value, corresStr)[1]
                    newCol = newCol.replace(corresStr, convertedStr)

                # Vertical bar
                newCol = re.sub(WIKI_RE.VERTICAL_BAR.value, "", newCol)

                # etc
                newCol = re.sub(r"}}", "", newCol)
                newCol = re.sub(WIKI_RE.DEL_ROW_SPAN.value, "", newCol)
                newCol = re.sub(WIKI_RE.DEL_COL_SPAN.value, "", newCol)
                newCol = re.sub(r"\[\[.+", "", newCol)

                newCol = newCol.strip()

                if isToken_th and -1 == newCol.find("<th>"):
                    tempColList = newCol.split()
                    tempColList.insert(0, "<th>")
                    newCol = ' '.join(tempColList)
                if -1 != newCol.find("<th>"):
                    isToken_th = True

                newRow.append(newCol)

            if 0 < len(newRow):
                newTable.append(newRow)
        retTableList.append(newTable)

    return retTableList

def DivideRowColSpan(tableList:list):
    retTableList = []

    # Col span
    divColSpanTableList = []
    for table in tableList:
        newTable = []
        for rdx, row in enumerate(table):
            newRow = []
            for cdx, col in enumerate(row):
                if re.search(WIKI_RE.COL_SPAN.value, col):
                    corresStr = re.search(WIKI_RE.COL_SPAN.value, col).group(0)
                    splitedStrList = corresStr.split("|")
                    for idx, splitedStr in enumerate(splitedStrList):
                        splitedStrList[idx] = splitedStr.strip()

                    spanCount = splitedStrList[0].replace("colspan=", "").strip()
                    if -1 != spanCount.find("\""):
                        spanCount = int(spanCount.replace("\"", ""))
                    else:
                        spanCount = int(spanCount)

                    spanValue = splitedStrList[1].strip()

                    for sc in range(spanCount):
                        newRow.append("<span> "+ spanValue)
                else:
                    newRow.append(col)
            newTable.append(newRow)
        divColSpanTableList.append(newTable)

    # Row Span
    for table in divColSpanTableList:
        RowSpanPairList = [] # (idx, count, value)
        newTable = []
        for rdx, row in enumerate(table):
            newRow = []
            for cdx, col in enumerate(row):
                for spIdx, spanPair in enumerate(RowSpanPairList):
                    if cdx == spanPair[0]:
                        newRow.append(spanPair[-1])

                        updateCount = spanPair[1]-1
                        if 0 >= updateCount:
                            RowSpanPairList.remove(spanPair)
                        else:
                            RowSpanPairList[spIdx] = (spanPair[0], spanPair[1]-1, spanPair[-1])

                if re.search(WIKI_RE.ROW_SPAN.value, col):
                    corresStr = re.search(WIKI_RE.ROW_SPAN.value, col).group(0)
                    splitedStrList = corresStr.split("| ")

                    spanCount = splitedStrList[0].replace("rowspan=", "").strip()
                    if -1 != spanCount.find("\""):
                        spanCount = int(spanCount.replace("\"", ""))
                    else:
                        spanCount = int(spanCount)

                    spanValue = splitedStrList[1].strip()

                    RowSpanPairList.append((cdx, spanCount-1, "<span> " + spanValue))
                    newRow.append("<span> " + spanValue)
                else:
                    newRow.append(col)
            newTable.append(newRow)
        retTableList.append(newTable)

    return retTableList

def FitTableRowLength(tableList:list):
    retTableList = []

    for table in tableList:
        # Check max Length
        maxRowLen = 0
        for row in table:
            maxRowLen = maxRowLen if maxRowLen > len(row) else len(row)

        # Extend Column
        for row in table:
            if len(row) < maxRowLen:
                diffLen = maxRowLen - len(row)
                for loop in range(diffLen):
                    backVal = row[-1]
                    row.append(backVal)

    retTableList = tableList

    return retTableList

def RemoveNotNeedRows(tableList:list):
    retTableList = []

    for table in tableList:
        newTable = []
        for row in table:
            isExistedData = False
            for col in row:
                # Remove my custom tag
                removeRegCol = re.sub(r"<[^>]+>", "", col).strip()
                if 1 <= len(removeRegCol):
                    isExistedData = True
                    break
            if isExistedData:
                newTable.append(row)
        retTableList.append(newTable)

    return retTableList

def ParseWikipedia(wikiPage:WikiPage):
    wikiTable = WikiTable(title=wikiPage.title, tableList=[])

    # Parse table from text
    tableList = ParseWikiTableRegex(wikiPage.text)

    # Divide rows and cols by Table Syntax
    tableList = DivideTableRowColBySyntax(tableList)
    tableList = RemoveEmptyRowFromTable(tableList)

    # Divide RowSpan and ColSpan
    tableList = DivideRowColSpan(tableList)

    # Remove Wikipeida Syntax
    tableList = RemoveWikipediaSyntax(tableList)

    # Fit Row length
    tableList = FitTableRowLength(tableList)

    # Remove Not Need Row
    tableList = RemoveNotNeedRows(tableList)

    wikiTable.tableList = wikiPage.title
    wikiTable.tableList = tableList
    return wikiTable

if "__main__" == __name__:
    # Parse Wikipedia
    for pageData in ReadWikiDataset("../Dataset/kor-wiki/kowiki-latest-pages-articles-multistream.xml"):
        wikipage = WikiPage(title=pageData[0], text=pageData[1])

        wikiTable = ParseWikipedia(wikipage)