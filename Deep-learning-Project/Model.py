from transformers import AutoTokenizer, TapasForMaskedLM, TapasConfig
from transformers import Trainer
import pandas as pd
import torch


if "__main__" == __name__:
    print("Model Pretrain")

    # Init
    modelPtDirPath = "./"
    tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=modelPtDirPath)

    # Train
    trainer = Trainer(
        model=model,
        train_dataset="",
        eval_dataset="",

    )