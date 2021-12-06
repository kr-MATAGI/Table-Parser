from transformers import TapasForMaskedLM
from transformers import TapasTokenizer
from transformers import AdamW

import torch
import datasets
import numpy as np

### Method
def LoadNpyFile(path):
    retNpy = np.load(path)
    print("LoadNpyFile -", path, "shape:", retNpy.shape)
    return retNpy


class KoQuadDataset(datasets.Dataset):
    def __init__(self, tables):
        self.tables = tables

    def __getitem__(self, idx):
        data = self.tables[idx]
        items = {key: torch.tensor(val) for key, val in data.items()}

        return items

    def __len__(self):
        return len(self.tables)

if "__main__" == __name__:
    print("Start - Fine-tuning using by korquad 2.0")


    test_load = datasets.load_from_disk("./Dataset/Tokenization/ko-wiki")
    print(test_load)
    exit()

    # Load kor-quad Npy Files
    rootDir = "./Dataset/korquad"

    answer_span_table_npy = LoadNpyFile(rootDir+"/answer_span_table.npy") # shape: (12660, 2)
    cols_table_npy = LoadNpyFile(rootDir+"/cols_table.npy") # shape: (12660, 3, 512)
    rows_table_npy = LoadNpyFile(rootDir+"/rows_table.npy") # shape: (12660, 3, 512)
    segments_table_npy = LoadNpyFile(rootDir+"/segments_table.npy") # shape: (12660, 3, 512)
    sequence_table_npy = LoadNpyFile(rootDir+"/sequence_table.npy") # shape: (12660, 3, 512)

    # My Custom
    data_num = answer_span_table_npy.shape[0]
    pre_labels = torch.tensor(np.zeros([data_num, 512]))
    print(pre_labels.shape)
    print("Complete - Load Npy Files")

    # Datasets
    train_last_idx = data_num * 0.8

    train_data_dict = {
        "segment_ids": [],
        "column_ids": [],
        "row_ids": [],
        "prev_labels": [],
        "column_ranks": [],
        "inv_column_ranks": [],
        "numeric_relations": []
    }
    train_data_dict["column_ids"] = cols_table_npy[:train_last_idx]
    train_data_dict["row_ids"] = rows_table_npy[:train_last_idx]
    train_data_dict["segments_table"] = segments_table_npy[:train_last_idx]
    train_data_dict["sequence_table"] = sequence_table_npy[:train_last_idx]
    train_dataset = datasets.Dataset.from_dict(train_data_dict)
    train_dataset = KoQuadDataset(train_dataset)
    train_data_loader = torch.utils.data.DataLoader(train_data_dict, batch_size=2)

    test_data_dict = {
        "segment_ids": [],
        "column_ids": [],
        "row_ids": [],
        "prev_labels": [],
        "column_ranks": [],
        "inv_column_ranks": [],
        "numeric_relations": []
    }
    test_data_dict["cols_table"] = cols_table_npy[train_last_idx:]
    test_data_dict["rows_table"] = rows_table_npy[train_last_idx:]
    test_data_dict["segments_table"] = segments_table_npy[train_last_idx:]
    test_data_dict["sequence_table"] = sequence_table_npy[train_last_idx:]
    test_dataset = datasets.Dataset.from_dict(test_data_dict)
    test_dataset = KoQuadDataset(test_data_dict)
    test_data_loader = torch.utils.data.DataLoader(test_data_dict, batch_size=2)

    # Fine tuning
    modelPtDirPath = "./"
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=modelPtDirPath,
                                             return_dict=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Train Device:", device)
    model.to(device)

    for epoch in range(10):
        print("Epoch:", epoch+1)
        for idx, batch in enumerate(train_data_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)
            
        for idx, batch in enumerate(test_data_loader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)