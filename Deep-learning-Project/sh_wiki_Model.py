import datasets
import torch
import numpy as np
import random

from transformers import TapasForMaskedLM
from transformers import AdamW

from torch.utils.data import (DataLoader, RandomSampler, TensorDataset)

import datasets
class SH_Dataset(datasets.Dataset):
    def __init__(self, srcData):
        self.srcData = srcData

    def __getitem__(self, idx):
        data = self.srcData[idx]
        items = {
            "input_ids": None,
            "attention_mask": None,
            "token_type_ids": None,
            "input_rows": None,
            "input_cols": None,
            "labels": None
        }

        addOnesTensor = torch.tensor(np.ones(512-384), dtype=torch.int64)
        addZeroTensor = torch.tensor(np.zeros(512-384), dtype=torch.int64)
        ## labels
        sequence_tensor = torch.tensor(data["input_ids"], dtype=torch.int64)
        sequence_tensor = torch.concat([sequence_tensor, addOnesTensor])
        items["labels"] = sequence_tensor

        ## input_ids

        randIdx = 1
        try:
            padStart_idx = sequence_tensor.index(1)
            randIdx = random.randrange(1, padStart_idx)
        except:
            randIdx = random.randrange(1, 512)
        items["input_ids"] = sequence_tensor
        items["input_ids"][randIdx] = 4  # [MASK]

        ## attention_mask
        items["attention_mask"] = torch.tensor(data["attention_mask"], dtype=torch.int64)
        items["attention_mask"] = torch.concat([items["attention_mask"], addZeroTensor])

        ## token_type_ids
        # segment_ids
        segment_ids_tensor = torch.tensor(data["input_segments"], dtype=torch.int64)
        segment_ids_tensor = torch.concat([segment_ids_tensor, addZeroTensor])

        # column_ids
        column_ids_tensor = torch.tensor(data["input_cols"], dtype=torch.int64)
        column_ids_tensor = torch.concat([column_ids_tensor, addZeroTensor])
        items["input_cols"] = column_ids_tensor

        # row_ids
        row_ids_tensor = torch.tensor(data["input_rows"], dtype=torch.int64)
        row_ids_tensor = torch.concat([row_ids_tensor, addZeroTensor])
        items["input_rows"] = row_ids_tensor

        # pre_labels - not used (fill with zero)
        pre_labels_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)

        # column_ranks
        column_ranks_tensor = torch.tensor(np.zeros(512), dtype=torch.int64)

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
    print("Model Pretrain")

    # Load Tokenized Datasets
    npy_root_dir = "./Dataset/sh_korwiki/"
    input_ids = np.load(npy_root_dir + 'input_ids_generated.npy')
    input_segments = np.load(npy_root_dir + 'segments_ids_generated.npy')
    attention_mask = np.load(npy_root_dir + 'mask_ids_generated.npy')
    input_rows = np.load(npy_root_dir + 'input_row_generated.npy')
    input_cols = np.load(npy_root_dir + 'input_col_generated.npy')
    labels = np.load(npy_root_dir + 'labels_generated.npy')

    print("input_ids.shape:", input_ids.shape)
    print("input_segments.shape:", input_segments.shape)
    print("attention_mask:", attention_mask.shape)
    print("input_rows.shape:", input_rows.shape)
    print("input_cols.shape:", input_cols.shape)
    print("labels.shape:", labels.shape)

    # Make Datasets
    train_data_dict = {
        "input_ids": None,
        "input_segments": None,
        "attention_mask": None,
        "input_rows": None,
        "input_cols": None,
        "labels": None
    }

    train_data_dict["input_ids"] = input_ids
    train_data_dict["input_segments"] = input_segments
    train_data_dict["attention_mask"] = attention_mask
    train_data_dict["input_rows"] = input_rows
    train_data_dict["input_cols"] = input_cols
    train_data_dict["labels"] =  labels

    train_dataset = datasets.Dataset.from_dict(train_data_dict)
    train_dataset = SH_Dataset(train_dataset)

    train_sampler = RandomSampler(train_dataset)
    train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=16)

    # Model
    modelPtDirPath = "./"
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=modelPtDirPath,
                                             return_dict=True)
    #model = TapasForMaskedLM.from_pretrained("google/tapas-base-masklm")

    # Train
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Train Device:", device)
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    for epoch in range(2):
        print("Epoch:", epoch+1)
        for idx, batch in enumerate(train_dataloader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)
            labels = batch["labels"].to(device)

            # Test - Check Shape
            # print("input_ids.shape", input_ids.shape)
            # print("attention_mask.shape", attention_mask.shape)
            # print("token_type_ids.shape", token_type_ids.shape)
            # print("labels.shape:", labels.shape)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = model(input_ids=input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            labels=labels)

            loss = outputs.loss
            print("Loss:", loss.item())

            loss.backward()
            optimizer.step()

    # Save Model
    savePath = "./SavedModel/sh_korwiki"
    model.save_pretrained(savePath)