import torch
from transformers import TapasTokenizer
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

    def AddNewToken2Vocab(self, vocabPath, destPath):
        tapasToeknzier = TapasTokenizer.from_pretrained("google/tapas-base-masklm")

        print("vocabPath:", vocabPath)
        print("destPath:", destPath)
        with open(vocabPath, mode="r", encoding="utf-8") as kf:
            addTokenCnt = 0
            for klueToken in kf:
                klueToken = klueToken.strip()
                addTokenCnt += 1
                if 0 == (addTokenCnt % 1000):
                    print(addTokenCnt, "Adding...", klueToken)
                tapasToeknzier.add_tokens(klueToken)
        tapasToeknzier.save_pretrained(destPath)
        # tapasToeknzier.save_vocabulary(destPath+"/new_vocab.txt")

    def LoadNewTokenizer(self, path="./NewTokenizer"):
        print("Start - LoadNewTokenizer {", path, "}")
        self.tokenizer = TapasTokenizer.from_pretrained(path)
        print("Complete - LoadNewTokenizer {", path, "}")

    def Tokenize(self, table):
        # Tapas
        table_dict = {}
        for rdx, row in enumerate(table):
            for cdx, col in enumerate(row):
                if 0 == rdx:
                    table_dict[col] = []
                else:
                    table_dict[table[0][cdx]].append(col)
        table_df = pd.DataFrame.from_dict(table_dict)
        tokenizedTensor = self.tokenizer(table=table_df, padding="max_length", return_tensors="pt")

        # klue
        # tableFlatten = ""
        # for row in table:
        #     tableFlatten += " ".join(row)
        # tokenizedTensor = self.tokenizer(text=tableFlatten)

        return tokenizedTensor

    def MakeDatasets(self, srcTableList):
        # Init
        trainDataDict = {'input_ids': [],
                         'token_type_ids': [],
                         'attention_mask': []}
        testDataDict = {'input_ids': [],
                         'token_type_ids': [],
                         'attention_mask': []}
        procCount = 0

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

            print(self.tokenizer.decode(tokenizedData["input_ids"]))

        tokenizedDatasets = datasets.DatasetDict({
            "train": datasets.Dataset.from_dict(trainDataDict),
            "test": datasets.Dataset.from_dict(testDataDict)
        })
        tokenizedDatasets.save_to_disk("../Dataset/Tokenization")
        print("Complete - MyTokenizer.MakeDataset()")

if "__main__" == __name__:
    print("Start Test - Tokenization")

    testTable = [[ "트랙", "제목", "링크" , "러닝 타임", "작곡가" ],
                [ "1", "Way Back then 옛날 옛적에", "", "2:32", "정재일" ],
                [ "2", "Round I 1라운드", "", "1:20", "정재일" ],
                [ "3", "The Rope is Tied 밧줄은 묶여 있다", "", "3:19", "정재일" ],
                [ "4", "Pink Soldiers 분홍 병정", "", "0:39", "김성수" ],
                [ "5", "Hostage Crisis 인질극", "", "2:23", "김성수" ],
                [ "6", "I Remember My Name · TITLE 내 이름이 기억났어", "", "3:14", "정재일" ]]

    testTableList = []
    testTableList.append(testTable)

    myTokenizer = MyTokenizer()

    myTokenizer.AddNewToken2Vocab(vocabPath="./TokenizeConfig/klue-vocab.txt", destPath="./NewTokenizer")
    myTokenizer.LoadNewTokenizer(path="./NewTokenizer")
    myTokenizer.MakeDatasets(testTableList)
