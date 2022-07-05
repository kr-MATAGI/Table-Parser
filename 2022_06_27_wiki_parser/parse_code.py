from builtins import str, enumerate

import ijson
import copy
import xml.etree.ElementTree as ET
import re
import os
import pickle

from typing import List
from data_def import Wiki_Page, TT_Pair, SPLIT_PARAG, Table_2dim
from re_def import WIKI_SYNTAX

### METHOD
#==============================================================================
def parse_wiki_doc(src_path: str=""):
#==============================================================================
    if not os.path.exists(src_path):
        print(f"[parse_code][parse_wiki_doc] ERR - Not Exists: {src_path}")
        return

    wiki_page_info_list: List[Wiki_Page] = []
    for doc_title, doc_text in read_wiki_doc(src_path):
        # wiki_page_data = Wiki_Page(title=doc_title)

        # split
        if not doc_text:
            continue
        res_split_body = split_minimum_paragraph(doc_text)

        # 최소 단위의 문단 제목 찾기
        res_valid_info_list = check_valid_paragraph_list(res_split_body)

        # Wiki Page 데이터 생성
        res_valid_paragraph = filter_valid_paragraph(res_split_body, res_valid_info_list)

        # Wiki_page 구조 만듦 - Text만 존재하는거, Text랑 Table Pair(중복 허용)
        res_wiki_page = make_wiki_page_data(doc_title, res_valid_paragraph)
        wiki_page_info_list.append(res_wiki_page)
    print(f"[parse_wiki_doc] Complete - Size: {len(wiki_page_info_list)}")

    # save *.pkl file
    save_path = "./save_wiki_page_info.pkl"
    with open(save_path, mode="wb") as save_pkl:
        pickle.dump(wiki_page_info_list, save_pkl)
        print(f"[parse_code] Save - {save_path}")

    # check size
    with open(save_path, mode="rb") as check_pkl:
        check_list = pickle.load(check_pkl)
        print(f"[parse_code] LOAD - size: {len(check_list)}")

#==============================================================================
def make_wiki_page_data(doc_title: str, src_parag_list: List[SPLIT_PARAG]):
#==============================================================================
    ret_wiki_page = Wiki_Page(title=doc_title)

    for parag_body in src_parag_list:
        res_table_list, res_text_list = extract_paragraph_table(parag_body.text_list)

        # table
        res_table_list = conv_2dim_table(res_table_list)
        res_table_list = split_row_and_col_span(res_table_list)
        # res_table_list = fit_table_row_length(res_table_list)

        for table in res_table_list:
            for row in table.row_list:
                for cdx, col in enumerate(row):
                    conv_col = remove_wiki_syntax(col)
                    row[cdx] = conv_col

        # if 0 < len(res_table_list):
        #     print("TITLE: \t", doc_title)
        #     print("TEXT: \n", parag_body)
        #     for a in res_table_list:
        #         for b in a.row_list:
        #             print(len(b), "\t", b)
        #     input()

        # text
        paragraph_list: List[str] = []
        paragraph: str = ""
        for txt_idx, res_text in enumerate(res_text_list):
            conv_text = remove_wiki_syntax(res_text)

            # "" 를 기준으로 단락 구분
            if "" == conv_text:
                if 0 < len(paragraph):
                    paragraph_list.append(paragraph)
                paragraph = ""
            else:
                if 0 >= len(paragraph):
                    paragraph += conv_text
                else:
                    paragraph += " " + conv_text
        if 0 < len(paragraph): # 나머지
            paragraph_list.append(paragraph)

        if 0 < len(res_table_list): # make pair
            for target_table in res_table_list:
                for target_paragraph in paragraph_list:
                    tt_pair = TT_Pair(text=target_paragraph,
                                      table=target_table.row_list)
                    ret_wiki_page.text_table_pair.append(tt_pair)
        else:
            ret_wiki_page.only_text_list.extend(paragraph_list)

    return ret_wiki_page

#==============================================================================
def extract_paragraph_table(body_text: List[str]):
#==============================================================================
    ret_table_list: List[List[str]] = []
    ret_text_list: List[str] = []

    new_table: List[str] = []
    is_table_line = False
    for b_line in body_text:
        # Table Start
        if re.search(WIKI_SYNTAX.TABLE_START.value, b_line):
            is_table_line = True
        # Table End
        elif re.search(WIKI_SYNTAX.TABLE_END.value, b_line):
            is_table_line = False
            ret_table_list.append(copy.deepcopy(new_table))
            new_table.clear()
            ret_text_list.append("")

        # Table Contents
        if is_table_line:
            new_table.append(b_line)
        else:
            ret_text_list.append(copy.deepcopy(b_line))

    return ret_table_list, ret_text_list

#==============================================================================
def conv_2dim_table(src_table_list: List[List[str]]):
#==============================================================================
    ret_conv_table_list: List[Table_2dim] = []

    for src_table in src_table_list:
        table_2dim = Table_2dim()
        new_row = []
        is_new_row = False
        for row in src_table:
            if re.search(WIKI_SYNTAX.TABLE_ROW.value, row):
                is_new_row = True
                if 0 < len(new_row):
                    table_2dim.row_list.append(copy.deepcopy(new_row))
                    new_row.clear()
                continue
            if is_new_row:
                new_row.append(row)
        if 0 < len(new_row):
            table_2dim.row_list.append(copy.deepcopy(new_row))

        # Remove and split - '!!', '||'
        new_table_rows: List[str] = []
        for row in table_2dim.row_list:
            if re.search(r"\!\!", row[0]):
                conv_row = row[0].split("!!")
                conv_row = [x.replace("!", "") for x in conv_row]
                new_table_rows.append(conv_row)
            elif re.search(r"\|\|", row[0]):
                conv_row = row[0].split("||")
                new_table_rows.append(conv_row)
            else:
                new_table_rows.append(row)
        table_2dim.row_list = new_table_rows
        ret_conv_table_list.append(table_2dim)

    return ret_conv_table_list

#==============================================================================
def split_row_and_col_span(src_table_list: List[Table_2dim]):
#==============================================================================
    ret_table_list: List[Table_2dim] = []

    # Col span
    divColSpanTableList = []
    for table in src_table_list:
        newTable = []
        for rdx, row in enumerate(table.row_list):
            newRow = []
            for cdx, col in enumerate(row):
                if re.search(WIKI_SYNTAX.COL_SPAN.value, col):
                    corresStr = re.search(WIKI_SYNTAX.COL_SPAN.value, col).group(0)
                    splitedStrList = corresStr.split("|")
                    for idx, splitedStr in enumerate(splitedStrList):
                        splitedStrList[idx] = splitedStr.strip()

                    spanCount = splitedStrList[0].replace("colspan=", "").strip()
                    if -1 != spanCount.find("\""):
                        spanCount = int(spanCount.replace("\"", ""))
                    else:
                        spanCount = int(spanCount)

                    spanValue = splitedStrList[1].strip()

                    for sc in range(spanCount):
                        newRow.append(spanValue)
                else:
                    newRow.append(col)
            newTable.append(newRow)
        divColSpanTableList.append(newTable)

    # Row Span
    for table in divColSpanTableList:
        new_table = Table_2dim()
        for rdx, row in enumerate(table):
            for cdx, col in enumerate(row):
                if re.search(WIKI_SYNTAX.ROW_SPAN.value, col):
                    span_str = re.search(WIKI_SYNTAX.ROW_SPAN.value, col).group(0)
                    split_span_str = span_str.split("|")
                    span_count = split_span_str[0].replace("rowspan=", "").strip()
                    span_count = int(span_count.replace("\"", ""))
                    span_value = split_span_str[-1].strip()
                    row[cdx] = span_value

                    for sc in range(span_count):
                        if (rdx+sc) == rdx:
                            continue
                        if (rdx+sc) >= len(table):
                            break
                        table[rdx+sc].insert(cdx, span_value)
        new_table.row_list = copy.deepcopy(table)
        ret_table_list.append(new_table)

    return ret_table_list

#==============================================================================
def fit_table_row_length(table_list: List[Table_2dim]):
#==============================================================================
    ret_table_list: List[Table_2dim] = []

    for table in table_list:
        # Check max length
        max_row_len = 0
        for row in table.row_list:
            max_row_len = max_row_len if max_row_len > len(row) else len(row)

        # Extend last contents
        for row in table.row_list:
            if len(row) < max_row_len:
                diff_len = max_row_len - len(row)
                for loop in range(diff_len):
                    back_val = row[-1]
                    row.append(back_val)
    ret_table_list = table_list

    return ret_table_list

#==============================================================================
def remove_wiki_syntax(src_text: str):
# ==============================================================================
    conv_text: str = copy.deepcopy(src_text).strip()

    conv_text = re.sub(WIKI_SYNTAX.TABLE_HEAD.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.CLASS.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.BG_COLOR.value, "", conv_text)

    conv_text = re.sub(WIKI_SYNTAX.V_ALIGN.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.ALIGN.value, "", conv_text)

    # Ref
    conv_text = re.sub(WIKI_SYNTAX.REF.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.REF_2.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.REF_3.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.REF_4.value, "", conv_text)
    # conv_text = re.sub(WIKI_SYNTAX.REF_5.value, "", conv_text)

    # Comment, Pre
    conv_text = re.sub(WIKI_SYNTAX.COMMENT.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.PRE.value, "", conv_text)

    # Sentence Align
    conv_text = re.sub(WIKI_SYNTAX.SENT_ALIGN.value, "", conv_text)

    # <BR />
    conv_text = re.sub(WIKI_SYNTAX.BR_OPEN.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.BR_CLOSE.value, "", conv_text)

    # File & media
    conv_text = re.sub(WIKI_SYNTAX.FILE.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.MEDIA.value, "", conv_text)

    # Style
    conv_text = re.sub(WIKI_SYNTAX.STYLE.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.WIDTH.value, "", conv_text)

    # 2022.07.04
    # <code>, </code>
    conv_text = re.sub(WIKI_SYNTAX.CODE_OPEN.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.CODE_CLOSE.value, "", conv_text)


    # width="100" align="center"
    conv_text = re.sub(WIKI_SYNTAX.WIDTH_2.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.ALIGN_2.value, "", conv_text)

    # Font shape
    if re.search(WIKI_SYNTAX.FONT_SHAPE_5.value, conv_text):
        fontShape = re.search(WIKI_SYNTAX.FONT_SHAPE_5.value, conv_text).group(0)
        convertFontShape = fontShape.replace("'''''", "")
        conv_text = conv_text.replace(fontShape, convertFontShape)
    if re.search(WIKI_SYNTAX.FONT_SHAPE_3.value, conv_text):
        fontShape = re.search(WIKI_SYNTAX.FONT_SHAPE_3.value, conv_text).group(0)
        convertFontShape = fontShape.replace("'''", "")
        conv_text = conv_text.replace(fontShape, convertFontShape)
    if re.search(WIKI_SYNTAX.FONT_SHAPE_2.value, conv_text):
        fontShape = re.search(WIKI_SYNTAX.FONT_SHAPE_2.value, conv_text).group(0)
        convertFontShape = fontShape.replace("''", "")
        conv_text = conv_text.replace(fontShape, convertFontShape)

    # Special Character
    conv_text = re.sub(WIKI_SYNTAX.SPECIAL_CHAR.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.SUBP_SCRIPT.value, "", conv_text)

    # Tag
    conv_text = re.sub(WIKI_SYNTAX.SPAN_TAG.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.MATH_TAG.value, "", conv_text)

    # Redirect
    if re.search(WIKI_SYNTAX.REDIRECT.value, conv_text):
        corresStr = re.search(WIKI_SYNTAX.REDIRECT.value, conv_text).group(0)
        convertedStr = corresStr.replace("#넘겨주기 [[", "")
        convertedStr = convertedStr.replace("]]", "")
        conv_text = conv_text.replace(corresStr, convertedStr)

    # Free Link
    if re.search(WIKI_SYNTAX.FREE_LINK_ALT.value, conv_text):
        conv_text = re.sub(WIKI_SYNTAX.FREE_LINK_LHS.value, "", conv_text)
        conv_text = re.sub(WIKI_SYNTAX.FREE_LINK_CLOSED.value, "", conv_text)

    if re.search(WIKI_SYNTAX.FREE_LINK_BASIC.value, conv_text):
        conv_text = re.sub(WIKI_SYNTAX.FREE_LINK_OPEN.value, "", conv_text)
        conv_text = re.sub(WIKI_SYNTAX.FREE_LINK_CLOSED.value, "", conv_text)

    # External link
    if re.search(WIKI_SYNTAX.EXT_LINK_ALT.value, conv_text):
        corresStr = re.search(WIKI_SYNTAX.EXT_LINK_ALT.value, conv_text).group(0)
        convertedStr = re.sub(WIKI_SYNTAX.EXT_LINK_ALT_LHS.value, "", corresStr)
        convertedStr = re.sub(r"\]", "", convertedStr)
        conv_text = conv_text.replace(corresStr, convertedStr)

    # Cite
    if re.search(WIKI_SYNTAX.CITE.value, conv_text):
        corresStr = re.search(WIKI_SYNTAX.CITE.value, conv_text).group(0)
        if re.search(WIKI_SYNTAX.VERTICAL_BAR.value, corresStr):
            convertedStr = re.split(WIKI_SYNTAX.VERTICAL_BAR.value, corresStr)[1]
            conv_text = conv_text.replace(corresStr, convertedStr)

    # Vertical bar
    conv_text = re.sub(WIKI_SYNTAX.VERTICAL_BAR.value, "", conv_text)

    # etc
    conv_text = re.sub(r"}}", "", conv_text)
    conv_text = re.sub(r"{{", "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.DEL_ROW_SPAN.value, "", conv_text)
    conv_text = re.sub(WIKI_SYNTAX.DEL_COL_SPAN.value, "", conv_text)
    conv_text = re.sub(r"\[\[", "", conv_text)

    # 2022.07.04
    conv_text = re.sub(WIKI_SYNTAX.REFERENCE.value, "", conv_text)
    # <gallery>, </gallery>
    conv_text = re.sub(WIKI_SYNTAX.GALLERY.value, "", conv_text)
    # display=title
    conv_text = conv_text.replace("display=title", "")
    # <small>, </small>
    conv_text = re.sub(WIKI_SYNTAX.SMALL.value, "", conv_text)

    return conv_text.strip()

#==============================================================================
def filter_valid_paragraph(split_parag_data: List[SPLIT_PARAG],
                           valid_parag_info: List[bool]):
#==============================================================================
    ret_wiki_page_data_list: List[SPLIT_PARAG] = []

    split_data_size = len(split_parag_data)
    valid_parag_info_size = len(valid_parag_info)

    # check size
    assert split_data_size == valid_parag_info_size, f"{split_data_size} : {valid_parag_info_size}"

    for split_data, b_valid_info in zip(split_parag_data, valid_parag_info):
        if not b_valid_info:
            continue
        ret_wiki_page_data_list.append(copy.deepcopy(split_data))

    return ret_wiki_page_data_list

#==============================================================================
def check_valid_paragraph_list(src_data: List[SPLIT_PARAG]):
#==============================================================================
    '''
        @NOTE
            최소 단위의 문단을 찾는 함수
    '''
    # check symbol count
    doc_sym_count_list: List[int] = [x.sym_cnt for x in src_data]

    # valid paragraph title
    b_valid_sym = [True for _ in range(len(doc_sym_count_list))]

    if 0 >= len(src_data):
        return b_valid_sym

    for sym_idx, sym_count in enumerate(doc_sym_count_list):
        if 0 == sym_idx:
            continue

        prev_sym_cnt = doc_sym_count_list[sym_idx-1]
        if prev_sym_cnt < sym_count:
            b_valid_sym[sym_idx-1] = False

    # TEST
    # print(b_valid_sym)
    # print(doc_sym_count_list)
    # for a, b in zip(doc_sym_count_list, b_valid_sym):
    #     print(a, " : ", b)
    # input()

    return b_valid_sym

#==============================================================================
def split_minimum_paragraph(doc_text: str= ""):
# ==============================================================================
    paragraph_list: List[SPLIT_PARAG] = []

    doc_split_text = doc_text.split("\n")

    symbol_cnt = 0
    parag_title = ""
    body_text = []
    is_added = False

    for doc_line in doc_split_text:
        if re.search(WIKI_SYNTAX.PARAG_TITLE.value, doc_line):
            if is_added: # initial
                add_split_parag = SPLIT_PARAG(sym_cnt=symbol_cnt,
                                              title=parag_title,
                                              text_list=body_text)
                paragraph_list.append(copy.deepcopy(add_split_parag))

                # init
                symbol_cnt = 0
                parag_title = ""
                body_text.clear()

            symbol_cnt = len(list(filter(lambda x: x == "=", doc_line)))
            parag_title = doc_line.replace("=", "").strip()
            is_added = True
        else:
            if is_added:
                body_text.append(doc_line)

    # 남은 데이터
    if 0 < len(body_text):
        left_parag_data = SPLIT_PARAG(sym_cnt=symbol_cnt,
                                      title=parag_title, text_list=body_text)
        paragraph_list.append(copy.deepcopy(left_parag_data))

    return paragraph_list

#==============================================================================
def read_wiki_doc(src_path: str=""):
#==============================================================================
    print(f"[parse_code][read_wiki_doc] src_path: {src_path}")

    document = ET.parse(src_path)
    root = document.getroot()
    doc_count = 0
    for page in root.iter(tag="page"):
        doc_count += 1

        title_tag = page.find("title")
        revision_tag = page.find("revision")
        text_tag = revision_tag.find("text")

        title = title_tag.text
        text = text_tag.text

        if 0 == (doc_count % 1000):
            print(f"{doc_count} is processing... - {title}")

        yield (title, text)

#==============================================================================
def remove_mediawiki_tag(src_path: str=""):
#==============================================================================
    if not os.path.exists(src_path):
        print(f"[parse_code][remove_mediawiki_tag] ERR - Not Exists: {src_path}")
        return

    with open(doc_path, mode="r", encoding="utf-8") as f:
        a = f.readlines()
        a[0] = "<mediawiki>\n"

        with open("./web_dump/conv_kowiki-latest-pages-articles.xml", mode="w", encoding="utf-8") as wf:
            wf.writelines(a)

### TEST ###
if "__main__" == __name__:
    print(f"[parse_code][main] TEST")

    doc_path = "./web_dump/conv_kowiki-latest-pages-articles.xml"
    parse_wiki_doc(doc_path)