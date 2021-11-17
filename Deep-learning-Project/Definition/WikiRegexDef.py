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

    ROW_SPAN = r"rowspan=\"[0-9]+\" \| [^\|]*"
    COL_SPAN = r"colspan=\"[0-9]+\" \| [^\|]*"

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

    SPECIAL_CHAR = r"&[a-zA-Z]+;"
    SUBP_SCRIPT = r"<su(b|p)>[^(<su(b|p)>))]+</su(b|p)>"

    MATH_TAG= r"<math>[^<]+</math>"
    SPAN_TAG = r"<span (?!</span>).+</span>"

    REDIRECT = r"#넘겨주기 (\[\[)[^\]]+(\]\])"

    EXT_LINK_ALT = r"\[[^\]]+ [^\]]+\]"
    EXT_LINK_ALT_LHS = r"\[[^\]]+\s"
    EXT_LINK = r"\[[^\]]+\]"

    REF = r"(<ref>).+(</ref>)"
    REF_2 = r"<ref .+>.+</ref>"
    REF_3 = r"<ref[^=]+=[^/]+/>"
    COMMENT = r"(<!--).+(-->)"

    VERTICAL_BAR = r"\|"

if "__main__" == __name__:
    # TODO
    test_str = "란스니스트리아만이 승인하는 독립 국가이다.<ref name=\"cnnAbSO\">url=http://www.cnn.com/2008/WORLD/europe/08/26/russia.vote.georgia/index.html</ref>"
    if re.search(WIKI_RE.REF_2.value, test_str):
        print(re.search(WIKI_RE.REF_2.value, test_str))