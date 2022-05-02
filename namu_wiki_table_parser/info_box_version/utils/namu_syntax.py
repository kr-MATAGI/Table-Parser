import re
from enum import Enum

class NAMU_RE(Enum):
    ## My Custom Attribute Token
    CUSTOM_ATTR = r'<\w+>'
    CUSTOM_BR = "{br}"

    ## Paragraph
    PARAGRAPH = r"={2,}#? .+ #?={2,}"

    # Is sentence end punctuation(.)?
    SENTENCE_PUNCT = r"\.$|\]$"

    ## Table
    ROW_SPLIT = r'\|\|'

    OLD_COL_SPAN = r'\|\|{2,}'
    NEW_COL_SPAN = r'<-\d+>'

    NEW_ROW_SPAN = r'<\|\d+>'

    ### Convert
    # 2.1
    TEXT_FORM = r"(''' '')|('' ''')|(''')|('')|__|~~|--" # Check Priority (''' '', ''')
    CONV_TEXT_FORM = "<tf>" # text form

    SUB_SCRIPT = r'\^\^|,,'
    CONV_SUB_SCRIPT = ' ' # white space

    # 2.3
    TEXT_COLOR = r'\{\{\{#\w+(,\s?#\w+)?\s?'
    CONV_TEXT_COLOR = '<tc>' # text color

    # 13.3.1
    BG_COLOR = r'<bgcolor=#?(\w|\d)+(,\s?#?\w+)?>'
    OLD_BG_COLOR = r'<#\w+>'
    CONV_BG_COLOR = '<bg>'

    TBG_COLOR = r'<(tablecolor|table\s?bgcolor)=#?\w+(,\s?#?\w+)?>'
    CONV_TBG_COLOR = '<tbg>'

    COL_BG_COLOR = r'<colbgcolor=#?\w+(,\s?#?\w+)?>'
    CONV_COL_BG_COLOR = '<cbg>'

    ROW_BG_COLOR = r'<rowbgcolor=#?\w+(,\s?#?\w+)?>'
    CONV_ROW_BG_COLOR = '<rbg>'

    CELL_COLOR = r'<color=#?\w+(,\s?#?\w+)?>'
    CONV_CELL_COLOR = '<celc>'

    COL_COLOR = r'<colcolor=#?\w+(,\s?#?\w+)?>'
    CONV_COL_COLOR = '<colc>'

    ROW_COLOR = r'<rowcolor=#?\w+(,\s?#?\w+)?>'
    CONV_ROW_COLOR = '<rowc>'

    ### Remove
    # 2.1
    LITERAL = r'\{\{\{\[\[|\]\]\}\}\}'

    # 2.2
    TEXT_SIZE_FRONT = r'\{\{\{(\+|-)\d\s*' # text size input's front

    # 3
    PARENT_ARTICLE_LINK = r'(\[\[)\.\./(\]\])'
    # CHILD_ARTICLIE_LINK = r'\[\[[/[\w]+]+'
    EXTERNAL_LINK = r'\[\[https?://[^\|(\]\])]\]\]'

    LINK_ALT_FRONT = r"\[\[[^\|\]]+\|"
    LINK_BASIC_FRONT = r"\[\["
    LINK_BACK = r"\]\]"

    # 5
    IMAGE_FILE = r'\[\[파일:[^\]]+(\|[^\]+])?\]\]'

    # 6
    YOUTUBE = r'\[youtube\(\w+(,\s?(start|width|height)=\w+%?)*\)\]|' \
                 r'\[include\(틀:.+ (left|center|right)?\s?url=\w+\)(,\s?(start|width|height)=\w+%?)*\]'
    KAKAO_TV = r'\[kakaotv\(\w+(,\s?(start|width|height)=\w+%?)*\)\]'
    NICO_VIDEO = r'\[nicovideo\(\w+(,\s?(start|width|height)=\w+%?)*\)\]'
    NAVER_VIDEO = r'\[include\(틀:(navertv|navervid){1}(,\s?(i=\w+|vid=\w+,\s?outkey=\w+)+)+(,\s?(start|width|height)=\w+%?)*\)\]'
    # 6 - deep syntax
    HTML_VIDEO = r'{{{#!html[^(}}})]+}}}'

    # 8
    ADD_LIST = r'v+(\w*\.|\*)?v*'
    BASIC_LIST = r"\*"

    # 9, 12.3
    FOOT_NOTE = r'\[\*.+\]|\[각주\]|\[footnote\]'

    # 10
    QUOTE = r">{1,}"

    # 11
    HORIZON_LINE = r"-{4,9}"

    # 12.1
    DOC_INSERT = r'\[include\(틀:[^\)]+\)\]'

    # 12.2
    AGE_FORM = r'\[age\(\d{4}-\d{1,2}-\d{1,2}\)\]'
    DATE_TIME_FORM = r'\[date\]|\[datetime\]'
    DDAY_FORM = r'\[dday\(\d{4}-\d{1,2}-\d{1,2}\)\]'

    # 12.3
    CONTENTS_TAG = r"\[목차\]|\[tableofcontents\]"

    # 12.4
    BR_TAG = r'(\[BR\])|(\[br\])'
    CLEARFIX = r'\[clearfix\]'

    # 13.3.1
    TABLE_ALIGN = r'<table\s?align=("|\')?(left|center|right)("|\')?>'
    TABLE_WIDTH = r'<table\s?width=\d+(px|%)?>'

    TABLE_BORDER_COLOR = r'<table\s?bordercolor=#?\w+(,#?\w+)?>'

    CELL_SIZE = r'<(width|height)=\d+(px|%)?>'

    CELL_H_ALIGN = r'(<\(>)|(<:>)|(<\)>)'
    CELL_V_ALIGN = r'(<\^\|\d+>)|(<v\|\d+>)'  # (<\|\d+>) ? -> row Span

    # 14
    FOLDING = r'\{\{\{#!folding\s?\[[^\[.]+\]'

    # macro - ruby
    MACRO_RUBY = r'\[ruby\(\w+, ruby=\w+\)\]'
    RUBY_FRONT = r'\[ruby\('
    RUBY_BACK = r',\s?ruby=.+\)\]'

    # tirple barket }}}
    TRIPLE_BARKET_BACK = r'}}}'

    # Exception
    FILE_LINK_FRONT = r"\[\[파일:.+"

    # Remove [[ TEXT ]], CONV [[ TEXT | TEXT ]]
    DISPLAY_TEXT = r"\[\[[^|\]]+\|[^\]]+\]\]"
    HYPER_LINK = r"\[\[[^\]]+\]\]"

#============================================================
def ModifyHTMLTags(table):
    newTable = []
    for idx, row in enumerate(table):
        newRow = row

        # Convert Tags -> Remove_Tag
        newRow = re.sub(NAMU_RE.TEXT_FORM.value, "", newRow)
        newRow = re.sub(NAMU_RE.SUB_SCRIPT.value, "", newRow)
        newRow = re.sub(NAMU_RE.TEXT_COLOR.value, "", newRow)
        newRow = re.sub(NAMU_RE.BG_COLOR.value, "", newRow)
        newRow = re.sub(NAMU_RE.TBG_COLOR.value, "", newRow)
        newRow = re.sub(NAMU_RE.COL_BG_COLOR.value, "", newRow)
        newRow = re.sub(NAMU_RE.ROW_BG_COLOR.value, "", newRow)
        newRow = re.sub(NAMU_RE.CELL_COLOR.value, "", newRow)
        newRow = re.sub(NAMU_RE.COL_COLOR.value, "", newRow)
        newRow = re.sub(NAMU_RE.ROW_COLOR.value, "", newRow)

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
        newRow = re.sub(NAMU_RE.OLD_BG_COLOR.value, "", newRow)
        # newRow = re.sub(NAMU_RE.LINK_BACK.value, '', newRow)
        newRow = re.sub(NAMU_RE.FILE_LINK_FRONT.value, "", newRow)

        # Ruby
        if re.search(NAMU_RE.MACRO_RUBY.value, newRow):
            rubyList = re.findall(NAMU_RE.MACRO_RUBY.value, newRow)

            for rubyStr in rubyList:
                delRubyStr = re.sub(NAMU_RE.RUBY_FRONT.value, '', rubyStr)
                delRubyStr = re.sub(NAMU_RE.RUBY_BACK.value, '', delRubyStr)
                newRow = newRow.replace(rubyStr, delRubyStr)

        # Remove [[ TEXT ]], CONV [[ TEXT | TEXT ]]
        if re.search(NAMU_RE.DISPLAY_TEXT.value, newRow):
            target_list = re.findall(NAMU_RE.DISPLAY_TEXT.value, newRow)
            for target_word in target_list:
                rhs_txt = target_word.split("|")[-1]
                newRow = newRow.replace(target_word, "[["+rhs_txt)
        # if re.search(NAMU_RE.HYPER_LINK.value, newRow):
        #     target_list = re.findall(NAMU_RE.HYPER_LINK.value, newRow)
        #     for target_word in target_list:
        #         conv_word = target_word.replace("[[", "").replace("]]", "")
        #         newRow = newRow.replace(target_word, conv_word)

        # Exception - ['<#FFFFFF,#1F2023>NME 선정 500대 명반|', '<#FFFFFF,#1F2023>NME 선정 500대 명반67위']
        newRow = re.sub(r"<#[^>]+>", "",newRow)
        # Exception - 'http://www.nicojp/watch/sm12099561|https://piapro.jp/t/AmXV|'
        newRow = re.sub(r"(http|https)://[^\|]+\|", "", newRow)
        # Exception - {{{#!wiki style="margin: -5px -10px;"
        newRow = re.sub(r"\{\{\{#!wiki .+", "", newRow)

        newTable.append(newRow.strip())
    return newTable