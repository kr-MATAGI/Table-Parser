# -*- coding: utf-8 -*-

import re
from enum import Enum

class WIKI_RE(Enum):
    TABLE_START = r"{\|"
    TABLE_ROW = r"\|-"
    TABLE_NEWLINE_COL = r"\|.+"
    TABLE_DOUBLE_COL = r"\|\|"
    TABLE_END = r"\|}"

    TABLE_TITLE = r"\|\+"
    TABLE_HEAD = r"!\s"

    ROW_SPAN = r"rowspan=\"?[0-9]+\"?\s?\|[^\|]*"
    COL_SPAN = r"colspan=\"?[0-9]+\"?\s?\|[^\|]*"

    DEL_ROW_SPAN = r"rowspan=\"?[0-9]+\"?"
    DEL_COL_SPAN = r"colspan=\"?[0-9]+\"?"

    FILE = r"(\[\[)파일:[^\]]+(\]\])"
    MEDIA = r"(\[\[)미디어:[^\]]+(\]\])"

    CLASS = r"class=\"[a-zA-Z0-9]+\""
    BG_COLOR = r"bgcolor=\"#?[a-zA-Z0-9]+\""
    ALIGN = r"align=[a-z]+\|"

    BR = r"<br />"

    FREE_LINK_BASIC = r"(\[\[)[^\]]+(\]\])"
    FREE_LINK_ALT = r"(\[\[)([^\]]+\|[^\]]+)(\]\])"
    FREE_LINK_LHS = r"(\[\[)[^\]]+\|"
    FREE_LINK_OPEN = r"(\[\[)"
    FREE_LINK_CLOSED = r"(\]\])"

    CITE = r"\{\{[^}]+\}\}"

    FONT_SHAPE_5 = r"(''''')[^']+(''''')"
    FONT_SHAPE_3 = r"(''')[^']+(''')"
    FONT_SHAPE_2 = r"('')[^']+('')"

    STYLE = r"style=\"[^\"]+\""
    WIDTH = r"width=[0-9]+%?"

    SPECIAL_CHAR = r"&[a-zA-Z]+;"
    SUBP_SCRIPT = r"<su(b|p)>[^(<su(b|p)>))]+</su(b|p)>"

    MATH_TAG= r"<math>[^<]+</math>"
    SPAN_TAG = r"<span (?!</span>).+</span>"

    REDIRECT = r"#넘겨주기 (\[\[)[^\]]+(\]\])"

    EXT_LINK_ALT = r"\[[^\]]+ [^\]]+\]"
    EXT_LINK_ALT_LHS = r"\[[^\]]+\s"
    EXT_LINK = r"\[[^\]]+\]"

    REF = r"(<ref>).+(</ref>)"
    REF_2 = r"<ref .+>[^<]+(</ref>)"
    REF_3 = r"<ref[^=]+=[^/]+/>"
    REF_4 = r"ref.+/ref"
    REF_5 = r"<ref>.+"

    COMMENT = r"(<!--).+(-->)"
    PRE = "(<pre>)|(</pre>)"

    SENT_ALIGN = "\*{1,4}.+"
    V_ALIGN = "valign=[a-zA-Z]+"

    VERTICAL_BAR = r"\|"

if "__main__" == __name__:
    testStr = 'valign=top 유엔 가입 국가로 승인 받았'
    if re.search(WIKI_RE.REF.value, testStr):
        print(re.search(WIKI_RE.REF.value, testStr).group(0))

    if re.search(WIKI_RE.REF_2.value, testStr):
        print(re.search(WIKI_RE.REF_2.value, testStr).group(0))

    if re.search(WIKI_RE.REF_3.value, testStr):
        print(re.search(WIKI_RE.REF_3.value, testStr).group(0))

    if re.search(WIKI_RE.REF_4.value, testStr):
        print(re.search(WIKI_RE.REF_4.value, testStr).group(0))

    if re.search(WIKI_RE.SENT_ALIGN.value, testStr):
        print(re.search(WIKI_RE.SENT_ALIGN.value, testStr).group(0))

    if re.search(WIKI_RE.V_ALIGN.value, testStr):
        print(re.search(WIKI_RE.V_ALIGN.value, testStr).group(0))