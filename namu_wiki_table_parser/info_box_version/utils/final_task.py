import pickle
import copy
import re
import random

from merge_info import Merge_Data
from typing import List, Tuple

#===============================================================
def make_idx_table_link_word_dict(src_pair: List[Tuple[str, int]]):
    ret_dict = {}

    for lhs, rhs in src_pair:
        if ret_dict.get(rhs, None) is None:
            ret_dict[rhs] = [lhs]
        else:
            ret_dict[rhs].append(lhs)

    return ret_dict

#===============================================================
def replace_task_1(info_box_item: Merge_Data):
    idx2title_dict = {i: t for t, i in info_box_item.title_idx_pair}

    # 테이블 첫 column에 document title을 넣음
    column_head_str = "DOC_TITLE"
    info_box_item.table[0].insert(0, column_head_str)

    # 각 row의 첫 열에 title을 넣음
    for r_idx, row in enumerate(info_box_item.table[1:]):
        data_idx = row[-1]
        row.insert(0, idx2title_dict[data_idx])

    # TEST
    # for r in info_box_item.table:
    #     print(r)

    # {data_idx : linkword} dict
    data_idx_table_link_word_dict = make_idx_table_link_word_dict(info_box_item.link_word_idx_pair)

    # {data_idx : sentences} dict
    data_idx_sent_dict = make_idx_table_link_word_dict(info_box_item.sent_list)

    # 위 2개의 dict를 비교해서 바꿀 것을 만듦
    # @NOTE : lw(link word)
    mapped_data_list = [] # [ (idx, link word, sentence), .... , ]
    for lw_key, lw_val in data_idx_table_link_word_dict.items():
        key_sent_list = data_idx_sent_dict[lw_key]
        if 0 >= len(key_sent_list):
            continue

        for target_lw in lw_val:
            for target_sent in key_sent_list:
                if target_lw in target_sent: # table의 link word가 sentences에 포함되어 있다.
                    mapped_data_list.append((lw_key, target_lw, target_sent))

    # masking fake(replaced) table
    max_len = len(info_box_item.table)
    origin_table = copy.deepcopy(info_box_item.table)
    replace_table_list = []
    origin_sent_list = copy.deepcopy(info_box_item.sent_list)
    for mapped_data in mapped_data_list: # [ (idx, link word, sentence), ... , ]
        match_row_idx = -1
        for r_idx, row in enumerate(info_box_item.table[1:]):
            if mapped_data[0] != row[-1]: # 맨 뒤의 idx를 보고 Loop를 최소화
                match_row_idx = r_idx
                break

        match_col_idx = -1
        conv_mapped_link_word = mapped_data[1].replace("[[", "").replace("]]", "")
        for c_idx, col in enumerate(info_box_item.table[match_row_idx]):
            if conv_mapped_link_word in str(col):
                match_col_idx = c_idx
                break

        if -1 == match_col_idx:
            continue

        # rand replace row idx
        rand_row_idx = -1
        while True:
            rand_row_idx = random.randrange(1, max_len)
            if rand_row_idx != match_row_idx:
                break

        # replace data
        origin_word = info_box_item.table[match_row_idx][match_col_idx]
        replace_word = info_box_item.table[rand_row_idx][match_col_idx]

        # swap
        replace_table = copy.deepcopy(info_box_item.table)
        replace_table[match_row_idx][match_col_idx] = replace_word
        replace_table[rand_row_idx][match_col_idx] = origin_word

        replace_table_list.append(replace_table)


    return origin_table, replace_table_list, origin_sent_list

def remove_last_data_idx_column(table: List[List[str]]):
    for r_idx, row in enumerate(table):
        table[r_idx] = row[:-1]

def remove_link_word_syntax(src_sent_list: List[str]):
    ret_sent_list = [x[0] for x in src_sent_list]
    for s_idx, sent in enumerate(ret_sent_list):
        ret_sent_list[s_idx] = sent.replace("[[", "").replace("]]", "")

    return ret_sent_list

### MAIN ###
if "__main__" == __name__:
    print(f"[final_task][__main__] START !")

    # LOAD File
    info_box_list = []
    with open("./slice_merge_info_box.pkl", mode="rb") as slice_file:
        info_box_list = pickle.load(slice_file)
        print(f"[final_task][__main__] LOAD - slice_info_list: {len(info_box_list)}")

    total_replace_table_cnt = 0
    for info_box_item in info_box_list:
        origin_table, replaced_table_list, sent_list = replace_task_1(info_box_item)

        # remove last column (=> data_idx)
        remove_last_data_idx_column(origin_table)
        for table in replaced_table_list:
            remove_last_data_idx_column(table)

        total_replace_table_cnt += len(replaced_table_list)
        # remove "[[", "]]", and sent_list[-1] (=> data_idx)
        sent_list = remove_link_word_syntax(sent_list)
    print(total_replace_table_cnt)