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
    title_idx_pair: List[Tuple[str, int]] = field(default_factory=list)
    table: List[List[str]] = field(default_factory=list)
    sent_list: List[str] = field(default_factory=list)

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
    check_used_idx_set = []
    ERR_CNT = 0
    # 가장 많이 공통되는 head를 찾는 코드
    for h_key, h_val in head_dict.items():
        freq_head_dict = {}
        for info_idx in h_val:
            head_list = info_box_list[info_idx].table[0]
            head_str = "\t".join(head_list)
            if freq_head_dict.get(head_str) is None:
                freq_head_dict[head_str] = 1
            else:
                freq_head_dict[head_str] += 1
        max_head_comb = max(freq_head_dict, key=freq_head_dict.get).split("\t")

        # Make Stacked Table !
        new_df = pd.DataFrame([], columns=max_head_comb)
        used_idx = []
        for info_idx in h_val:
            curr_head_list = info_box_list[info_idx].table[0]
            is_all_include = True
            for check_head in max_head_comb:
                if check_head not in curr_head_list:
                    is_all_include = False
                    break
            if not is_all_include: # ignore current info box
                continue

            used_idx.append(info_idx)
            used_idx.sort()
            diff_head = list(set(curr_head_list) ^ set(max_head_comb))
            if 0 == len(diff_head): # 완전일치
                try:
                    add_df = pd.DataFrame(info_box_list[info_idx].table[1:], columns=max_head_comb)
                    new_df = pd.concat([new_df, add_df], axis=0)
                except:
                    ERR_CNT += 1
            else: # 차이가 나는 열을 없앰
                add_df = pd.DataFrame(info_box_list[info_idx].table[1:], columns=curr_head_list)

                try:
                    for del_head in diff_head:
                        add_df = add_df.drop(del_head, axis=1)
                    new_df = pd.concat([new_df, add_df], axis=0)
                except Exception as err:
                    ERR_CNT += 1

        # check overlap
        if used_idx in check_used_idx_set:
            continue

        # merge body_text
        merge_body_text = []
        for u_idx in used_idx:
            merge_body_text.extend(info_box_list[u_idx].body_text)
        check_used_idx_set.append(used_idx)

        # pd.DataFrame to list
        new_table_list = [max_head_comb]
        new_table_list.extend(new_df.to_numpy().tolist())

        # append merge_data set
        merge_data_list.append(Merge_Data(used_idx_list=used_idx,
                                          table=new_table_list,
                                          sent_list=merge_body_text))
    print(len(merge_data_list))
    print("ERR - ", ERR_CNT)
    print("TIME: ", time.time() - start_time)

    # write file
    with open("./merge_output.txt", mode="w", encoding="utf-8") as write_file:
        for data in merge_data_list:
            write_file.write("TABLE:\n")
            for r in data.table:
                for c in r:
                    write_file.write(c + "\t")
                write_file.write("\n")
            write_file.write("\nSENT:\n")
            for s in data.sent_list:
                write_file.write(s + "\n")
            write_file.write("\n\n")