from transformers import AutoTokenizer, TapasForMaskedLM
import pandas as pd
import torch




if "__main__" == __name__:
    print("Model Pretrain")

    # Init
    pretrainedPath = "./ModelBinFiles/klue-tapas-base.bin",
    tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")
    model = TapasForMaskedLM.from_pretrained(pretrained_model_name_or_path=pretrainedPath)
