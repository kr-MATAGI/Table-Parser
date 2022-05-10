import pickle
import copy
import re
import random
import numpy as np
import time

from merge_info import Merge_Data
from typing import List, Tuple
from dataclasses import dataclass, field

from transformers import AutoTokenizer

#===============================================================
@dataclass
class Table_Sent_Data:
    origin_table: List[List[str]] = field(default_factory=list)
    replace_table_list: List[List[List[str]]] = field(default_factory=list)
    sent_list: List[str] = field(default_factory=list)

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

    # 테이블 첫 column에 document title을 넣음 - NOT USED YET....
    # column_head_str = "DOC_TITLE"
    # info_box_item.table[0].insert(0, column_head_str)
    #
    # # 각 row의 첫 열에 title을 넣음
    # for r_idx, row in enumerate(info_box_item.table[1:]):
    #     data_idx = row[-1]
    #     row.insert(0, idx2title_dict[data_idx])

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

def make_replace_table_dict(tokenizer, table: List[List[str]], sentence: str, max_len: int=512):
    ret_dict = {
        "input_ids": [],
        "row_ids": [],
        "col_ids": [],
        "segment_ids": []
    }

    tokens = tokenizer.tokenize(sentence)
    tokens.insert(0, "[CLS]")
    tokens.append("[SEP]")

    table_row_len = len(table)
    table_col_len = len(table[0])

    # use a origin table
    row_ids = []
    col_ids = []
    segment_ids = []
    origin_flatten_table = []
    for r_idx, ori_row in enumerate(table):
        for c_idx, ori_col in enumerate(ori_row):
            col_tokens = tokenizer.tokenize(ori_col)
            row_ids += [(r_idx + 1) for _ in range(len(col_tokens))]
            col_ids += [(c_idx + 1) for _ in range(len(col_tokens))]
            origin_flatten_table.extend(col_tokens)

    empty_row_col_ids = [0] * len(tokens)
    row_ids = empty_row_col_ids + row_ids
    col_ids = empty_row_col_ids + col_ids
    segment_ids = [0] * len(tokens)
    segment_ids += [1] * len(origin_flatten_table)
    tokens += origin_flatten_table

    valid_len = len(tokens)
    if max_len < valid_len:
        tokens = tokens[:max_len - 1]
        tokens.append("[SEP]")
        row_ids = row_ids[:max_len]
        col_ids = col_ids[:max_len]
        segment_ids = segment_ids[:max_len]
        valid_len = max_len
    else:
        tokens += ["[PAD]"] * (max_len - valid_len)
        row_ids += [0] * (max_len - valid_len)
        col_ids += [0] * (max_len - valid_len)
        segment_ids += [0] * (max_len - valid_len)
    input_ids = tokenizer.convert_tokens_to_ids(tokens)

    ret_dict["input_ids"].append(input_ids)
    ret_dict["row_ids"].append(row_ids)
    ret_dict["col_ids"].append(col_ids)
    ret_dict["segment_ids"].append(segment_ids)

    return ret_dict

def make_table_npy(src_data: List[Table_Sent_Data], model_name: str, max_len: int=512):
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    npy_make_dict = {
        "input_ids": [],
        "labels": [],
        "row_ids": [],
        "col_ids": [],
        "segment_ids": []
    }

    # convert data to numpy
    for proc_idx, src_item in enumerate(src_data):
        if 0 == (proc_idx % 100):
            print(f"{proc_idx} Processing...")

        if 0 >= len(src_item.replace_table_list):
            continue

        for src_sent in src_item.sent_list:
            origin_npy_dict = make_replace_table_dict(tokenizer, table=src_item.origin_table,
                                                      sentence=src_sent, max_len=512)

            # Insert Origin Table
            npy_make_dict["input_ids"].extend(origin_npy_dict["input_ids"])
            npy_make_dict["row_ids"].extend(origin_npy_dict["row_ids"])
            npy_make_dict["col_ids"].extend(origin_npy_dict["col_ids"])
            npy_make_dict["segment_ids"].extend(origin_npy_dict["segment_ids"])
            npy_make_dict["labels"].append(1) # True

            # Insert Replace Table
            rand_idx = random.randrange(0, len(src_item.replace_table_list))
            replace_npy_dict = make_replace_table_dict(tokenizer, table=src_item.replace_table_list[rand_idx],
                                                       sentence=src_sent, max_len=512)
            npy_make_dict["input_ids"].extend(replace_npy_dict["input_ids"])
            npy_make_dict["row_ids"].extend(replace_npy_dict["row_ids"])
            npy_make_dict["col_ids"].extend(replace_npy_dict["col_ids"])
            npy_make_dict["segment_ids"].extend(replace_npy_dict["segment_ids"])
            npy_make_dict["labels"].append(0) # False

    # Check Size
    print(f"npy_make_dict.input_ids: {len(npy_make_dict['input_ids'])}")
    print(f"npy_make_dict.row_ids: {len(npy_make_dict['row_ids'])}")
    print(f"npy_make_dict.col_ids: {len(npy_make_dict['col_ids'])}")
    print(f"npy_make_dict.segment_ids: {len(npy_make_dict['segment_ids'])}")
    print(f"npy_make_dict.labels: {len(npy_make_dict['labels'])}")

    assert len(npy_make_dict['input_ids']) == len(npy_make_dict['input_ids'])
    assert len(npy_make_dict['input_ids']) == len(npy_make_dict['row_ids'])
    assert len(npy_make_dict['input_ids']) == len(npy_make_dict['col_ids'])
    assert len(npy_make_dict['input_ids']) == len(npy_make_dict['segment_ids'])

    # Save npy
    all_data_npy_stack = np.stack([npy_make_dict["input_ids"], npy_make_dict["segment_ids"],
                                   npy_make_dict["row_ids"], npy_make_dict["col_ids"]], axis=-1)
    print(f"all_data_npy_stack.shape: {all_data_npy_stack.shape}")
    print(f"labels.shape: {npy_make_dict['labels']}")

    np.save("./npy/all_ids", all_data_npy_stack)
    np.save("./npy/label", npy_make_dict['labels'])
    print("[final_task.py][make_table_npy] Complete - SAVE NPY !")


### MAIN ###
if "__main__" == __name__:
    print(f"[final_task][__main__] START !")

    is_make_data_set = False
    if is_make_data_set:
        # LOAD File
        info_box_list = []
        with open("./slice_merge_info_box.pkl", mode="rb") as slice_file:
            info_box_list = pickle.load(slice_file)
            print(f"[final_task][__main__] LOAD - slice_info_list: {len(info_box_list)}")

        save_data_list = [] # List[Table_Info_Set]
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

            # save list
            table_info_set = Table_Sent_Data(origin_table=origin_table,
                                             replace_table_list=replaced_table_list,
                                             sent_list=sent_list)
            save_data_list.append(table_info_set)
        print(total_replace_table_cnt)

        with open("./task_1_data.pkl", mode="wb") as write_file:
            pickle.dump(save_data_list, write_file)
            print(f"[final_task.py][__main__] Save - List.Len: {len(save_data_list)}")

    #### MAKE *.npy
    is_make_table_npy = True
    if is_make_table_npy:
        start_time = time.time()

        src_data = []
        with open("./task_1_data.pkl", mode="rb") as load_file:
            src_data = pickle.load(load_file)
            print(f"[final_task.py][make_table_npy] LOAD FILE - {len(src_data)}")
        make_table_npy(src_data=src_data, model_name="monologg/kobigbird-bert-base", max_len=512)

        print(f"Processing Time... : {time.time() - start_time}")
