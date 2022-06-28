from builtins import str

import ijson
import copy
import xml.etree.ElementTree as ET
import re
import os

from typing import List
from data_def import Wiki_Page, TT_Pair, SPLIT_PARAG
from re_def import WIKI_SYNTAX

### METHOD
#==============================================================================
def parse_wiki_doc(src_path: str=""):
#==============================================================================
    if not os.path.exists(src_path):
        print(f"[parse_code][parse_wiki_doc] ERR - Not Exists: {src_path}")
        return

    for doc_title, doc_text in read_wiki_doc(src_path):
        # wiki_page_data = Wiki_Page(title=doc_title)

        # split
        res_split_body = split_minimum_paragraph(doc_text)

        # divide by max_sym_cnt
        valid_text_list = divide_text_by_sym_cnt(res_split_body)

#==============================================================================
def divide_text_by_sym_cnt(src_data: List[SPLIT_PARAG]):
#==============================================================================
    ret_valid_text: List[str] = []

    for split_parag in src_data:
        is_extract = False
        for body_text in split_parag.text_list:
            if is_extract:
                ret_valid_text.append(body_text)

            elif re.search(WIKI_SYNTAX.PARAG_TITLE.value, body_text):
                sym_cnt = len(list(filter(lambda x: x == "=", body_text)))
                if split_parag.max_sym_cnt <= sym_cnt:
                    is_extract = True

    return ret_valid_text

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

    doc_path = "./web_dump/kowiki-latest-pages-articles2.xml"
    parse_wiki_doc(doc_path)