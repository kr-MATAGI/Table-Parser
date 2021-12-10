from transformers import TapasForMaskedLM
from transformers import AdamW
from Utils.Tokenization import *

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
            "labels": None,
            "input_ids": None,
            "attention_mask": None,
            "token_type_ids": None
        }

        ## labels
        startIdx = data["labels"][0]
        endIdx = data["labels"][1]
        label = data["input_ids"][0][startIdx:endIdx]

        empty_tensor = torch.tensor(np.zeros(512 - len(label)), dtype=torch.int64)
        label_tensor = torch.tensor(label, dtype=torch.int64)
        items["labels"] = torch.concat([label_tensor, empty_tensor], dim=-1)

        ## input_ids
        items["input_ids"] = torch.tensor(data["input_ids"][0], dtype=torch.int64)

        ## attention_mask
        items["attention_mask"] = torch.tensor(data["attention_mask"][0], dtype=torch.int64)

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
        column_ranks_tensor = torch.tensor(data["column_ranks"][0], dtype=torch.int64)

        # inv_column_ranks
        inv_column_ranks = torch.flip(column_ranks_tensor, dims=[0])

        # numeric_relations
        numeric_relation_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)
        items["token_type_ids"] = torch.column_stack([segment_ids_tensor,
                                                      column_ids_tensor,
                                                      row_ids_tensor,
                                                      pre_labels_tensor,
                                                      column_ranks_tensor,
                                                      inv_column_ranks,
                                                      numeric_relation_tensor])

        return items

    def __len__(self):
        return len(self.srcData)

if "__main__" == __name__:
    myTokenizer = MyTokenizer()
    myTokenizer.LoadNewTokenizer("klue/roberta-base")
    print("Start - Fine-tuning using by korquad 2.0")

    # Load kor-quad Npy Files
    rootDir = "./Dataset/korquad"

    answer_span_table_npy = LoadNpyFile(rootDir+"/answer_span_table.npy") # shape: (12660, 2) # labels
    cols_table_npy = LoadNpyFile(rootDir+"/cols_table.npy") # shape: (12660, 3, 512)
    rows_table_npy = LoadNpyFile(rootDir+"/rows_table.npy") # shape: (12660, 3, 512)
    column_rank_npy = LoadNpyFile(rootDir+"/ranks_table.npy") # shape: (12660, 3, 512)
    attention_mask_npy = LoadNpyFile(rootDir+"/mask_table.npy") # shape: (12660, 3, 512)
    segments_table_npy = LoadNpyFile(rootDir+"/segments_table.npy") # shape: (12660, 3, 512)
    sequence_table_npy = LoadNpyFile(rootDir+"/sequence_table.npy") # shape: (12660, 3, 512) -> input_ids

    # My Custom
    data_num = answer_span_table_npy.shape[0]
    print("Complete - Load Npy Files")

    # Datasets
    data_split_idx = int(data_num * 0.8)
    print("Total Data Size:", data_num, "Data split Index:", data_split_idx)

    train_data_dict = {
        "labels": [],
        "input_ids": [],
        "attention_mask": [],
        "segment_ids": [],
        "column_ids": [],
        "row_ids": [],
        "column_ranks": []
    }
    train_data_dict["labels"] = answer_span_table_npy[:data_split_idx]
    train_data_dict["input_ids"] = sequence_table_npy[:data_split_idx]
    train_data_dict["attention_mask"] = attention_mask_npy[:data_split_idx]
    train_data_dict["segment_ids"] = segments_table_npy[:data_split_idx]
    train_data_dict["column_ids"] = cols_table_npy[:data_split_idx]
    train_data_dict["row_ids"] = rows_table_npy[:data_split_idx]
    train_data_dict["column_ranks"] = column_rank_npy[:data_split_idx]

    train_dataset = datasets.Dataset.from_dict(train_data_dict)
    train_dataset = KorQuadDataset(train_dataset)
    print("Train Datasets Size:", len(train_dataset))
    train_data_loader = torch.utils.data.DataLoader(train_dataset, batch_size=1)

    test_data_dict = {
        "labels": [],
        "input_ids": [],
        "attention_mask": [],
        "segment_ids": [],
        "column_ids": [],
        "row_ids": [],
        "column_ranks": []
    }
    test_data_dict["labels"] = answer_span_table_npy[data_split_idx:]
    test_data_dict["input_ids"] = sequence_table_npy[data_split_idx:]
    test_data_dict["attention_mask"] = attention_mask_npy[data_split_idx:]
    test_data_dict["segment_ids"] = segments_table_npy[data_split_idx:]
    test_data_dict["column_ids"] = cols_table_npy[data_split_idx:]
    test_data_dict["row_ids"] = rows_table_npy[data_split_idx:]
    test_data_dict["column_ranks"] = column_rank_npy[data_split_idx:]

    test_dataset = datasets.Dataset.from_dict(test_data_dict)
    test_dataset = KorQuadDataset(test_dataset)
    print("Test Datasets Size:", len(test_dataset))
    test_data_loader = torch.utils.data.DataLoader(test_data_dict, batch_size=1)

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
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)
            labels = batch["labels"].to(device) # shape (batch_size, 2)

            # zero the parameter gradients
            optimizer.zero_grad()

            outputs = model(input_ids=input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            labels=labels)

            loss = outputs.loss
            logits = outputs.logits
            print("Loss:", loss.item())

            loss.backward()
            optimizer.step()

    # Save Model
    output_model_file = "./output_model_korquad.bin"
    n_gpu = torch.cuda.device_count()
    print('n gpu:', n_gpu)
    if n_gpu > 1:
        torch.save(model.module.state_dict(), output_model_file)
    else:
        torch.save(model.state_dict(), output_model_file)

# Sample
# testTable = [["트랙", "제목", "링크", "러닝 타임", "작곡가"],
#              ["1", "Way Back then 옛날 옛적에", "", "2:32", "정재일"],
#              ["2", "Round I 1라운드", "", "1:20", "정재일"],
#              ["3", "The Rope is Tied 밧줄은 묶여 있다", "", "3:19", "정재일"],
#              ["4", "Pink Soldiers 분홍 병정", "", "0:39", "김성수"],
#              ["5", "Hostage Crisis 인질극", "", "2:23", "김성수"],
#              ["6", "I Remember My Name · TITLE 내 이름이 기억났어", "", "3:14", "정재일"]]