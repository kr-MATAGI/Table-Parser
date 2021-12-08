import datasets
import torch
import numpy as np
import random

from transformers import TapasForMaskedLM
from transformers import AdamW


class MyTableDataset(datasets.Dataset):
    def __init__(self, tables):
        self.tables = tables

    def __getitem__(self, idx):
        data = self.tables[idx]

        items = {
            "input_ids": None,
            "attention_mask": None,
            "token_type_ids": None,
            "labels": None
        }

        ## input_ids
        randIdx = 1
        try:
            padStart_idx = data["input_ids"][0].index(1)
            randIdx = random.randrange(1, padStart_idx)
        except:
            randIdx = random.randrange(1, 512)
        items["input_ids"] = torch.tensor(np.array(data["input_ids"][0], dtype=np.int64))
        items["input_ids"][randIdx] = 4 # [MASK]

        ## attention_mask
        items["attention_mask"] = torch.tensor(np.array(data["attention_mask"][0], dtype=np.int64))

        ## token_type_ids
        items["token_type_ids"] = torch.tensor(np.array(data["token_type_ids"][0], dtype=np.int64))

        ## labels
        items["labels"] = torch.tensor(np.array(data["input_ids"][0], dtype=np.int64))

        return items

    def __len__(self):
        return len(self.tables)

if "__main__" == __name__:
    print("Model Pretrain")

    # Load Tokenized Datasets
    totalDatasets = datasets.load_from_disk("./Dataset/Tokenization/ko-wiki")

    trainDataset = totalDatasets["train"]
    testDataset = totalDatasets["test"]

    summarize_dataset = datasets.concatenate_datasets([trainDataset, testDataset])
    summarize_dataset = MyTableDataset(summarize_dataset)
    pt_dataloader = torch.utils.data.DataLoader(summarize_dataset, batch_size=1024)

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
    for epoch in range(10):
        print("Epoch:", epoch+1)
        for idx, batch in enumerate(pt_dataloader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)
            labels = batch["labels"].to(device)

            # Test - Check Shape
            # print("input_ids.shape", input_ids.shape)
            # print("attention_mask.shape", attention_mask.shape)
            # print("token_type_ids.shape", token_type_ids.shape)

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
    savePath = "./SavedModel/kor-wiki"
    model.save_pretrained(savePath)