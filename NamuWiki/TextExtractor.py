

'''
    @Note
        Extract text only
        Remove text attr, size, color, background color, hyper-link....
'''
import re

### REGEX
# 2.1
RE_TEXT_FORM = r"(''' '')|('' ''')|(''')|('')|__|~~|--" # Check Priority (''' '', ''')
RE_SUB_SCRIPT = r'\^\^|,,'
RE_LITERAL = r'\{\{\{\[\[|\]\]\}\}\}'

# 2.2
RE_TEXT_SIZE_FRONT = r'\{\{\{(\+|-)\d\s*' # text size input's front

# 2.3
RE_TEXT_COLOR = r'\{\{\{#\w+(,\s?#\w+)?\s?'

RE_TEXT_ATTR_BACK = r"}}}"

# 3
RE_LINK_ALT_FRONT = r"\[\[[^\|\]]+\|"
RE_LINK_BASIC_FRONT = r"\[\["
RE_LINK_BACK = r"\]\]"

# 8
RE_ADD_LIST = r'v+(\w*\.|\*)?v*'
RE_BASIC_LIST = r"\*"

# 9, 12.3
RE_FOOT_NOTE = r'\[\*.+\]|\[각주\]|\[footnote\]'

# 10
RE_QUOTE = r">{1,}"

# 11
RE_HORIZON_LINE = r"-{4,9}"

# 12
RE_MACRO_RUBY = r'\[ruby\(\w+, ruby=\w+\)\]'
RE_RUBY_FRONT = r'\[ruby\('
RE_RUBY_BACK = r',\s?ruby=.+\)\]'

# 12.2
RE_AGE_FORM = r'\[age\(\d{4}-\d{1,2}-\d{1,2}\)\]'
RE_DATE_TIME_FORM = r'\[date\]|\[datetime\]'
RE_DDAY_FORM = r'\[dday\(\d{4}-\d{1,2}-\d{1,2}\)\]'

# 12.3
RE_CONTENTS_TAG = r"\[목차\]|\[tableofcontents\]"

# 12.4
RE_BR_TAG = r'(\[BR\])|(\[br\])'
RE_CLEARFIX = r'\[clearfix\]'

# 14
RE_FOLDING = r'\{\{\{#!folding\s?\[[^\[.]+\]'

class TextExtractor:
    ### VAR ###


    ### PRIVATE ###


    ### PUBLIC ####
    def __init__(self):
        print('INIT TextExtractor !')

    '''
        @Note
            Extract Text and remove <\w+> from table
        @Param
            tableList (source)
        @Return
            retTableList (include only text)
    '''
    def ExtractTextAtTable(self, tableList):
        retTableList = []

        for table in tableList:
            newTable = []
            for row in table:
                newRow = []
                for col in row:
                    newCol = re.sub(r"<\w+>", '', col) # attr tag
                    newCol = re.sub(RE_LINK_ALT_FRONT, '', newCol) # [[.+|.+]]
                    newCol = re.sub(RE_LINK_BASIC_FRONT, '', newCol) # [[.+]]
                    newCol = re.sub(RE_LINK_BACK, '', newCol) # [[.+|.+]] and [[.+]]

                    newRow.append(newCol)
                newTable.append(newRow)
            retTableList.append(newTable)

        return retTableList

    '''
        @Note
            Remove Namu-wiki syntax
        @Param
            srcString (length is 1)
        @Return
            retStringList (split by '.')
    '''
    def RemoveNamuwikiSyntax(self, srcStr):
        retStrList = []

        splitStrList = srcStr[0].split('.')
        for splitStr in splitStrList:
            newStr = re.sub(RE_TEXT_FORM, '', splitStr)
            newStr = re.sub(RE_SUB_SCRIPT, '', newStr)
            newStr = re.sub(RE_TEXT_SIZE_FRONT, '', newStr)
            newStr = re.sub(RE_TEXT_COLOR, '', newStr)
            newStr = re.sub(RE_LITERAL, '', newStr)
            newStr = re.sub(RE_LINK_ALT_FRONT, '', newStr)
            newStr = re.sub(RE_LINK_BASIC_FRONT, '', newStr)
            newStr = re.sub(RE_LINK_BACK, '', newStr)
            newStr = re.sub(RE_TEXT_ATTR_BACK, '', newStr)
            newStr = re.sub(RE_ADD_LIST, '', newStr)
            newStr = re.sub(RE_BASIC_LIST, '', newStr)
            newStr = re.sub(RE_FOOT_NOTE, '', newStr)
            newStr = re.sub(RE_QUOTE, '', newStr)
            newStr = re.sub(RE_HORIZON_LINE, '', newStr)
            newStr = re.sub(RE_AGE_FORM, '', newStr)
            newStr = re.sub(RE_DATE_TIME_FORM, '', newStr)
            newStr = re.sub(RE_DDAY_FORM, '', newStr)
            newStr = re.sub(RE_CONTENTS_TAG, '', newStr)
            newStr = re.sub(RE_BR_TAG, '', newStr)
            newStr = re.sub(RE_CLEARFIX, '', newStr)
            newStr = re.sub(RE_FOLDING, '', newStr)

            # 12. Macro - Ruby
            if re.search(RE_MACRO_RUBY, newStr):
                rubyList = re.findall(RE_MACRO_RUBY, newStr)

                for rubyStr in rubyList:
                    delRubyStr = re.sub(RE_RUBY_FRONT, '', rubyStr)
                    delRubyStr = re.sub(RE_RUBY_BACK, '', delRubyStr)
                    newStr = newStr.replace(rubyStr, delRubyStr)

            if 0 < len(newStr.lstrip()):
                retStrList.append(newStr.lstrip())

        return retStrList