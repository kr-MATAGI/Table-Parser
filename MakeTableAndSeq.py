# masking generation strategy
#
# 1: masking with table documents and infoboxes
#
# 2: masking with only plain text documents
# plain text length must be longer than 256
# max_length = 384

### Import Compute Tool
import copy
from random import random as rand
import numpy as np
from dataclasses import dataclass

### Import Namu Wiki Parser
from NamuWiki.NamuParser import NamuWikiParser
from NamuWiki.TextExtractor import TextExtractor
from NamuWiki.ParagraphTextScorer import TableTextScorer

### Hugging Face - transformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

### GLOBAL
max_length = 512
total_size = 300000
count = 0

max_masking = 20

# File Path
SRC_JSON_PATH = './dataset/docData200302.json'

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")

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
namuTableTextScorer = TableTextScorer()

@dataclass
class TableRelation:
    table = None
    sentence = None

@dataclass
class ParagraphRelation:
    paragraphIdx: int = None
    tableRelation = list()

## TEST MODE
TEST_TARGET = 'SPARK!'
TEST_MODE = True
TEST_TEXT_PRINT = False

if __name__ == '__main__':
    ### Parse Table
    docCnt = 0
    for document in namuParser.ParsingJSON():
        docCnt += 1

        if 0 == (docCnt % 1000):
            print('Processing...', document[DOC_TITLE], docCnt)

        #### TEST MODE ####
        if TEST_MODE and TEST_TARGET != document[DOC_TITLE]: continue

        # Make paragraph list - [paragraph index, table list, text list]
        splitParagraphList = namuParser.ParseTableAndDetailsFromDocument(document[DOC_TITLE],
                                                                         document[DOC_TEXT])

        paragraphRelationList = []  # [ TableRelation data structure ... ]
        for paragraph in splitParagraphList:
            paragraphRelation = ParagraphRelation()
            paragraphRelation.paragraphIdx = paragraph[0]
            paragraphRelation.tableRelation = list()

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
                textParagraphList = namuTextExtractor.RemoveNamuwikiSyntax(paragraph[2])
                paragraph[2] = textParagraphList

            # Add score between table and sequence
            if (0 < len(paragraph[1])) and (0 < len(paragraph[2])):
                # Make concat tables
                concatTableList = []
                for table in paragraph[1]:
                    mergeTable = []
                    for row in table:
                        mergeTable += row

                    concatStr = ' '.join(mergeTable)
                    concatTableList.append(concatStr)

                # Compute sentence core per concatTable
                tableSentenceDict = dict() # key: int - table index, value: list - sentenceIndex

                for ctIdx, concatTable in enumerate(concatTableList):
                    scoreList = []
                    namuTableTextScorer.SetConcatTable(concatTable)

                    for sentence in paragraph[2]:
                        score = namuTableTextScorer.GetSentenceScore(sentence)
                        scoreList.append(score)

                    # Search highest score sentence
                    highScore = max(scoreList)
                    highSentenceIdx = scoreList.index(highScore)
                    tableSentenceDict[ctIdx] = highSentenceIdx

                # Make tableRelation and Add tableRelation to paragraphRelation
                for key, val in tableSentenceDict.items():
                    tableRelation = TableRelation()

                    table = paragraph[1][key]
                    tableRelation.table = table

                    tableRelation.sentence = paragraph[2][val]
                    paragraphRelation.tableRelation.append(tableRelation)

            else:
                # exist only table
                if 0 < len(paragraph[1]): # table
                    for table in paragraph[1]:
                        tableRelation = TableRelation()
                        tableRelation.table = table
                        tableRelation.sentenceList = None

                        paragraphRelation.tableRelation.append(tableRelation)

            paragraphRelationList.append(paragraphRelation)


        #### TEST ####
        if TEST_MODE:
            for test_paragraph in paragraphRelationList:
                print("para idx: ", test_paragraph.paragraphIdx)

                for test_tableRelation in test_paragraph.tableRelation:
                    print(test_tableRelation.table)
                    print(test_tableRelation.sentence)

                print('\n===============')

            if TEST_TEXT_PRINT:
                print(document[DOC_TEXT])
        ###############

        ### Tokenizer

        break

