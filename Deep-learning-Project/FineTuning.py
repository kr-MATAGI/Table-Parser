from transformers import TapasForMaskedLM
from transformers import TapasTokenizer
from transformers import AdamW

import torch
import datasets

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

    # Load Datasets
    koquad_dataset_path = ""
    koquad_datasets = datasets.load_from_disk(koquad_dataset_path)

    koquad_dataloader = torch.utils.data.DataLoader(koquad_datasets, batch_size=2)

    # Model
    modelDirPath = "./"
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=modelDirPath)

    # Fine-tuning
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Train Device:", device)
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    for epoch in range(10):
        print("Epoch:", epoch)
        for idx, batch in enumerate():
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