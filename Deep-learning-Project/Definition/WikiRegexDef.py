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

    CITE = r"{{([^\|]+\|?)+}}"

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

    VERTICAL_BAR = r"\|"

if "__main__" == __name__:
    test_str = "[[Mobile IP]]"

    a = re.search(WIKI_RE.FREE_LINK_BASIC.value, test_str)
    a_1 = re.sub(WIKI_RE.FREE_LINK_OPEN.value, "", test_str)
    a_2 = re.sub(WIKI_RE.FREE_LINK_CLOSED.value, "", a_1)
    print(a_2)

    test_str2 = "[[서울 특별시|대한민국의 수도]]"
    b = re.search(WIKI_RE.FREE_LINK_ALT.value, test_str2)
    b_1 = re.sub(WIKI_RE.FREE_LINK_LHS.value, "", test_str2)
    b_2 = re.sub(WIKI_RE.FREE_LINK_CLOSED.value, "", b_1)
    print(b_2)

    test_str3 = "aa {{flagIOCmedalist|에코 율리 이라완|INA|2020|하계}}"
    c = re.search(WIKI_RE.CITE.value, test_str3)
    c_1 = re.split(WIKI_RE.VERTICAL_BAR.value, test_str3)
    print(c.group(0))
    print(c_1)

    test_str4 = "|{{flagIOCmedalist|[[알리 다부디]]|IRI|2020|하계}}"
    d = re.search(WIKI_RE.TABLE_NEWLINE_COL.value, test_str4)
    print(d)

    test_str5 = "새로운 문단을 시작하지 않아도<br /> 다음 줄로 내릴 수 있습니다."
    e = re.search(WIKI_RE.BR.value, test_str5)
    print(e)

    test_str6 = "'''''글자 모양을 만듭니다.''''' ''기울어진거'' '''진한거'''"
    f = re.search(WIKI_RE.FONT_SHAPE_5.value, test_str6).group(0)
    f_2 = f.replace("'''''", "")
    test_str6 = test_str6.replace(f, f_2)

    f = re.search(WIKI_RE.FONT_SHAPE_3.value, test_str6).group(0)
    f_2 = f.replace("'''", "")
    test_str6 = test_str6.replace(f, f_2)

    f = re.search(WIKI_RE.FONT_SHAPE_2.value, test_str6).group(0)
    f_2 = f.replace("''", "")
    test_str6 = test_str6.replace(f, f_2)
    print(test_str6)

    test_str7 = "&Agrave; &Aacute; &Acirc; &Atilde; &Auml; &Aring; &Uacute; &Ucirc; &Uuml;"
    g = re.findall(WIKI_RE.SPECIAL_CHAR.value, test_str7)
    print(test_str7)

    test_str8 = "X<sub>1</sub> X<sub>2</sub> X<sub>10</sub>"
    h = re.sub(WIKI_RE.SUBP_SCRIPT.value, "", test_str8)
    print(h)

    test_str9 = "X<sup>1</sup> X<sup>2</sup> X<sup>10</sup>"
    i = re.sub(WIKI_RE.SUBP_SCRIPT.value, "", test_str9)
    print(i)

    test_str10 = "X<sup>a<sub>1</sub></sup>"
    j = re.sub(WIKI_RE.SUBP_SCRIPT.value, "", test_str9)
    print(j)


    test_str11 = "<math> x </math>가 실수일 때 <math>x^2 \ge 0 </math> 가 항상 성립한다."
    a11 = re.sub(WIKI_RE.MATH_TAG.value, "", test_str11)

    test_str12 = "따라서 다음과 같은 식으로 나타낼 수 있다. <span class=\"mw-poem-indented\ style=\"display: inline-block; margin-inline-start: 1em;\" <math>\sum_{n=0}^\infty \frac{x^n}{n!}</math></span> 이 식에 의한 급수는"
    a12 = re.sub(WIKI_RE.SPAN_TAG.value, "", test_str12)
    print(re.search(WIKI_RE.SPAN_TAG.value, test_str12).group(0))
    print(a12)

    test_str13 = "#넘겨주기 [[유엔#활동]]"
    if re.search(WIKI_RE.REDIRECT.value, test_str13):
        corresStr = re.search(WIKI_RE.REDIRECT.value, test_str13).group(0)
        convertedStr = corresStr.replace("#넘겨주기 [[", "")
        convertedStr = convertedStr.replace("]]", "")
        test_str13 = test_str13.replace(corresStr, convertedStr)
        print(test_str13)

    test_str14 = "[http://ko.wikipedia.org/ 위키백과]"
    test_str15 = "[http://ko.wikipedia.org/]"

    if re.search(WIKI_RE.EXT_LINK_ALT.value, test_str14):
        corres = re.search(WIKI_RE.EXT_LINK_ALT.value, test_str14).group(0)
        a14 = re.sub(WIKI_RE.EXT_LINK_ALT_LHS.value, "", corres)
        a14 = re.sub(r"\]", "", a14)
        print("14", a14)

    a15 = re.search(WIKI_RE.EXT_LINK.value, test_str15)
    print(a15)


    test_str16 = "[[파일:Wikipedia-logo-v2-ko.png|30 px|위키백과]]"
    test_str17 = "[[미디어:Wikipedia-logo-v2-ko.png|퍼즐 형태의 로고 그림]]"

    if re.search(WIKI_RE.FILE.value, test_str16):
        corresStr = re.search(WIKI_RE.FILE.value, test_str16).group(0)
        print(corresStr)
    if re.search(WIKI_RE.MEDIA.value, test_str17):
        corresStr = re.search(WIKI_RE.MEDIA.value, test_str17).group(0)
        print(corresStr)


    test_str18 = "| colspan=\"2\" |  | a |  | colspan=\"2\" | F"
    if re.search(WIKI_RE.COL_SPAN.value, test_str18):
        a18 = re.findall(WIKI_RE.COL_SPAN.value, test_str18)

        for elem in a18:
            newStrList = []
            splitElem = str(elem).split(" | ")
            count = splitElem[0].replace("colspan=", "")
            count = count.replace("\"", "")
            count = int(count)

            value = splitElem[1]
            for c in range(count):
                newStrList.append(value)

            newStr = " | ".join(newStrList)
            test_str18 = test_str18.replace(elem, newStr)

    test_str19 = "| rowspan=\"2\" | A"

    if re.search(WIKI_RE.ROW_SPAN.value, test_str19):
        a19 = re.findall(WIKI_RE.ROW_SPAN.value, test_str19)

        indexFind = test_str19.split("|")
        print(indexFind)
        for elem in a19:
            splitElem = str(elem).split(" | ")

            print(test_str19.index(elem))
            print(splitElem)
