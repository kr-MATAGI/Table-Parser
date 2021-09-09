
import re
import sys

import ijson

## Ref : https://namu.wiki/w/%EB%82%98%EB%AC%B4%EC%9C%84%ED%82%A4:%EB%AC%B8%EB%B2%95%20%EB%8F%84%EC%9B%80%EB%A7%90

## Definition
# Dict Def
DOC_TITLE = 'title'
DOC_TEXT = 'text'

### regex
## Table Token
RE_ROW_SPLIT = r'\|\|'

RE_OLD_COL_SPAN = r'\|\|{2,}'
RE_NEW_COL_SPAN = r'<-\d+>'
RE_NEW_ROW_SPAN = r'<\|\d+>'

RE_EMPTY_CELL = r'[\|\|]+'

## Custom Attribute Token
RE_CUSTOM_ATTR = r'<\w+>'

## Convert
# 2.1
RE_TEXT_FORM = r"(''' '')|('' ''')|(''')|('')|__|~~|--" # Check Priority (''' '', ''')
CONV_TEXT_FORM = "<tf>" # text form

RE_SUB_SCRIPT = r'\^\^|,,'
CONV_SUB_SCRIPT = ' ' # white space

# 2.3
RE_TEXT_COLOR = r'\{\{\{#\w+(,\s?#\w+)?\s?'
CONV_TEXT_COLOR = '<tc>' # text color

# 13.3.1
RE_BG_COLOR = r'<bgcolor=#?\w+(,\s?#?\w+)?>'
CONV_BG_COLOR = '<bg>'

RE_TBG_COLOR = r'<(tablecolor|tablebgcolor)=#?\w+(,\s?#?\w+)?>'
CONV_TBG_COLOR = '<tbg>'

RE_COL_BG_COLOR = r'<colbgcolor=#?\w+(,\s?#?\w+)?>'
CONV_COL_BG_COLOR = '<cbg>'

RE_ROW_BG_COLOR = r'<rowbgcolor=#?\w+(,\s?#?\w+)?>'
CONV_ROW_BG_COLOR = '<rbg>'

RE_CELL_COLOR = r'<color=#?\w+(,\s?#?\w+)?>'
CONV_CELL_COLOR = '<celc>'

RE_COL_COLOR = r'<colcolor=#?\w+(,\s?#?\w+)?>'
CONV_COL_COLOR = '<colc>'

RE_ROW_COLOR = r'<rowcolor=#?\w+(,\s?#?\w+)?>'
CONV_ROW_COLOR = '<rowc>'

## Remove
# 2.1
RE_LITERAL = r'\{\{\{\[\[|\]\]\}\}\}'

# 2.2
RE_TEXT_SIZE_FRONT = r'\{\{\{\+\d ' # text size input's front

# 3
RE_PARENT_ARTICLE_LINK = r'\[\[\.\./\]\]'
# RE_CHILD_ARTICLIE_LINK = r'\[\[[/[\w]+]+'
RE_EXTERNAL_LINK = r'\[\[https?://.+(\..+)?(\|.+)?\]\]'

# 5
RE_IMAGE_FILE = r'\[\[파일:.+\|?(&?(width|height|align|bgcolor)=(left|center|right|(\d+%?)|(#\w+)))*\]\]'

# 6
RE_YOUTUBE = r'\[youtube\(\w+(,\s?(start|width|height)=\w+%?)*\)\]|' \
             r'\[include\(틀:.+ (left|center|right)?\s?url=\w+\)(,\s?(start|width|height)=\w+%?)*\]'
RE_KAKAO_TV = r'\[kakaotv\(\w+(,\s?(start|width|height)=\w+%?)*\)\]'
RE_NICO_VIDEO = r'\[nicovideo\(\w+(,\s?(start|width|height)=\w+%?)*\)\]'
RE_NAVER_VIDEO = r'\[include\(틀:(navertv|navervid){1}(,\s?(i=\w+|vid=\w+,\s?outkey=\w+)+)+(,\s?(start|width|height)=\w+%?)*\)\]'
# 6 - deep syntax
RE_HTML_VIDEO = r'\{\{\{#!html <video src=("|\').+("|\')></video>\}\}\}|' \
                r'\{\{\{#!html .+\}\}\}'

# 8
RE_ADD_LIST = r'v+(\w*\.|\*)?v*'

# 9
RE_FOOT_NOTE = r'\[\*.+\]'

# 12.2
RE_AGE_FORM = r'\[age\(\d{4}-\d{1,2}-\d{1,2}\)\]'
RE_DATE_TIME_FORM = r'\[date\]|\[datetime\]'
RE_DDAY_FORM = r'\[dday\(\d{4}-\d{1,2}-\d{1,2}\)\]'

# 12.4
RE_BR_TAG = r'\[br\]'
RE_CLEARFIX = r'\[clearfix\]'

# 13.3.1
RE_TABLE_ALIGN = r'<table\s?align=\'?(left|center|right)\'?>'
RE_TABLE_WIDTH = r'<table\s?width=\d+(px|%)?>'

RE_TABLE_BORDER_COLOR = r'<table\s?bordercolor=#\w+>'

RE_CELL_SIZE = r'<(width|height)=\d+(px|%)?>'

RE_CELL_H_ALIGN = r'(<\(>)|(<:>)|(<\)>)'
RE_CELL_V_ALIGN = r'(<\^\|\d+>)|(<v\|\d+>)' # (<\|\d+>) ? -> row Span

# 14
RE_FOLDING = r'\{\{\{#!folding\s?\[[^\[.]+\]'

# macro - ruby
RE_MACRO_RUBY = r'\[ruby\(\w+, ruby=\w+\)\]'
RE_RUBY_FRONT = r'\[ruby\('
RE_RUBY_BACK = r',\s?ruby=.+\)\]'

# tirple barket }}}
RE_TRIPLE_BARKET_BACK = r'\}\}\}'

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
            if not re.search(RE_OLD_COL_SPAN, row):
                colSpanList = re.findall(RE_OLD_COL_SPAN, row)

                for colSpan in colSpanList:
                    spanCnt = len(re.findall(RE_ROW_SPLIT, colSpan)) - 1
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

        re_checkRow = re.compile(RE_ROW_SPLIT)
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

                # Convert Tags
                newRow = re.sub(RE_TEXT_FORM, CONV_TEXT_FORM, newRow)
                newRow = re.sub(RE_SUB_SCRIPT, CONV_SUB_SCRIPT, newRow)
                newRow = re.sub(RE_TEXT_COLOR, CONV_TEXT_COLOR, newRow)
                newRow = re.sub(RE_BG_COLOR, CONV_BG_COLOR, newRow)
                newRow = re.sub(RE_TBG_COLOR, CONV_TBG_COLOR, newRow)
                newRow = re.sub(RE_COL_BG_COLOR, CONV_COL_BG_COLOR, newRow)
                newRow = re.sub(RE_ROW_BG_COLOR, CONV_ROW_BG_COLOR, newRow)
                newRow = re.sub(RE_CELL_COLOR, CONV_CELL_COLOR, newRow)
                newRow = re.sub(RE_COL_COLOR, CONV_COL_COLOR, newRow)
                newRow = re.sub(RE_ROW_COLOR, CONV_ROW_COLOR, newRow)

                # Remove Tags
                newRow = re.sub(RE_LITERAL, '', newRow)
                newRow = re.sub(RE_TEXT_SIZE_FRONT, '', newRow)
                newRow = re.sub(RE_PARENT_ARTICLE_LINK, '', newRow)
                newRow = re.sub(RE_EXTERNAL_LINK, '', newRow)
                newRow = re.sub(RE_IMAGE_FILE, '', newRow)
                newRow = re.sub(RE_YOUTUBE, '', newRow)
                newRow = re.sub(RE_KAKAO_TV, '', newRow)
                newRow = re.sub(RE_NICO_VIDEO, '', newRow)
                newRow = re.sub(RE_NAVER_VIDEO, '', newRow)
                newRow = re.sub(RE_HTML_VIDEO, '', newRow)
                newRow = re.sub(RE_ADD_LIST, '', newRow)
                newRow = re.sub(RE_FOOT_NOTE, '', newRow)
                newRow = re.sub(RE_AGE_FORM, '', newRow)
                newRow = re.sub(RE_DATE_TIME_FORM, '', newRow)
                newRow = re.sub(RE_DDAY_FORM, '', newRow)
                newRow = re.sub(RE_BR_TAG, '', newRow)
                newRow = re.sub(RE_TABLE_ALIGN, '', newRow)
                newRow = re.sub(RE_TABLE_WIDTH, '', newRow)
                newRow = re.sub(RE_TABLE_BORDER_COLOR, '', newRow)
                newRow = re.sub(RE_CELL_SIZE, '', newRow)
                newRow = re.sub(RE_CELL_H_ALIGN, '', newRow)
                newRow = re.sub(RE_CELL_V_ALIGN, '', newRow)
                newRow = re.sub(RE_FOLDING, '', newRow)
                newRow = re.sub(RE_TRIPLE_BARKET_BACK, '', newRow)

                # Ruby
                if re.search(RE_MACRO_RUBY, newRow):
                    rubyList = re.findall(RE_MACRO_RUBY, newRow)
                    
                    for rubyStr in rubyList:
                        delRubyStr = re.sub(RE_RUBY_FRONT, '', rubyStr)
                        delRubyStr = re.sub(RE_RUBY_BACK, '', delRubyStr)
                        newRow = newRow.replace(rubyStr, delRubyStr)
                table[idx] = newRow

    '''
        Split Row and Col by '||'
    '''
    def SplitRowAndColByToken(self, table):
        retTable = []

        for row in table:
            newRow = []
            spliteRowList = re.split(RE_ROW_SPLIT, row)[1:-1]

            for col in spliteRowList:
                newRow.append(col)
            retTable.append(newRow)

        return retTable

    '''
        Split Col Span
    '''
    def SplitColSpan(self, table):
        retTable = []

        for row in table:
            newRow = []

            for col in row:
                if re.search(RE_NEW_COL_SPAN, col):
                    spanCnt = int(re.search(RE_NEW_COL_SPAN, col).group(0).replace('<-', '').replace('>', ''))
                    newCol = re.sub(RE_NEW_COL_SPAN, '<cs>', col)
                    for spIdx in range(spanCnt):
                        newRow.append(newCol)
                else:
                    newRow.append(col)
            retTable.append(newRow)

        return retTable


    '''
        Split Row Span
    '''
    def SplitRowSpan(self, table):
        retTable = []

        spanInfoList = [] # (colIdx, str, spanCnt)
        for row in table:
            newRow = []

            for cIdx, col in enumerate(row):
                if re.search(RE_NEW_ROW_SPAN, col):
                    spanCnt = int(re.search(RE_NEW_ROW_SPAN, col).group(0).replace("<|", '').replace(">", ''))
                    newCol = re.sub(RE_NEW_ROW_SPAN, '<rs>', col)
                    spanInfo = (cIdx, newCol, spanCnt-1)
                    spanInfoList.append(spanInfo)

                    newRow.append(newCol)
                else:
                    for infoIdx, infoData in enumerate(spanInfoList):
                        if cIdx == infoData[0]:
                            newRow.append(infoData[1])
                            if 0 > infoData[2]-1:
                                spanInfoList.remove(infoData)
                            else:
                                newInfo = (infoData[0], infoData[1], infoData[2]-1)
                                spanInfoList[infoIdx] = newInfo
                    newRow.append(col)
            retTable.append(newRow)

        return retTable
        
    '''
        Remove Empty Cells
    '''
    def RemoveEmptyCells(self, table):
        retTable = []

        for row in table:
            newRow = []

            for col in row:
                removeTokenCol = re.sub(r"<\w+>", '', col)
                if 0 < len(removeTokenCol):
                    newRow.append(col)
            if 0 < len(newRow):
                retTable.append(newRow)

        return retTable

    '''
        Slice Table Length with min length
    '''
    def SliceTableLength(self, table):
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

    '''
        Merge Related Process 
    '''
    def PreprocessingTable(self, table):
        retTable = table

        ## Preprocess
        retTable = self.SplitRowAndColByToken(table)
        retTable = self.SplitColSpan(retTable)
        retTable = self.SplitRowSpan(retTable)
        retTable = self.RemoveEmptyCells(retTable)
        retTable = self.SliceTableLength(retTable)

        return retTable