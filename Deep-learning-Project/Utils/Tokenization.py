import torch
from transformers import AutoTokenizer
import pandas as pd
import numpy as np
import datasets
import random

'''
    klue/roberta-base
    0 - [CLS]
    1 - [PAD]
    2 - [SEP]
    3 - [UNK]
    4 - [MASK]
    5 - !
    
    google/tapas-mask-lm
    101 - [CLS]
    0 - [PAD]
    102 - [SEP]
    100 - [100]
    103 - [MASK]
'''
class MyTokenizer:
    def __init__(self):
        # keys = dict_keys(['input_ids', 'token_type_ids', 'attention_mask'])
        print("INIT - MyTokenizer")

    def LoadNewTokenizer(self, path):
        print("Start - LoadNewTokenizer {", path, "}")
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        print("Complete - LoadNewTokenizer {", path, "}")

    def Tokenize(self, table):
        # Tapas
        # table_dict = {}
        # for rdx, row in enumerate(table):
        #     for cdx, col in enumerate(row):
        #         if 0 == rdx:
        #             table_dict[col] = []
        #         else:
        #             table_dict[table[0][cdx]].append(col)
        # table_df = pd.DataFrame.from_dict(table_dict)
        # tokenizedTensor = self.tokenizer(table=table_df, padding="max_length", return_tensors="pt")

        # klue
        tableFlatten = ""
        for row in table:
            tableFlatten += " ".join(row)
        tokenizedTensor = self.tokenizer(text=tableFlatten, return_tensors="pt")

        tokenSentLen = len(tokenizedTensor["input_ids"][0])
        if 512 > tokenSentLen:
            diffLen = 512-tokenSentLen
            new_input_ids = torch.tensor(np.ones((1, diffLen), dtype=np.int64)) # [PAD]
            new_input_ids = torch.cat([tokenizedTensor["input_ids"], new_input_ids], dim=1)

            new_attention_mask = torch.tensor(np.zeros((1, diffLen), dtype=np.int64))
            new_attention_mask = torch.cat([tokenizedTensor["attention_mask"], new_attention_mask], dim=1)

            new_token_type_ids = torch.tensor(np.zeros((1, diffLen), dtype=np.int64))
            new_token_type_ids = torch.cat([tokenizedTensor["token_type_ids"], new_token_type_ids], dim=1)

            tokenizedTensor["input_ids"] = new_input_ids
            tokenizedTensor["attention_mask"] = new_attention_mask
            tokenizedTensor["token_type_ids"] = new_token_type_ids
        elif 512 < tokenSentLen:
            new_input_ids = torch.tensor(np.ones((1, 512), dtype=np.int64))  # [PAD]
            new_input_ids += tokenizedTensor["input_ids"][:, 512]

            new_attention_mask = torch.tensor(np.zeros((1, 512), dtype=np.int64))
            new_attention_mask += tokenizedTensor["attention_mask"][:, 512]

            new_token_type_ids = torch.tensor(np.zeros((1, 512), dtype=np.int64))
            new_token_type_ids += tokenizedTensor["token_type_ids"][:, 512]

            tokenizedTensor["input_ids"] = new_input_ids
            tokenizedTensor["attention_mask"] = new_attention_mask
            tokenizedTensor["token_type_ids"] = new_token_type_ids

        new_token_type_ids = torch.tensor(np.zeros([tokenizedTensor["token_type_ids"].shape[0],
                                                    tokenizedTensor["token_type_ids"].shape[1],
                                                    7],
                                                   dtype=np.int64))
        tokenizedTensor["token_type_ids"] = new_token_type_ids

        return tokenizedTensor

    def MakeDatasets(self, srcTableList, savedPath):
        # Init
        procCount = 0
        print("MakeDatasets savedPath:", savedPath)

        # Shuffle
        srcTableListLen = len(srcTableList)
        print("TotalTable Size:", srcTableListLen, "\n")

        shuffledTableList = srcTableList
        random.shuffle(shuffledTableList)

        # Slice train and test datasets
        splitIdx = int(srcTableListLen * 0.8)

        trainTableList = srcTableList[:splitIdx]
        testTableList = srcTableList[splitIdx:]

        # Tokenization - Train dataset
        trainDataDict = {
            "input_ids": [],
            "token_type_ids": [],
            "attention_mask": []
        }
        for table in trainTableList:
            procCount += 1
            if 0 == (procCount % 1000):
                print(procCount, "Processing...")

            tokenizedData = self.Tokenize(table)
            trainDataDict["input_ids"].append(tokenizedData["input_ids"])
            trainDataDict["token_type_ids"].append(tokenizedData["token_type_ids"])
            trainDataDict["attention_mask"].append(tokenizedData["attention_mask"])

        # Tokenization - Test dataset
        testDataDict = {
            "input_ids": [],
            "token_type_ids": [],
            "attention_mask": []
        }
        for table in testTableList:
            procCount += 1
            if 0 == (procCount % 1000):
                print(procCount, "Processing...")

            tokenizedData = self.Tokenize(table)
            testDataDict["input_ids"].append(tokenizedData["input_ids"])
            testDataDict["token_type_ids"].append(tokenizedData["token_type_ids"])
            testDataDict["attention_mask"].append(tokenizedData["attention_mask"])

            # test - decode print
            #print(self.tokenizer.decode(tokenizedData["input_ids"]))

        tokenizedDatasets = datasets.DatasetDict({
            "train": datasets.Dataset.from_dict(trainDataDict),
            "test": datasets.Dataset.from_dict(testDataDict)
        })

        tokenizedDatasets.save_to_disk(savedPath)
        print("Complete - MyTokenizer.MakeDataset()")

if "__main__" == __name__:
    print("Start Test - Tokenization")

    # ones_tensor = torch.tensor(np.ones(shape=(1, 874), dtype=np.int64))
    # print(ones_tensor.shape)
    #
    # convert_tensor = torch.tensor(np.zeros(shape=(1, 512), dtype=np.int64))
    # convert_tensor += ones_tensor[:, :512]
    #
    # print(convert_tensor.shape)

    tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")