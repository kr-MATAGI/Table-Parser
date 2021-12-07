from transformers import TapasForMaskedLM
from transformers import TapasConfig
from transformers import AdamW

import torch
import datasets
import numpy as np

### Method
def LoadNpyFile(path):
    retNpy = np.load(path)
    print("LoadNpyFile -", path, "shape:", retNpy.shape)
    return retNpy


class KorQuadDataset(datasets.Dataset):
    def __init__(self, srcData):
        self.srcData = srcData

    def __getitem__(self, idx):
        data = self.srcData[idx]
        items = {
            "labels": torch.tensor(data["answers"]),
            "input_ids": None,
            # "attention_mask": torch.tensor(np.zeros(512)),
            "token_type_ids": None
        }

        ## input_ids
        items["input_ids"] = torch.tensor(data["input_ids"][0], dtype=torch.int64)

        ## attention_mask

        ## token_type_ids
        # segment_ids
        segment_ids_tensor = torch.tensor(data["segment_ids"][0], dtype=torch.int64)

        # column_ids
        column_ids_tensor = torch.tensor(data["column_ids"][0], dtype=torch.int64)

        # row_ids
        row_ids_tensor = torch.tensor(data["row_ids"][0], dtype=torch.int64)

        # pre_labels - not used (fill with zero)
        pre_labels_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)

        # column_ranks
        column_ranks_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)

        # inv_column_ranks
        inv_column_ranks = torch.flip(column_ranks_tensor, dims=[0])

        # numeric_relations
        numeric_relation_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)
        items["token_type_ids"] = torch.column_stack([segment_ids_tensor, column_ids_tensor,
                                                     row_ids_tensor, pre_labels_tensor,
                                                      column_ranks_tensor, inv_column_ranks,
                                                      numeric_relation_tensor])

        return items

    def __len__(self):
        return len(self.srcData)

if "__main__" == __name__:
    print("Start - Fine-tuning using by korquad 2.0")

    # Load kor-quad Npy Files
    rootDir = "./Dataset/korquad"

    answer_span_table_npy = LoadNpyFile(rootDir+"/answer_span_table.npy") # shape: (12660, 2) # labels
    cols_table_npy = LoadNpyFile(rootDir+"/cols_table.npy") # shape: (12660, 3, 512)
    rows_table_npy = LoadNpyFile(rootDir+"/rows_table.npy") # shape: (12660, 3, 512)
    # column_rank_npy = LoadNpyFile(rootDir"/")
    segments_table_npy = LoadNpyFile(rootDir+"/segments_table.npy") # shape: (12660, 3, 512)
    sequence_table_npy = LoadNpyFile(rootDir+"/sequence_table.npy") # shape: (12660, 3, 512) -> input_ids

    # My Custom
    data_num = answer_span_table_npy.shape[0]
    pre_labels = torch.tensor(np.zeros([data_num, 512]))
    print("Complete - Load Npy Files")

    # Datasets
    train_last_idx = int(data_num * 0.8)

    train_data_dict = {
        "answers": [],
        "input_ids": [],
        "segment_ids": [],
        "column_ids": [],
        "row_ids": [],
        # "column_ranks": [],
    }
    train_data_dict["answers"] = answer_span_table_npy[:train_last_idx]
    train_data_dict["input_ids"] = sequence_table_npy[:train_last_idx]
    train_data_dict["segment_ids"] = segments_table_npy[:train_last_idx]
    train_data_dict["column_ids"] = cols_table_npy[:train_last_idx]
    train_data_dict["row_ids"] = rows_table_npy[:train_last_idx]
    # train_data_dict["column_ranks"]

    train_dataset = datasets.Dataset.from_dict(train_data_dict)
    train_dataset = KorQuadDataset(train_dataset)
    train_data_loader = torch.utils.data.DataLoader(train_dataset, batch_size=2)

    batch = next(iter(train_data_loader))

    test_data_dict = {
        "answers": [],
        "input_ids": [],
        "segment_ids": [],
        "column_ids": [],
        "row_ids": [],
        # "column_ranks": [],
    }
    test_data_dict["answers"] = answer_span_table_npy[train_last_idx:]
    test_data_dict["input_ids"] = sequence_table_npy[train_last_idx:]
    test_data_dict["segment_ids"] = segments_table_npy[train_last_idx:]
    test_data_dict["column_ids"] = cols_table_npy[train_last_idx:]
    test_data_dict["row_ids"] = rows_table_npy[train_last_idx:]
    # test_data_dict["column_ranks"]

    test_dataset = datasets.Dataset.from_dict(test_data_dict)
    test_dataset = KorQuadDataset(test_data_dict)
    test_data_loader = torch.utils.data.DataLoader(test_data_dict, batch_size=2)

    # Fine tuning
    modelPtDirPath = "./"
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=modelPtDirPath)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Train Device:", device)
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    for epoch in range(10):
        print("Epoch:", epoch+1)
        for idx, batch in enumerate(train_data_loader):
            input_ids = batch["input_ids"].to(device)
            # attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)
            labels = batch["answers"].to(device) # shape (batch_size, 2)

            # Test - Check Shape
            # print("input_ids.shape", input_ids.shape)
            # print("token_type_ids.shape", token_type_ids.shape)

            # zero the parameter gradients
            optimizer.zero_grad()

            outputs = model(input_ids=input_ids,
                            token_type_ids=token_type_ids)

            loss = outputs.loss
            print("Loss:", loss.item()) # loss == None

            loss.backward()
            optimizer.step()


        for idx, batch in enumerate(test_data_loader):
            input_ids = batch["input_ids"].to(device)
            # attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)