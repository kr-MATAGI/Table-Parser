import re
import os
import copy
import ijson
import pickle

from dataclasses import dataclass, field
from typing import List

from namu_syntax import NAMU_RE, ModifyHTMLTags
from namu_table import PreprocessingTable, remove_namu_syntax, clear_link_syntax_in_table, remove_empty_cells, remove_short_rows

#============================================================
@dataclass
class Classify_Data:
    '''
    @NOTE
        table -> 2D List [ [row1(col_1, col_2, ...)], ... ]
    '''
    title: str = ""
    table: List[List[str]] = field(default_factory=list)
    body_text: str = ""

    link_word_list: List[str] = field(default_factory=list)

#============================================================
class Namu_Parser:
    def __init__(self, src_path: str):
        self.src_path = src_path
        if not os.path.exists(self.src_path):
            print(f"[Namu_Parser][__init__] ERR - Not Exists : {self.src_path}")

    def _convert_table_colspan_token(self, table):
        retRowList = []
        for row in table:
            if re.search(NAMU_RE.OLD_COL_SPAN.value, row):
                newRow = row
                colSpanList = re.findall(NAMU_RE.OLD_COL_SPAN.value, row)

                for colSpan in colSpanList:
                    spanCnt = len(re.findall(NAMU_RE.ROW_SPLIT.value, colSpan))
                    convStr = '||<-%s>' % spanCnt
                    newRow = row.replace(colSpan, convStr)

                retRowList.append(newRow)
            else:
                retRowList.append(row)

        return retRowList

    def parse_namu_json(self):
        print(f"[Namu_Parser][__init__] Parse Target: {self.src_path}")

        with open(self.src_path, mode="r", encoding="utf-8") as src_file:
            parser = ijson.parse(src_file)

            ret_dict = {}
            is_new_key = False
            for prefix, event, value in parser:
                if ("item", "start_map") == (prefix, event):
                    is_new_key = True
                elif prefix.endswith('.title') and is_new_key:
                    ret_dict["title"] = value
                    ret_dict["text"] = []
                elif prefix.endswith(".text"):
                    ret_dict["text"].append(value)
                elif ("item", "end_map") == (prefix, event):
                    yield ret_dict
                    is_new_key = False
                    ret_dict.clear()

    def classify_info_box_and_text(self, doc_text: List[str], doc_title: str):
        info_box = [] # table
        body_text = []

        if 0 >= len(doc_text):
            print(f"[Namu_Parser][classify_info_box_and_text] ERROR - {doc_title} doc_text.len is 0")
            return

        raw_text = doc_text[0].split("\n")
        is_insert_info_box = True
        for raw_line in raw_text:
            if re.search(NAMU_RE.PARAGRAPH.value, raw_line):
                if is_insert_info_box:
                    is_insert_info_box = False # info box 외 다른 테이블을 인식하지 않게
            elif re.search(NAMU_RE.ROW_SPLIT.value, raw_line):
                if is_insert_info_box: # info box만 테이블 데이터로 활용
                    info_box.append(raw_line)
            else:
                if 0 < len(info_box) and "" == raw_line:
                    is_insert_info_box = False
                body_text.append(raw_line.replace("\n", "")) # 모든 단락 텍스트

        # filter - empty line in body_text
        body_text = list(filter(lambda x: True if 0 < len(x) else False, body_text))
        # convert - colspan (||||||...)
        info_box = self._convert_table_colspan_token(info_box)
        return info_box, body_text


def extract_sentences_relate_link_word(info_box: List[List[str]], body_text: str):
    ret_body_text = ""

    # info box에서 링크 단어 추출
    re_link_word = r"\[\[[^\]]+\]\]"
    all_link_word_list = []
    for row in info_box:
        for col in row:
            link_word_list = re.findall(re_link_word, col)
            all_link_word_list.extend(list(filter(lambda x: True if re.search(re_link_word, x) else False, link_word_list)))
    all_link_word_list = list(set(all_link_word_list))

    # 본문에서 링크 단어를 포함하는 문장 추출
    target_sent_list = []
    for paragraph_text in body_text:
        split_paragraph = paragraph_text.split(".")
        split_paragraph = list(filter(lambda x: True if 0 < len(x) else False, split_paragraph))
        for sent in split_paragraph:
            if re.search(re_link_word, sent):
                target_sent_list.append(sent.strip())

    link_word_rel_sent = []
    for sent in target_sent_list:
        check_list = list(filter(lambda x: True if x in sent else False, all_link_word_list))
        if 0 < len(check_list):
            link_word_rel_sent.append(sent.strip())
    link_word_rel_sent = list(set(link_word_rel_sent))
    ret_body_text = link_word_rel_sent

    return ret_body_text, all_link_word_list

#============================================================
if "__main__" == __name__:
    json_path = "../../data/namuwiki_20210301.json"

    # write file
    IS_EG_WRITE_FILE = True
    write_file = open("./output.txt", mode="w", encoding="utf-8")

    all_results = []
    namu_parser = Namu_Parser(src_path=json_path)
    for doc_idx, doc_dict in enumerate(namu_parser.parse_namu_json()):
        if 0 == (doc_idx % 1000):
            print(f"{doc_idx} Processing... doc_title: {doc_dict['title']}")

        classify_data = Classify_Data(title=doc_dict["title"])
        classify_data.table, classify_data.body_text = namu_parser.classify_info_box_and_text(doc_text=doc_dict["text"],
                                                                                              doc_title=doc_dict["title"])
        # ignore - empty info_box
        if 0 >= len(classify_data.table):
            continue

        classify_data.table = ModifyHTMLTags(classify_data.table)
        classify_data.table = PreprocessingTable(classify_data.table)
        classify_data.body_text = remove_namu_syntax(srcList=classify_data.body_text)

        # 본문에서 info box의 링크 단어를 포함한 문장을 추출
        classify_data.body_text, link_word_list = extract_sentences_relate_link_word(info_box=classify_data.table,
                                                                                     body_text=classify_data.body_text)
        # ignore - empty body_text and info box
        if 0 >= len(classify_data.body_text) or 0 >= len(classify_data.table):
            continue

        # 테이블의 데이터에서 링크 단어를 표시하는 '[[', ']]'를 삭제
        classify_data.table = clear_link_syntax_in_table(classify_data.table)
        # table data 재처리
        classify_data.table = remove_empty_cells(classify_data.table)
        classify_data.table = remove_short_rows(classify_data.table)

        # 2022.05.06 - link word 추가
        classify_data.link_word_list = link_word_list

        all_results.append(classify_data)

        if IS_EG_WRITE_FILE:
            write_file.write(classify_data.title + "\n")
            write_file.write("TABLE: \n")
            for row in classify_data.table:
                for col in row:
                    write_file.write(col + "\t")
                write_file.write("\n")

            write_file.write("\nLINK_WORD: \n")
            for link_word in classify_data.link_word_list:
                write_file.write(link_word + "\t")

            write_file.write("\nSentences: \n")
            for sent in classify_data.body_text:
                write_file.write(sent + "\n")
            write_file.write("\n")
    write_file.close()

    # Write *.pkl file
    with open("./namu_info_box.pkl", mode="wb") as pkl_file:
        pickle.dump(all_results, pkl_file)

    # Check count
    print(f"Complete - {len(all_results)}")
