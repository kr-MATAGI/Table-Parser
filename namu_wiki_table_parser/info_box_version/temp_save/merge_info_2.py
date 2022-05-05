import math
import pickle
import copy
import pandas as pd
import time

from namu_parser import Classify_Data
from typing import List, Tuple
from dataclasses import dataclass, field


# ====================================================================
@dataclass
class Merge_Data:
    title_idx_pair: List[Tuple[str, int]] = field(default_factory=list)  # (Title, info set index)
    table: List[List[str]] = field(default_factory=list)
    sent_list: List[Tuple[str, int]] = field(default_factory=list)  # (sent, info set index)


# ====================================================================
def filter_junk_table(data: Classify_Data):
    # Check 1 - 2줄로 이루어진 table
    if 2 >= len(data.table):
        return False

    # Check 2 - Not Yet...

    return True


# ====================================================================
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


# ====================================================================
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


# ====================================================================
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
    HEAD_CRITERIA_SCORE = 0.5  # head_val 테이블에서 얼마나 등장하는지
    ROW_INFO_CRITERIA_SCORE = 0.5  # row가 얼만큼 merge table에 정보를 채웠는지
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
        head_score_base_line = math.floor(len(head_val) * HEAD_CRITERIA_SCORE)
        merge_table_head_list = list(map(lambda x: x[0] if head_score_base_line <= x[1] else None, table_head_dict))
        merge_table_head_list = list(filter(lambda x: True if x is not None else False, merge_table_head_list))
        merge_table_head_list.append("INFO_IDX")  # 출처를 알고 나중에 자를 때 쓰기 위해

        # 정해진 merge table HEAD에 따라 info box table의 데이터를 삽입
        head_fit_base_line = math.floor(len(merge_table_head_list) * HEAD_CRITERIA_SCORE)
        merge_row_list = []
        use_info_idx_list = []
        for data_idx in head_val:
            info_data_df = pd.DataFrame(info_box_list[data_idx].table[1:], columns=info_box_list[data_idx].table[0])
            for _, row in info_data_df.iterrows():
                # keys()로 먼저 merge table head에 얼만큼 해당하는지 판단하고 continue 결정
                fit_score = len(list(filter(lambda x: True if x in merge_table_head_list else False, row.keys())))
                if head_fit_base_line > fit_score:
                    continue
                use_info_idx_list.append(data_idx)
                # merge head를 key로써 값을 찾아 merge table의 새로운 행을 만듦
                merge_row = []
                for merge_head in merge_table_head_list:
                    extract_str = row.get(merge_head, "")
                    if type(extract_str) is not str:
                        merge_row.append("")
                    elif extract_str != merge_head:
                        merge_row.append(extract_str)
                    else:
                        merge_row.append("")
                insert_count = len(list(filter(lambda x: True if x != "" else False, merge_row)))
                row_insert_base_line = math.floor(len(merge_table_head_list) * ROW_INFO_CRITERIA_SCORE)
                if row_insert_base_line <= insert_count:
                    merge_row[-1] = data_idx  # 맨 마지막은 info idx
                    merge_row_list.append(merge_row)
        ## end, head_val loop

        merge_row_list.insert(0, merge_table_head_list)

        use_info_idx = list(set(use_info_idx_list))
        use_info_idx.sort()

        # 이미 사용했던 idx 조합은 최종 결과물에 넣지 않는다.
        if use_info_idx in check_used_info_idx_set:
            continue
        check_used_info_idx_set.extend(use_info_idx)

        # info box에서 사용된 문장 뽑아내기
        merge_table_sent_list = []
        for data_idx in use_info_idx_list:
            for body_text in info_box_list[data_idx].body_text:
                merge_table_sent_list.append((body_text, data_idx))

        # 사용된 title과 info idx pair 만들기
        title_info_idx_pair = []
        for data_idx in use_info_idx_list:
            title_info_idx_pair.append((info_box_list[data_idx].title, data_idx))

        # make merge result
        merge_result = Merge_Data(title_idx_pair=title_info_idx_pair,
                                  table=merge_row_list,
                                  sent_list=merge_table_sent_list)
        merge_data_list.append(merge_result)
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
                output_txt.write("(" + x + "-" + str(y) + ")\t")
            output_txt.write("\n\nTABLE:\n")

            table_count += 1
            for r in target_data.table:
                for c in r:
                    output_txt.write(str(c) + "\t")
                output_txt.write("\n")
            output_txt.write("\n\nSENT:\n")

            sent_count += len(target_data.sent_list)
            for s, i in target_data.sent_list:
                output_txt.write("(" + s + ", " + str(i) + ")")
            output_txt.write("\n\n")
    # PRINT TABLE, SENT COUNT
    print(f"COUNT - table: {table_count}, sent: {sent_count}")