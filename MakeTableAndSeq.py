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

### Import Namu Wiki Parser
from NamuWiki.NamuParser import NamuWikiParser
from NamuWiki.TextExtractor import TextExtractor

### GLOBAL
max_length = 512
total_size = 300000
count = 0

max_masking = 20

# File Path
SRC_JSON_PATH = './dataset/docData200302.json'

# Numpy
sequence_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
segments_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
masks_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
cols_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)
rows_has_ans = np.zeros(shape=[total_size, 2, max_length], dtype=np.int32)

label_ids = np.zeros(shape=[total_size, 2, max_masking], dtype=np.int32)
label_position = np.zeros(shape=[total_size, 2, max_masking], dtype=np.int32)
label_weight = np.zeros(shape=[total_size, 2, max_masking], dtype=np.float64)

## NamuParser
DOC_TITLE = 'title'
DOC_TEXT = 'text'
namuParser = NamuWikiParser(SRC_JSON_PATH)
namuTextExtractor = TextExtractor()

## TEST MODE
TEST_TARGET = '백 평짜리 숲(킹덤 하츠)'
TEST_MODE = True

if __name__ == '__main__':

    ### Parse Table
    docCnt = 0
    for document in namuParser.ParsingJSON():
        docCnt += 1

        if 0 == (docCnt % 1000):
            print('Processing...', document[DOC_TITLE], docCnt)

        # TEST MODE
        if TEST_MODE and TEST_TARGET != document[DOC_TITLE]: continue

        # Make paragraph list - [paragraph index, table list, text list]
        splitParagraphList = namuParser.ParseTableAndDetailsFromDocument(document[DOC_TITLE], document[DOC_TEXT])

        for paragraph in splitParagraphList:
            ## Table
            if 0 < len(paragraph[1]): # exist table
                newTableList = []
                modifiedTableList = namuParser.ModifyHTMLTags(paragraph[1])

                for table in modifiedTableList:
                    preprocessedTable = namuParser.PreprocessingTable(table)

                    if 2 <= len(preprocessedTable):
                        newTableList.append(preprocessedTable)

                normalTableList, infoBoxList = namuParser.ClassifyNormalTableOrInfoBox(newTableList)
                onlyTextTableList = namuTextExtractor.ExtractTextAtTable(normalTableList) # only use normal tables
                paragraph[1] = onlyTextTableList

            ## Sequence
            if 0 < len(paragraph[2]): # exist paragraph text
                splitParagraphList = namuTextExtractor.RemoveNamuwikiSyntax(paragraph[2])
                paragraph[2] = splitParagraphList

        break

        '''
        if 0 < len(tableAndDetailsList):
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

                ################### MY Sequence Text 개요 기준 테이블 관련 텍스트
                seq_text = None
                sentences = seq_text.split('. ')
                ###################################
        '''