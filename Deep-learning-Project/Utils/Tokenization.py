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
        self.tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")

        # input_ids.type = torch.Tensor, len = 512
        # keys = dict_keys(['input_ids', 'attention_mask', 'token_type_ids'])
        #self.tokenizer = AutoTokenizer.from_pretrained("google/tapas-base-masklm")
        print("INIT - MyTokenizer")

    def Tokenize(self, table):
        # Table flatten
        tableFlatten = ""
        for row in table:
            tableFlatten += " ".join(row)

        tokenizedDict = self.tokenizer(text=tableFlatten)
        input_ids = tokenizedDict["input_ids"]
        token_type_ids = tokenizedDict["token_type_ids"]
        attention_mask = tokenizedDict["attention_mask"]

        # Check Length
        tokenizedLen = len(input_ids)
        if 512 > tokenizedLen:
            zeroList = [ 0 for _ in range(512 - tokenizedLen) ]
            input_ids.extend(zeroList)
            token_type_ids.extend(zeroList)
            attention_mask.extend(zeroList)

            tokenizedDict["input_ids"] = input_ids
            tokenizedDict["token_type_ids"] = token_type_ids
            tokenizedDict["attention_mask"] = attention_mask

        return tokenizedDict

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
        for table in trainTableList:
            procCount += 1
            if 0 == (procCount % 1000):
                print(procCount, "Processing...")

            tokenizedData = self.Tokenize(table)
            trainDataDict['input_ids'].append(tokenizedData['input_ids'])
            trainDataDict['token_type_ids'].append(tokenizedData['token_type_ids'])
            trainDataDict['attention_mask'].append(tokenizedData['attention_mask'])

        # Tokenization - Test dataset
        for table in testTableList:
            procCount += 1
            if 0 == (procCount % 1000):
                print(procCount, "Processing...")

            tokenizedData = self.Tokenize(table)
            testDataDict['input_ids'].append(tokenizedData['input_ids'])
            testDataDict['token_type_ids'].append(tokenizedData['token_type_ids'])
            testDataDict['attention_mask'].append(tokenizedData['attention_mask'])
            #pretrainDatasetDict["test"].append(tokenizedData)

        trainDatasets = datasets.Dataset.from_dict(trainDataDict)
        testDatasets = datasets.Dataset.from_dict(testDataDict)

        tokenizedDatasets = datasets.DatasetDict({
            "train": trainDatasets,
            "test": testDatasets
        })
        tokenizedDatasets.save_to_disk("../Dataset/Tokenization")

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

    myTokenizere = MyTokenizer()
    #myTokenizere.MakeDatasets(testTableList)
    a = datasets.load_from_disk("../Dataset/Tokenization")
