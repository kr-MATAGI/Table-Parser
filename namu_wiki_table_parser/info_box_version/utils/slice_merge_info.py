import pickle
import copy
import time
from merge_info import Merge_Data
from typing import List

def slice_merge_table(merge_info_list: List[Merge_Data], base_line_len: int = 10):
    print(f"[slice_merge_info][slice_merge_table] merge_info_list size : {len(merge_info_list)}")

    ret_list = []
    for proc_idx, merge_info in enumerate(merge_info_list):
        if 0 == (proc_idx % 100):
            print(f"{proc_idx} Processing... ")

        if base_line_len >= len(merge_info.table): # 길지 않아서 기준 충족
            ret_list.append(merge_info)
            continue

        # Extract HEAD
        slice_table_list = []
        head_list = merge_info.table[0]
        table_rows = merge_info.table[1:]

        new_table = []
        while True:
            if base_line_len <= len(new_table):
                # 현재까지 모인거
                new_table.insert(0, head_list)
                slice_table_list.append(copy.deepcopy(new_table))
                new_table.clear()

            if base_line_len >= len(table_rows):
                # 현재까지 모인거
                if 0 < len(new_table):
                    new_table.insert(0, head_list)
                    slice_table_list.append(copy.deepcopy(new_table))
                    new_table.clear()

                # 남은 거
                if 0 < len(table_rows):
                    new_table.append(head_list)
                    new_table.extend(table_rows)
                    slice_table_list.append(copy.deepcopy(new_table))
                    new_table.clear()
                break

            top_row = table_rows[0]
            new_table.append(copy.deepcopy(top_row))
            table_rows.remove(top_row)

        # 원래 Merge Data에서 title과 sentences를 맵핑
        origin_title_list = merge_info.title_idx_pair
        origin_sent_list = merge_info.sent_list
        for slice_table in slice_table_list:
            new_merge_data = Merge_Data()

            table_rows = slice_table[1:]
            last_col_data_list = [x[-1] for x in table_rows]
            extract_title_list = [x for x in origin_title_list if x[-1] in last_col_data_list]
            extract_sent_list = [x for x in origin_sent_list if x[-1] in last_col_data_list]

            new_merge_data.title_idx_pair = extract_title_list
            new_merge_data.table = slice_table
            new_merge_data.sent_list = extract_sent_list

            ret_list.append(new_merge_data)

    return ret_list


if "__main__" == __name__:
    print(f"[slice_merge_info][__main__] START !")

    src_merge_info_list = []
    with open("./merge_info_box.pkl", mode="rb") as src_file:
        src_merge_info_list = pickle.load(src_file)
        print(f"[slice_merge_info][__main__] LOAD Size: {len(src_merge_info_list)}")

    # src_merge_info_list = src_merge_info_list[:1] # FOR TEST
    results = slice_merge_table(merge_info_list=src_merge_info_list, base_line_len=10)
    print(f"[slice_merge_info][__main__] Complete Size: {len(results)}")

    # write
    with open("./slice_merge_info_box.pkl", mode="wb") as write_file:
        pickle.dump(results, write_file)

    print(f"[slice_merge_info][__main__] Complete write file !")

