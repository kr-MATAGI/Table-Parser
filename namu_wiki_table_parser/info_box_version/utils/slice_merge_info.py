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
        origin_link_word_list = merge_info.link_word_idx_pair
        for slice_table in slice_table_list:
            new_merge_data = Merge_Data()

            table_rows = slice_table[1:]
            last_col_data_list = [x[-1] for x in table_rows]
            extract_title_list = [x for x in origin_title_list if x[-1] in last_col_data_list]
            extract_sent_list = [x for x in origin_sent_list if x[-1] in last_col_data_list]

            # 2022.05.06 - link word 추가
            extract_link_word = [x for x in origin_link_word_list if x[-1] in last_col_data_list]

            new_merge_data.title_idx_pair = extract_title_list
            new_merge_data.table = slice_table
            new_merge_data.sent_list = extract_sent_list
            new_merge_data.link_word_idx_pair = extract_link_word

            ret_list.append(new_merge_data)

    return ret_list


if "__main__" == __name__:
    print(f"[slice_merge_info][__main__] START !")

    with open("./slice_merge_info_box.pkl", mode="rb") as check_file:
        a = pickle.load(check_file)
        print(len(a))

    table_count = 0
    sent_count = 0
    with open("./slice_output.txt", mode="w", encoding="utf-8") as output_txt:
        for target_data in a:
            output_txt.write("TITLE: \n")
            for x, y in target_data.title_idx_pair:
                output_txt.write("(" + x + "-" + str(y) + ")\t")
            output_txt.write("\n\nTABLE:\n")

            table_count += 1
            for r in target_data.table:
                for c in r:
                    output_txt.write(str(c) + "\t")
                output_txt.write("\n")

            output_txt.write("\n\nLINK WORD:\n")
            for lw, i in target_data.link_word_idx_pair:
                output_txt.write("(" + lw + ", " + str(i) + ")")

            output_txt.write("\n\nSENT:\n")
            sent_count += len(target_data.sent_list)
            for s, i in target_data.sent_list:
                output_txt.write("(" + s + ", " + str(i) + ")")
            output_txt.write("\n\n")
    print(f"table count : {table_count}")
    print(f"sent count : {sent_count}")
    exit()

    src_merge_info_list = []
    with open("./merge_info_box.pkl", mode="rb") as src_file:
        src_merge_info_list = pickle.load(src_file)
        print(f"[slice_merge_info][__main__] LOAD Size: {len(src_merge_info_list)}")

    # src_merge_info_list = src_merge_info_list[:1] # FOR TEST
    results = slice_merge_table(merge_info_list=src_merge_info_list, base_line_len=5)
    print(f"[slice_merge_info][__main__] Complete Size: {len(results)}")

    # write
    with open("./slice_merge_info_box.pkl", mode="wb") as write_file:
        pickle.dump(results, write_file)

    print(f"[slice_merge_info][__main__] Complete write file !")

