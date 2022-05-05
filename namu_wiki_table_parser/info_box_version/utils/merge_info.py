import math
import pickle
import copy
import pandas as pd
import time

from namu_parser import Classify_Data
from typing import List, Tuple
from dataclasses import dataclass, field

#====================================================================
@dataclass
class Merge_Data:
    title_idx_pair: List[Tuple[str, int]] = field(default_factory=list) # (Title, info set index)
    table: List[List[str]] = field(default_factory=list)
    sent_list: List[Tuple[str, int]] = field(default_factory=list) # (sent, info set index)

#====================================================================
def filter_junk_table(data: Classify_Data):
    # Check 1 - 2줄로 이루어진 table
    if 2 >= len(data.table):
        return False

    # Check 2 - Not Yet...

    return True
#====================================================================
def fit_table_column_max_len(data: Classify_Data):
    # check max len
    max_col_len = -1
    for row in data.table:
        max_col_len = max_col_len if max_col_len > len(row) else len(row)

    # fill data
    for row in data.table:
        if max_col_len > len(row):
            last_item = row[-1]
            row.extend([last_item] * (max_col_len - len(row)))

    return data

#====================================================================
def rotate_right_table(data: Classify_Data):
    row_len = len(data.table)
    col_len = len(data.table[0])

    rotate_table = []
    for c_idx in range(col_len):
        new_row = []
        for r_idx in range(row_len):
            new_row.append(data.table[r_idx][c_idx])
        rotate_table.append(new_row)
    data.table = rotate_table

    return data

#====================================================================
### MAIN ###
if "__main__" == __name__:
    start_time = time.time()
    print(f"[reverse_index_dict][__main__] MAIN !")

    # LOAD pkl file
    info_box_list = []
    with open("./namu_info_box.pkl", mode="rb") as pkl_file:
        info_box_list = pickle.load(pkl_file)
        print(f"[reverse_index_dict][__main__] LOAD Size - {len(info_box_list)}")

    # Filter junk table
    print(f"BEFORE filtering - info box size: {len(info_box_list)}")
    info_box_list = list(filter(filter_junk_table, info_box_list))
    print(f"AFTER filtering - info box size: {len(info_box_list)}")

    # Fit table column max len
    info_box_list = list(map(fit_table_column_max_len, info_box_list))

    # Rotate right direction
    info_box_list = list(map(rotate_right_table, info_box_list))

    # Make table HEAD dictionary
    merge_data_list = []
    head_dict = {}
    for info_idx, info_box_info in enumerate(info_box_list):
        table_head_list = info_box_info.table[0]
        table_head_list = list(map(lambda x: x.strip(), table_head_list))

        for head_word in table_head_list:
            if head_dict.get(head_word) is None:
                head_dict[head_word] = [info_idx]
            else:
                head_dict[head_word].append(info_idx)

    # filter dictionary by value size
    print(f"BEFORE filtering - head_dict.keys() size: {len(head_dict.keys())}")
    head_dict = dict(filter(lambda item: 2 <= len(item[1]), head_dict.items()))
    print(f"AFTER filtering - head_dict.keys() size: {len(head_dict.keys())}")

    # table combination and vstack
    check_used_info_idx_set = []

    # 만들어진 table head_dict을 통해 merge table에 쓰일 head를 계산한다.
    DICT_CRITERIA_SCORE = 0.5 # head_val 테이블에서 얼마나 등장하는지
    HEAD_CRITERIA_SCORE = 0.5 # 기준 되는 merge table head를 얼마나 포함하고 있는지
    for proc_idx, (head_key, head_val) in enumerate(head_dict.items()):
        if 0 == (proc_idx % 100):
            print(f"{proc_idx} Processing... : {head_key}")
        total_info_size = len(head_val)

        table_head_dict = {}
        for data_idx in head_val:
            for head in info_box_list[data_idx].table[0]:
                if table_head_dict.get(head) is None:
                    table_head_dict[head] = 1
                else:
                    table_head_dict[head] += 1

        table_head_dict = sorted(table_head_dict.items(), key=lambda item: item[1], reverse=True)
        # head_dict에서 일정 수준 이상의 val를 가진 것을 자르기 위함
        dict_base_line_score = math.floor(len(head_val) * DICT_CRITERIA_SCORE)
        merge_table_head_list = [x[0] for x in table_head_dict if dict_base_line_score <= x[1]]
        merge_table_head_list.append("INFO_IDX") # 나중에 테이블을 일정 크기별로 자를 때 출처를 알기 위해

        # 정해진 merge table head에 얼마나 head가 일치하는지
        head_fit_base_line_score = math.floor(len(merge_table_head_list) * HEAD_CRITERIA_SCORE)
        merge_row_list = [] # merge table의 ROW들
        use_idx_list = []
        for data_idx in head_val:
            curr_df = pd.DataFrame(info_box_list[data_idx].table[1:], columns=info_box_list[data_idx].table[0])
            fit_score = len(list(filter(lambda x: True if x in merge_table_head_list[:-1] else False, info_box_list[data_idx].table[0])))
            if head_fit_base_line_score <= fit_score:
                continue

            use_idx_list.append(data_idx)
            for _, row_item in curr_df.iterrows():
                # merge table head에 맞게 행을 생성
                merge_row = []
                for merge_head in merge_table_head_list:
                    col_item = row_item.get(merge_head, "")
                    if type(col_item) is not str:
                        print(col_item)
                        print("\n")
                        print(curr_df)
                        input()

    # end, head_dict loop

    print(f"Complete - Make Merge Info Box Table: {len(merge_data_list)} !, TIME: {time.time() - start_time}")

    # Write File and Check Count
    table_count = 0
    sent_count = 0
    with open("./merge_info_box.pkl", mode="wb") as pkl_file:
        pickle.dump(merge_data_list, pkl_file)
    with open("./merge_output.txt", mode="w", encoding="utf-8") as output_txt:
        for target_data in merge_data_list:
            output_txt.write("TITLE: \n")
            for x, y in target_data.title_idx_pair:
                output_txt.write("("+x+"-"+str(y)+")\t")
            output_txt.write("\n\nTABLE:\n")

            table_count += 1
            for r in target_data.table:
                for c in r:
                    output_txt.write(str(c)+"\t")
                output_txt.write("\n")
            output_txt.write("\n\nSENT:\n")

            sent_count += len(target_data.sent_list)
            for s, i in target_data.sent_list:
                output_txt.write("(" + s + ", " + str(i) + ")")
            output_txt.write("\n\n")
    # PRINT TABLE, SENT COUNT
    print(f"COUNT - table: {table_count}, sent: {sent_count}")