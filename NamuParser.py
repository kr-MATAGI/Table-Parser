
import re
import sys

import ijson

## Ref : https://namu.wiki/w/%EB%82%98%EB%AC%B4%EC%9C%84%ED%82%A4:%EB%AC%B8%EB%B2%95%20%EB%8F%84%EC%9B%80%EB%A7%90

## Definition
# Dict Def
DOC_TITLE = 'title'
DOC_TEXT = 'text'

## regex
# Table Token
RE_CHECK_ROW = r'^\|\|'
RE_SPLIT_TOKEN = r'\|\|'

RE_OLD_COL_SPAN = r'\|\|{2,}'
RE_NEW_COL_SPAN = r'<-\d>'
RE_NEW_ROW_SPAN = r'<\|\d>'

RE_EMPTY_CELL = r'[\|\|]+'

# convert
RE_BG_COLOR = r'<bgcolor=#[\w]+>|<bgcolor=[\w]+>{1}' # bgcolor
CONV_BG_COLOR = '<bg>'

RE_BR_TAG = r'\[BR\]'
CONV_BR_TAG = '<br>'

RE_TEXT_SHAPE = r"\'\'\'|\'\'|\'\'\' \'\'" # ''', '', ''' '', __
CONV_TEXT_SHAPE = "\'\'\'"

RE_ROW_BG_COLOR = r'<rowbgcolor=.+>'
CONV_ROW_BG_COLOR = '<rbg>'

RE_TABLE_BG_COLOR = r'<tablebgcolor=#[\w]+>|<table bgcolor=#[\w]+>'
CONV_TABLE_BG_COLOR = r'<tbg>'

# remove
RE_TABLE_SIZE = r'<tablewidth=[\w]+>|<tablealign=[\w]+>|<table width=[\w]+>|<table align=\'[\w]+\'>'
RE_TABLE_BORDER = r'<tablebordercolor=.+>|<table bordercolor=.+>'

RE_CELL_SIZE = r'<width=.+>|<height=.+>'

RE_TEXT_COLOR = r'{{{#[\w]+ |<#[\w]+>' # Plz check order
RE_TEXT_SIZE = r'{{{\+[\d]|}}}'
RE_TEXT_ALIGN = r'<\(>|<\:>|<\)>'

RE_FILE_LINK = r'\[\[파일:[^\]]+\]\]'
RE_VIDEO_LINK = r'\[youtube\(.+\)\]|\[kakaotv\(.+\)\]|\[nicovideo\(.+\)\]|\{\{\{\#!html.+\}\}\}'
RE_HTML_LINK = r'\[\[http.+\]\]'

RE_FOOT_NOTE = r'\[\*.+\]'

# macro - ruby
RE_MACRO_RUBY = r'\[ruby\([\w]+, ruby\=[\w]+\)\]'
RE_RUBY_FRONT = r'\[ruby\([\w]+, '

class NamuWikiParser:
    ### VAR ###
    __srcPath = ''

    ### INIT ###
    '''
        Initialize
        @Param
            jsonPath - wiki json path
    '''
    def __init__(self, jsonPath):
        self.__srcPath = jsonPath
        print('Init PreProcesser - JSON Path: ', self.__srcPath)

    ### PRIVATE ###
    def __ConvertTableColSpanToken(self, rowList):
        retRow = rowList

        for rIdx, row in enumerate(rowList):
            if None != re.search(RE_OLD_COL_SPAN, row):
                colSpanList = re.findall(RE_OLD_COL_SPAN, row)

                for colSpan in colSpanList:
                    spanCnt = len(re.findall(RE_SPLIT_TOKEN, colSpan)) - 1
                    convStr = '||<-%s>' % spanCnt
                    row = row.replace(colSpan, convStr)

                rowList[rIdx] = row

        return retRow

    ### PUBLIC ###
    '''
        Parse wiki json using ijson
    '''
    def ParsingJSON(self):
        with open(self.__srcPath, 'r', encoding='utf-8') as srcFile:
                parser = ijson.parse(srcFile)
                
                retValue = {}
                isNewKey = False
                for prefix, event, value in parser:
                    if ('item', 'start_map') == (prefix, event): isNewKey = True
                    elif True == prefix.endswith('.title') and True == isNewKey: 
                        retValue[DOC_TITLE] = value
                        retValue[DOC_TEXT] = []
                    elif True == prefix.endswith('.text'):
                        retValue[DOC_TEXT].append(value)
                    elif ('item', 'end_map') == (prefix, event):
                        yield retValue
                        isNewKey = False
                        retValue.clear()
    
    '''
        @Note
            All docText's len() is 1
        @Param
            docText - item.text, type(list)
    '''
    def ParseTableFromText(self, docText):
        retTableList = []

        re_checkRow = re.compile(RE_CHECK_ROW)
        for text in docText:
            splitList = text.split('\n')
            
            # Get Table
            tableRows = []
            for element in splitList:
                if None != re_checkRow.match(element): tableRows.append(element)
                else:
                    if 0 < len(tableRows):
                        # Remove colspan r'[||]{2,}'
                        newRows = self.__ConvertTableColSpanToken(tableRows.copy())

                        retTableList.append(newRows)
                        tableRows.clear()
        
        return retTableList

    '''
        @Note
            Convert HTML Tags
            e.g.
                
            and Remove Others
    '''
    def ModifyHTMLTags(self, tableList):
        for table in tableList:
            for idx, row in enumerate(table):
                newRow = row
                
                # Remove Tags
                newRow = re.sub(RE_TABLE_SIZE, '', newRow) # Remove table's tag
                newRow = re.sub(RE_TABLE_BORDER, '', newRow) # Remove table's tag
                newRow = re.sub(RE_TEXT_ALIGN, '', newRow) # Remove text align' tag
                newRow = re.sub(RE_FILE_LINK, '', newRow) # Remove [[파일:*.*]]
                newRow = re.sub(RE_VIDEO_LINK, '', newRow) # Remove youtube link
                newRow = re.sub(RE_HTML_LINK, '', newRow) # Remove external html link
                newRow = re.sub(RE_CELL_SIZE, '', newRow) # Remove cell's width, height
                newRow = re.sub(RE_TEXT_COLOR, '', newRow) # Remove {{{#[\w]+}}}, check piority with text size
                newRow = re.sub(RE_TEXT_SIZE, '', newRow) # Remove {{{, }}}
                newRow = re.sub(RE_FOOT_NOTE, '', newRow) # Remove [* ]

                # Convert Tags
                newRow = re.sub(RE_TABLE_BG_COLOR, CONV_TABLE_BG_COLOR, newRow)
                newRow = re.sub(RE_BG_COLOR, CONV_BG_COLOR, newRow)
                newRow = re.sub(RE_BR_TAG, CONV_BR_TAG, newRow)
                newRow = re.sub(RE_TEXT_SHAPE, CONV_TEXT_SHAPE, newRow)
                newRow = re.sub(RE_ROW_BG_COLOR, CONV_ROW_BG_COLOR, newRow)

                # Ruby
                if not re.search(RE_MACRO_RUBY, newRow):
                    rubyList = re.findall(RE_MACRO_RUBY, newRow)
                    
                    for rubyStr in rubyList:
                        delRubyStr = re.sub(RE_RUBY_FRONT, '', rubyStr)
                        delRubyStr = delRubyStr.replace('ruby=', '')
                        delRubyStr = delRubyStr.replace(')]', '')
                        
                        newRow = newRow.replace(rubyStr, delRubyStr)

                table[idx] = newRow

    '''
        Split Col Span
    '''
    def SplitColSpan(self, table):
        for rIdx, row in enumerate(table):
            if None != re.search(RE_NEW_COL_SPAN, row):
                colList = re.split(RE_SPLIT_TOKEN, row)[1:-1]

                newColList = []
                for col in colList:
                    newCol = col
                    spanCnt = 0

                    if None != re.search(RE_NEW_COL_SPAN, col):
                        spanCnt = re.findall(RE_NEW_COL_SPAN, col)[0]
                        spanCnt = int(spanCnt.replace('<-', '').replace('>', '')) - 1

                        newCol = re.sub(RE_NEW_COL_SPAN, '<cs>', col)
                    newColList.append(newCol)
                    for cnt in range(spanCnt): newColList.append(newCol)
                
                # Re-Merge
                newRow = '||'
                for col in newColList: newRow += (col + '||')
                table[rIdx] = newRow

        return table


    '''
        Split Row Span
    '''
    def SplitRowSpan(self, table):
        spanTripList = [] # (colIdx, colText, spanCnt)
        for rIdx, row in enumerate(table):
            if None != re.search(RE_NEW_ROW_SPAN, row):
                rowList = re.split(RE_SPLIT_TOKEN, row)[1:-1]
                
                newColList = []
                for cIdx, col in enumerate(rowList):
                    newCol = col

                    if None != re.search(RE_NEW_ROW_SPAN, col):
                        spanCnt = re.findall(RE_NEW_ROW_SPAN, col)[0]
                        spanCnt = int(spanCnt.replace('<|', '').replace('>', '')) - 1
                        
                        newCol = re.sub(RE_NEW_ROW_SPAN, '<rs>', col)
                        spanTripList.append((cIdx, newCol, spanCnt))

                    newColList.append(newCol)
                
                # Re-Merge
                newRow = '||'
                for col in newColList: newRow += (col + '||')
                table[rIdx] = newRow
            else:
                if 0 < len(spanTripList):
                    rowList = re.split(RE_SPLIT_TOKEN, row)[1:-1]

                    newColList = []
                    for cIdx, col in enumerate(rowList):
                        for trIdx, triPair in enumerate(spanTripList):
                            if triPair[0] == cIdx:
                                newColList.append(triPair[1])

                                newSpanCnt = int(triPair[2]) - 1
                                newTriPair = (triPair[0], triPair[1], newSpanCnt)
                                if 0 >= newSpanCnt: spanTripList.remove(triPair)
                                else: spanTripList[trIdx] = newTriPair
                        newColList.append(col)
            
                    # Re-Merge
                    newRow = '||'
                    for col in newColList: newRow += (col + '||')
                    table[rIdx] = newRow

        return table
        
    '''
        Remove Empty Cells
    '''
    def RemoveEmptyCells(self, table):
        newTable = []
        for row in table:
            rowSplitList = re.split(RE_EMPTY_CELL, row.replace(' ', ''))
            if 2 < len(rowSplitList): newTable.append(row)
        table = newTable

        return table

    '''
        Slice Table Length with min length
    '''
    def SliceTableLength(self, table):
        newTable = []

        # Check Min Length
        minLen = sys.maxsize
        for row in table:
            currLen = len(re.split(RE_SPLIT_TOKEN, row)[1:-1])
            minLen = minLen if minLen < currLen else currLen

        # Slice Over Length
        for row in table:
            spList = re.split(RE_SPLIT_TOKEN, row)[1:-1]
            newRow = spList[:minLen]
            newTable.append(newRow)

        return newTable

    '''
        Classify Normal Table and Info Box
        @Param
            Origin Table List (Source Table)
        @Return
            normalTableList, infoBoxList
    '''
    def ClassifyNormalTableOrInfoBox(self, tableList):
        normalTableList = []
        infoBoxList = []

        for table in tableList:
            colLen = len(table[0])
            if 3 <= colLen:
                normalTableList.append(table)
            else:
                infoBoxList.append(table)

        return normalTableList, infoBoxList