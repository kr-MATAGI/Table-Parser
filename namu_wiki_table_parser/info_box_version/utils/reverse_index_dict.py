import pickle
from namu_parser import Classify_Data


### MAIN ###
if "__main__" == __name__:
    print(f"[reverse_index_dict][__main__] MAIN !")

    # LOAD pkl file
    info_box_list = []
    with open("./namu_info_box.pkl", mode="rb") as pkl_file:
        info_box_list = pickle.load(pkl_file)
        print(f"[reverse_index_dict][__main__] LOAD Size - {len(info_box_list)}")

    # @TODO:...