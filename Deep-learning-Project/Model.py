from transformers import AutoTokenizer, TapasForMaskedLM, TapasConfig
from transformers import Trainer
import pandas as pd

from torch.utils.data import Dataset, DataLoader
import torch


## Dataset
class TableDataset(Dataset):
    def __init__(self):
        return

    def __getitem__(self, item):
        return

    def __len__(self):
        return


if "__main__" == __name__:
    print("Model Pretrain")

    # Init
    modelPtDirPath = "./"
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=modelPtDirPath)