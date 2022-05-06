import pickle


from merge_info import Merge_Data

#===============================================================
def like_gans_task_func(info_box_item: Merge_Data):
    idx2title_dict = {i: t for t, i in info_box_item.title_idx_pair}

    # 테이블 첫 column에 document title을 넣음
    column_head_str = "구분"
    info_box_item.table[0].insert(0, column_head_str)

    # 각 row의 첫 열에 title을 넣음
    for r_idx, row in enumerate(info_box_item.table[1:]):
        data_idx = row[-1]
        row.insert(0, idx2title_dict[data_idx])

    #

    return

### MAIN ###
if "__main__" == __name__:
    print(f"[final_task][__main__] START !")

    # LOAD File
    info_box_list = []
    with open("./slice_merge_info_box.pkl", mode="rb") as slice_file:
        info_box_list = pickle.load(slice_file)
        print(f"[final_task][__main__] LOAD - slice_info_list: {len(info_box_list)}")

    for info_box_item in info_box_list:
        like_gans_task_func(info_box_item)
        break