import re
from typing import List

from namu_syntax import NAMU_RE

#####
def remove_namu_syntax(srcList):
    retStrList = []

    for srcStr in srcList:
        splitStrList = srcStr.split(NAMU_RE.CUSTOM_BR.value + NAMU_RE.CUSTOM_BR.value)  # \n\n
        for splitStr in splitStrList:
            # Delete \n
            splitStr = re.sub(NAMU_RE.CUSTOM_BR.value, '', splitStr)
            splitStr = splitStr.lstrip().rstrip()

            # Check '.' punctuation
            if not re.search(NAMU_RE.SENTENCE_PUNCT.value, splitStr):
                continue

            # re
            newStr = re.sub(NAMU_RE.IMAGE_FILE.value, '', splitStr)
            newStr = re.sub(NAMU_RE.YOUTUBE.value, '', newStr)
            newStr = re.sub(NAMU_RE.KAKAO_TV.value, '', newStr)
            newStr = re.sub(NAMU_RE.NICO_VIDEO.value, '', newStr)
            newStr = re.sub(NAMU_RE.NAVER_VIDEO.value, '', newStr)
            newStr = re.sub(NAMU_RE.HTML_VIDEO.value, '', newStr)
            newStr = re.sub(NAMU_RE.EXTERNAL_LINK.value, '', newStr)
            newStr = re.sub(NAMU_RE.DOC_INSERT.value, '', newStr)

            newStr = re.sub(NAMU_RE.TEXT_FORM.value, '', newStr)
            newStr = re.sub(NAMU_RE.SUB_SCRIPT.value, '', newStr)
            newStr = re.sub(NAMU_RE.TEXT_SIZE_FRONT.value, '', newStr)
            newStr = re.sub(NAMU_RE.TEXT_COLOR.value, '', newStr)
            newStr = re.sub(NAMU_RE.LITERAL.value, '', newStr)
            newStr = re.sub(NAMU_RE.LINK_ALT_FRONT.value, '', newStr)
            newStr = re.sub(NAMU_RE.LINK_BASIC_FRONT.value, '', newStr)
            newStr = re.sub(NAMU_RE.ADD_LIST.value, '', newStr)
            newStr = re.sub(NAMU_RE.BASIC_LIST.value, '', newStr)
            newStr = re.sub(NAMU_RE.FOOT_NOTE.value, '', newStr)
            newStr = re.sub(NAMU_RE.QUOTE.value, '', newStr)
            newStr = re.sub(NAMU_RE.HORIZON_LINE.value, '', newStr)
            newStr = re.sub(NAMU_RE.AGE_FORM.value, '', newStr)
            newStr = re.sub(NAMU_RE.DATE_TIME_FORM.value, '', newStr)
            newStr = re.sub(NAMU_RE.DDAY_FORM.value, '', newStr)
            newStr = re.sub(NAMU_RE.CONTENTS_TAG.value, '', newStr)
            newStr = re.sub(NAMU_RE.BR_TAG.value, '', newStr)
            newStr = re.sub(NAMU_RE.CLEARFIX.value, '', newStr)
            newStr = re.sub(NAMU_RE.FOLDING.value, '', newStr)

            newStr = re.sub(NAMU_RE.LINK_BACK.value, '', newStr)
            newStr = re.sub(NAMU_RE.TRIPLE_BARKET_BACK.value, '', newStr)

            # 12. Macro - Ruby
            if re.search(NAMU_RE.MACRO_RUBY.value, newStr):
                rubyList = re.findall(NAMU_RE.MACRO_RUBY.value, newStr)

                for rubyStr in rubyList:
                    delRubyStr = re.sub(NAMU_RE.RUBY_FRONT.value, '', rubyStr)
                    delRubyStr = re.sub(NAMU_RE.RUBY_BACK.value, '', delRubyStr)
                    newStr = newStr.replace(rubyStr, delRubyStr)

            # Exception (Last Process)
            newStr = re.sub(r'\[[^\]]+\]', '', newStr)

            # Add newStr to return list
            if 0 < len(newStr.lstrip()):
                retStrList.append(newStr.lstrip())

    return retStrList

def find_table_content(table: List[List[str]], sent_list: List[str]):
    ret_related_sent_list = []

    if 0 >= len(sent_list):
        return ret_related_sent_list

    concat_sent_list = ""
    for sent in sent_list:
        concat_sent_list += sent
    split_sent_list = concat_sent_list.split(". ")
    table_content_set = set()
    for row in table:
        for col in row:
            table_content = col.strip()
            if 0 >= len(table_content):
                continue
            table_content_set.add(table_content)
    table_content_set = list(table_content_set)

    ret_related_sent_list = list(map(lambda x, y: y if x in y else None, table_content_set, split_sent_list))
    while None in ret_related_sent_list:
        ret_related_sent_list.remove(None)

    return ret_related_sent_list