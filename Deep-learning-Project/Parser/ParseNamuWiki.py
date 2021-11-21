# Built-in
import sys
import re

# Utils
from Utils.DataLoader import *
from Utils.HeadExtractor import *

# Def
from Definition.WikiDef import *


##### Method #####
def ConvertTableColSpanToken(rowList):
    retRowList = []
    for row in rowList:
        if re.search(NAMU_RE.OLD_COL_SPAN.value, row):
            newRow = row
            colSpanList = re.findall(NAMU_RE.OLD_COL_SPAN.value, row)

            for colSpan in colSpanList:
                spanCnt = len(re.findall(NAMU_RE.ROW_SPLIT.value, colSpan))
                convStr = '||<-%s>' % spanCnt
                newRow = row.replace(colSpan, convStr)

            retRowList.append(newRow)
        else:
            retRowList.append(row)

    return retRowList

def ParseTableFromText(docText):
    retTableList = []

    re_checkRow = re.compile(NAMU_RE.ROW_SPLIT.value)
    for text in docText:
        splitList = text.split('\n')

        # Get Table
        tableRows = []
        for element in splitList:
            if re_checkRow.search(element):
                tableRows.append(element)
            else:
                if 0 < len(tableRows):
                    # Remove colspan r'[||]{2,}'
                    newRows = ConvertTableColSpanToken(tableRows.copy())

                    retTableList.append(newRows)
                    tableRows.clear()

    return retTableList

def ModifyHTMLTags(tableList):
    retTableList = []

    for table in tableList:
        newTable = []
        for idx, row in enumerate(table):
            newRow = row

            # Convert Tags
            newRow = re.sub(NAMU_RE.TEXT_FORM.value, NAMU_RE.CONV_TEXT_FORM.value, newRow)
            newRow = re.sub(NAMU_RE.SUB_SCRIPT.value, NAMU_RE.CONV_SUB_SCRIPT.value, newRow)
            newRow = re.sub(NAMU_RE.TEXT_COLOR.value, NAMU_RE.CONV_TEXT_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.BG_COLOR.value, NAMU_RE.CONV_BG_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.TBG_COLOR.value, NAMU_RE.CONV_TBG_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.COL_BG_COLOR.value, NAMU_RE.CONV_COL_BG_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.ROW_BG_COLOR.value, NAMU_RE.CONV_ROW_BG_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.CELL_COLOR.value, NAMU_RE.CONV_CELL_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.COL_COLOR.value, NAMU_RE.CONV_COL_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.ROW_COLOR.value, NAMU_RE.CONV_ROW_COLOR.value, newRow)

            # Remove Tags
            newRow = re.sub(NAMU_RE.LITERAL.value, '', newRow)
            newRow = re.sub(NAMU_RE.TEXT_SIZE_FRONT.value, '', newRow)
            newRow = re.sub(NAMU_RE.PARENT_ARTICLE_LINK.value, '', newRow)
            newRow = re.sub(NAMU_RE.IMAGE_FILE.value, '', newRow)  # Check Order
            newRow = re.sub(NAMU_RE.EXTERNAL_LINK.value, '', newRow)  # Check Order
            newRow = re.sub(NAMU_RE.YOUTUBE.value, '', newRow)
            newRow = re.sub(NAMU_RE.KAKAO_TV.value, '', newRow)
            newRow = re.sub(NAMU_RE.NICO_VIDEO.value, '', newRow)
            newRow = re.sub(NAMU_RE.NAVER_VIDEO.value, '', newRow)
            newRow = re.sub(NAMU_RE.HTML_VIDEO.value, '', newRow)
            newRow = re.sub(NAMU_RE.ADD_LIST.value, '', newRow)
            newRow = re.sub(NAMU_RE.FOOT_NOTE.value, '', newRow)
            newRow = re.sub(NAMU_RE.AGE_FORM.value, '', newRow)
            newRow = re.sub(NAMU_RE.DATE_TIME_FORM.value, '', newRow)
            newRow = re.sub(NAMU_RE.DDAY_FORM.value, '', newRow)
            newRow = re.sub(NAMU_RE.BR_TAG.value, '', newRow)
            newRow = re.sub(NAMU_RE.TABLE_ALIGN.value, '', newRow)
            newRow = re.sub(NAMU_RE.TABLE_WIDTH.value, '', newRow)
            newRow = re.sub(NAMU_RE.TABLE_BORDER_COLOR.value, '', newRow)
            newRow = re.sub(NAMU_RE.CELL_SIZE.value, '', newRow)
            newRow = re.sub(NAMU_RE.CELL_H_ALIGN.value, '', newRow)
            newRow = re.sub(NAMU_RE.CELL_V_ALIGN.value, '', newRow)
            newRow = re.sub(NAMU_RE.FOLDING.value, '', newRow)
            newRow = re.sub(NAMU_RE.TRIPLE_BARKET_BACK.value, '', newRow)

            # Exception
            newRow = re.sub(NAMU_RE.OLD_BG_COLOR.value, NAMU_RE.CONV_BG_COLOR.value, newRow)
            newRow = re.sub(NAMU_RE.LINK_BACK.value, '', newRow)
            newRow = re.sub(NAMU_RE.ETC_FILE.value, '', newRow)
            newRow = re.sub(NAMU_RE.ETC_HTTP.value, '', newRow)
            newRow = re.sub(NAMU_RE.ETC_BARKET.value, '', newRow)

            # Ruby
            if re.search(NAMU_RE.MACRO_RUBY.value, newRow):
                rubyList = re.findall(NAMU_RE.MACRO_RUBY.value, newRow)

                for rubyStr in rubyList:
                    delRubyStr = re.sub(NAMU_RE.RUBY_FRONT.value, '', rubyStr)
                    delRubyStr = re.sub(NAMU_RE.RUBY_BACK.value, '', delRubyStr)
                    newRow = newRow.replace(rubyStr, delRubyStr)
            newTable.append(newRow)
        retTableList.append(newTable)

    return retTableList

## Inner method of PreprocessingTable()
def SplitRowAndColByToken(table):
    retTable = []

    for row in table:
        newRow = []
        spliteRowList = re.split(NAMU_RE.ROW_SPLIT.value, row)[1:-1]

        for col in spliteRowList:
            newRow.append(col)
        retTable.append(newRow)

    return retTable

def SplitColSpan(table):
    retTable = []

    for row in table:
        newRow = []

        for col in row:
            if re.search(NAMU_RE.NEW_COL_SPAN.value, col):
                spanCnt = int(re.search(NAMU_RE.NEW_COL_SPAN.value, col).group(0).replace('<-', '').replace('>', ''))
                newCol = re.sub(NAMU_RE.NEW_COL_SPAN.value, '<cs>', col)
                for spIdx in range(spanCnt):
                    newRow.append(newCol)
            else:
                newRow.append(col)
        retTable.append(newRow)

    return retTable


def SplitRowSpan(table):
    retTable = []

    spanInfoList = []  # (colIdx, str, spanCnt)
    for row in table:
        newRow = []

        for cIdx, col in enumerate(row):
            if re.search(NAMU_RE.NEW_ROW_SPAN.value, col):
                spanCnt = int(re.search(NAMU_RE.NEW_ROW_SPAN.value, col).group(0).replace("<|", '').replace(">", ''))
                newCol = re.sub(NAMU_RE.NEW_ROW_SPAN.value, '<rs>', col)
                spanInfo = (cIdx, newCol, spanCnt - 1)
                spanInfoList.append(spanInfo)

                newRow.append(newCol)
            else:
                for infoIdx, infoData in enumerate(spanInfoList):
                    if cIdx == infoData[0]:
                        newRow.append(infoData[1])
                        if 0 >= infoData[2] - 1:
                            spanInfoList.remove(infoData)
                        else:
                            newInfo = (infoData[0], infoData[1], infoData[2] - 1)
                            spanInfoList[infoIdx] = newInfo
                newRow.append(col)
        retTable.append(newRow)

    return retTable

def RemoveEmptyRows(table):
    retTable = []

    for row in table:
        if 0 < len(row):
            retTable.append(row)

    return retTable

def SliceTableLength(table):
    retTable = []

    # Check Table Min Length
    minLen = sys.maxsize
    for row in table:
        minLen = min(minLen, len(row))

    # Slice row of table
    for row in table:
        newRow = row[:minLen]
        retTable.append(newRow)

    return retTable

def PreprocessingTable(tableList):
    retTableList = []

    for table in tableList:
        newTable = SplitRowAndColByToken(table)
        newTable = SplitColSpan(newTable)
        newTable = SplitRowSpan(newTable)
        newTable = RemoveEmptyRows(newTable)
        newTable = SliceTableLength(newTable)

        if 1 < len(newTable):
            retTableList.append(newTable)

    return retTableList

## Inner method of RemoveDecoTables
def CheckRowIsEmptyCells(table):
    retValue = True

    for row in table:
        isEmpty = True
        for col in row:
            if 0 < len(str(col).lstrip()):
                isEmpty = False
                break

        if isEmpty:
            retValue = False
            break

    return retValue

def CheckEmptyCellsRatio(table, ratio=0.3):
    retValue = True

    emptyCellCnt = 0
    totalCellCnt = 0
    for row in table:
        for col in row:
            totalCellCnt += 1

            stripCell = str(col).lstrip()
            if 0 >= len(stripCell):
                emptyCellCnt += 1

    if ratio <= (emptyCellCnt / totalCellCnt):
        retValue = False

    return retValue

def RemoveDecoTables(tableList):
    retTableList = []

    for table in tableList:
        # Check Method 1
        isMT = CheckRowIsEmptyCells(table)
        if not isMT:
            continue

        # Check Method 2
        isMT = CheckEmptyCellsRatio(table, ratio=0.3)

        if isMT:
            retTableList.append(table)

    return retTableList

def ClassifyNormalTableOrInfoBox(tableList):
    normalTableList = []
    infoBoxList = []

    for table in tableList:
        colLen = len(table[0])
        if 3 <= colLen:
            normalTableList.append(table)
        else:
            infoBoxList.append(table)

    return normalTableList, infoBoxList

if "__main__" == __name__:
    # Class Instances
    headExtractor = HeadExtractor()

    # Parsing
    docCnt = 0
    tableCnt = 0
    for doc in ReadNamuwikiDataset("../Dataset/namu-wiki/namuwiki_20210301.json"):
        docCnt += 1

        if 0 == (docCnt % 1000):
            print("Processing...", docCnt, ":", doc[DOC_TITLE])

        wikiTable = WikiTable(title="", tableList=[])
        wikiTable.title = doc[DOC_TITLE]

        # Preprocess tables
        tableList = ParseTableFromText(doc[DOC_TEXT])
        tableList = ModifyHTMLTags(tableList)
        tableList = PreprocessingTable(tableList)
        tableList, infoBoxList = ClassifyNormalTableOrInfoBox(tableList)

        # Remove trash tables
        tableList = headExtractor.RemoveNoExistedTableHeaderTalbe(tableList)
        tableList = RemoveDecoTables(tableList)

        if 0 < len(tableList):
            # Document: 867,024 - Table: 1432250 -> 2,130,063
            #tableList = headExtractor.IsHeadLeftColumnOnWikiTable(tableList)
            tableCnt += len(tableList)
        wikiTable.tableList = tableList

    # Print doc/table counts
    print("Document Counts:", docCnt)
    print("table Counts:", tableCnt)