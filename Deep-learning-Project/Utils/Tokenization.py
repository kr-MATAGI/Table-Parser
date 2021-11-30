from transformers import AutoTokenizer
import pandas as pd
import numpy as np


class MyTokenizer:
    def __init__(self):
        # Init
        self.input_ids_list = []
        self.token_type_ids_list = []
        self.attention_mask_list = []

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

        if len(input_ids) == len(token_type_ids) and \
            len(token_type_ids) == len(attention_mask):
            self.input_ids_list.append(input_ids)
            self.token_type_ids_list.append(token_type_ids)
            self.attention_mask_list.append(attention_mask)

    def SaveTrainToken(self):
        np.save("./test.npy", self.input_ids_list)

if "__main__" == __name__:
    print("Start Tokenization")

    testTable = [[ "트랙", "제목", "링크" , "러닝 타임", "작곡가" ],
                [ "1", "Way Back then 옛날 옛적에", "", "2:32", "정재일" ],
                [ "2", "Round I 1라운드", "", "1:20", "정재일" ],
                [ "3", "The Rope is Tied 밧줄은 묶여 있다", "", "3:19", "정재일" ],
                [ "4", "Pink Soldiers 분홍 병정", "", "0:39", "김성수" ],
                [ "5", "Hostage Crisis 인질극", "", "2:23", "김성수" ],
                [ "6", "I Remember My Name · TITLE 내 이름이 기억났어", "", "3:14", "정재일" ]]

    '''
        0 - [CLS]
        1 - [PAD]
        2 - [SEP]
        3 - [UNK]
        4 - [MASK]
        5 - !
    '''

    myToken = MyTokenizer()
    myToken.Tokenize(testTable)
    myToken.Tokenize(testTable)
    #myToken.SaveTrainToken()
