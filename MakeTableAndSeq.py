# masking generation strategy
#
# 1: masking with table documents and infoboxes
#
# 2: masking with only plain text documents
# plain text length must be longer than 256
# max_length = 384

### Import Compute Tool
from random import random as rand
import numpy as np

### Import Model
from transformers import AutoTokenizer

### Import Namu Wiki Parser
from NamuWiki.NamuParser import NamuWikiParser

### Import SyangHeun Moduel
import Table_Holder # maybe is need...

### GLOBAL
max_length = 512
total_size = 300000
count = 0

max_masking = 20

SRC_JSON_PATH = './dataset/docData200302.json'

sequence_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
segments_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
masks_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
cols_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
rows_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)

label_ids = np.zeros(shape=[total_size, 2, max_masking], dtype=np.int32)
label_position = np.zeros(shape=[total_size, 2, max_masking], dtype=np.int32)
label_weight = np.zeros(shape=[total_size, 2, max_masking], dtype=np.float)

## Tokenizer
tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")

## NamuParser
namuParser = NamuWikiParser(SRC_JSON_PATH)
DOC_TITLE = 'title'
DOC_TEXT = 'text'

## TEST MODE
TEST_MODE = True

if __name__ == '__main__':

    ### Parse Table
    docCnt = 0
    for document in namuParser.ParsingJSON():
        docCnt += 1

        if TEST_MODE and (0 == docCnt % 1000):
            print('Processing...', document[DOC_TITLE], docCnt)

        docTableList = namuParser.ParseTableFromText(document[DOC_TEXT])

        if 0 < len(docTableList):
            newTableList = []
            namuParser.ModifyHTMLTags(docTableList)

            for table in docTableList:
                preprocessedTable = namuParser.PreprocessingTable(table)

                if 2 <= len(preprocessedTable):
                    newTableList.append(preprocessedTable)
            normalTableList, infoBoxList = namuParser.ClassifyNormalTableOrInfoBox(newTableList)

            # Extract Text, Remove <\w+>, [[.+]]
            textTableList = namuParser.ExtractTextDataInColumn(normalTableList)

            for textTable in textTableList:
                table_data = textTable

                new_data = []
                num_row = len(table_data)
                num_col = len(table_data[0])

                for y in range(num_col):
                    new_line = []

                    for x in range(num_row):
                        new_line.append(table_data[x][y])
                    new_data.append(new_line)

                # table_holder.table_data = new_data # ????????

                ################### MY Sequence Text 개요 기준 테이블 관련 텍스트
                seq_text = None
                sentences = seq_text.split('. ')
                ###################################

                seq_text = ''
                for sentence in sentences:
                    if len(tokenizer.tokenize(seq_text)) > 64:
                        break
                    seq_text += sentence + '. '

                tokens = tokenizer.tokenize(seq_text)
                tokens.insert(0, '[CLS]')