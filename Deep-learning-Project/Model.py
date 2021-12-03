import datasets
import torch
from transformers import TapasForMaskedLM
from transformers import Trainer
from transformers import AdamW


class MyTableDataset(datasets.Dataset):
    def __init__(self, tables):
        self.tables = tables

    def __getitem__(self, idx):
        data = self.tables[idx]
        items = {key: torch.tensor(val) for key, val in data.items()}

        return items

    def __len__(self):
        return len(self.tables)

if "__main__" == __name__:
    print("Model Pretrain")

    # Load Tokenized Datasets
    totalDatasets = datasets.load_from_disk("./Dataset/Tokenization")

    trainDataset = MyTableDataset(totalDatasets["train"])
    testDataset = MyTableDataset(totalDatasets["test"])

    train_dataloader = torch.utils.data.DataLoader(trainDataset, batch_size=1)
    test_dataloader = torch.utils.data.DataLoader(testDataset, batch_size=1)

    # Model
    modelPtDirPath = "./"
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=modelPtDirPath)
    #model = TapasForMaskedLM.from_pretrained("google/tapas-base-masklm")

    # Train
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    for epoch in range(10):
        print("Epoch:", epoch)
        for idx, batch in enumerate(test_dataloader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            token_type_ids = batch["token_type_ids"].to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = model(input_ids=input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids)

            loss = outputs.loss

            # TODO: Get Loss, backword, step