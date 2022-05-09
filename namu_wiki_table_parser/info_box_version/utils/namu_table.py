import re
import sys
from namu_syntax import NAMU_RE

'''
    Split Row and Col by '||'
'''
def SplitRowAndColByToken(table):
    retTable = []

    for row in table:
        newRow = []
        spliteRowList = re.split(NAMU_RE.ROW_SPLIT.value, row)[1:]

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
                spanCnt = int(
                    re.search(NAMU_RE.NEW_COL_SPAN.value, col).group(0).replace('<-', '').replace('>', ''))
                newCol = re.sub(NAMU_RE.NEW_COL_SPAN.value, "", col)
                for spIdx in range(spanCnt):
                    newRow.append(newCol.strip())
            else:
                newRow.append(col.strip())
        retTable.append(newRow)

    return retTable

'''
    Split Row Span
'''
def SplitRowSpan(table):
    retTable = []

    spanInfoList = []  # (colIdx, str, spanCnt)
    for row in table:
        newRow = []

        for cIdx, col in enumerate(row):
            if re.search(NAMU_RE.NEW_ROW_SPAN.value, col):
                spanCnt = int(
                    re.search(NAMU_RE.NEW_ROW_SPAN.value, col).group(0).replace("<|", '').replace(">", ''))
                newCol = re.sub(NAMU_RE.NEW_ROW_SPAN.value, "", col)
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

def remove_empty_cells(table):
    ret_table = []

    for row in table:
        new_row = list(filter(lambda x: True if 0 < len(x) else False, row))
        if 0 < len(new_row):
            ret_table.append(new_row)
    return ret_table

'''
    Remove Empty Cells
'''
def remove_short_rows(table):
    retTable = []

    for row in table:
        if 1 < len(row):
            retTable.append(row)

    return retTable

'''
    Slice Table Length with min length
'''
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

def extend_row(table):
    ret_table = []

    # check max len(row)
    max_row_len = [len(x) for x in table]
    max_row_len = max(max_row_len)

    for row in table:
        new_row = row
        if max_row_len > len(row):
            new_row.extend(["" for _ in range(max_row_len - len(row) + 1)])
        ret_table.append(new_row)

    return ret_table

def PreprocessingTable(table):
    retTable = table

    ## Preprocess
    retTable = SplitRowAndColByToken(table)
    retTable = SplitColSpan(retTable)
    retTable = extend_row(retTable)
    retTable = SplitRowSpan(retTable)
    retTable = remove_empty_cells(retTable)
    retTable = remove_short_rows(retTable)
    retTable = SliceTableLength(retTable)

    return retTable

def clear_link_syntax_in_table(table):
    ret_table = table
    for row in ret_table:
        for cdx, col in enumerate(row):
            conv = col.replace("[[", "")
            conv = conv.replace("]]", "")
            row[cdx] = conv

    return ret_table


#### FOR BODY TEXT
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
            # Exception - [[분류:VOCALOID 오리지널 곡/2010년]][[분류:VOCALOID 전당입성]][[분류:나무위키 VOCALOID 프로젝트]]
            newStr = re.sub(r"\[\[분류:[^\]]+\]\]", "", splitStr)
            newStr = re.sub(NAMU_RE.IMAGE_FILE.value, '', newStr)
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
            # newStr = re.sub(NAMU_RE.LINK_ALT_FRONT.value, '', newStr)
            # newStr = re.sub(NAMU_RE.LINK_BASIC_FRONT.value, '', newStr)
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

            # newStr = re.sub(NAMU_RE.LINK_BACK.value, '', newStr)
            newStr = re.sub(NAMU_RE.TRIPLE_BARKET_BACK.value, '', newStr)

            # 12. Macro - Ruby
            if re.search(NAMU_RE.MACRO_RUBY.value, newStr):
                rubyList = re.findall(NAMU_RE.MACRO_RUBY.value, newStr)

                for rubyStr in rubyList:
                    delRubyStr = re.sub(NAMU_RE.RUBY_FRONT.value, '', rubyStr)
                    delRubyStr = re.sub(NAMU_RE.RUBY_BACK.value, '', delRubyStr)
                    newStr = newStr.replace(rubyStr, delRubyStr)

            # Exception (Last Process)
            # newStr = re.sub(r'[^\]]\[[^\]]+\]', '', newStr)

            if re.search(NAMU_RE.DISPLAY_TEXT.value, newStr):
                target_list = re.findall(NAMU_RE.DISPLAY_TEXT.value, newStr)
                for target_word in target_list:
                    rhs_txt = target_word.split("|")[-1]
                    newStr = newStr.replace(target_word, "[[" + rhs_txt)

            # Add newStr to return list
            if 0 < len(newStr.strip()):
                retStrList.append(newStr.strip())

    return retStrList