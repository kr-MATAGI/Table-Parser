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
from NamuWiki.NamuTextExtractor import TextExtractor
from NamuWiki.NamuSentenceScorer import TableTextScorer
from NamuWiki.NamuTokenizer import NamuTokenizer

### Import Table Header Extractor
from HeadExtractor import TableHeaderExtractor

### Hugging Face - transformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

### GLOBAL
MAX_LENGTH = 512
MAX_MASKING = 20

TOTAL_SIZE = 300000
COUNT = 0

# File Path
SRC_JSON_PATH = './dataset/docData200302.json'

# Tokenizer
tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")

# Numpy
sequence_has_ans = np.zeros(shape=[TOTAL_SIZE, MAX_LENGTH], dtype=np.int32)
segments_has_ans = np.zeros(shape=[TOTAL_SIZE, MAX_LENGTH], dtype=np.int32)
masks_has_ans = np.zeros(shape=[TOTAL_SIZE, MAX_LENGTH], dtype=np.int32)
cols_has_ans = np.zeros(shape=[TOTAL_SIZE, MAX_LENGTH], dtype=np.int32)
rows_has_ans = np.zeros(shape=[TOTAL_SIZE, MAX_LENGTH], dtype=np.int32)

label_ids = np.zeros(shape=[TOTAL_SIZE, MAX_MASKING], dtype=np.int32)
label_position = np.zeros(shape=[TOTAL_SIZE, MAX_MASKING], dtype=np.int32)
label_weight = np.zeros(shape=[TOTAL_SIZE, MAX_MASKING], dtype=np.float64)

## NamuParser
DOC_TITLE = 'title'
DOC_TEXT = 'text'
namuParser = NamuWikiParser(SRC_JSON_PATH)
namuTextExtractor = TextExtractor()
namuTableTextScorer = TableTextScorer()

## Table Head Extractor
tableHeaderExtractor = TableHeaderExtractor()

@dataclass
class TableRelation:
    table = None
    sentences: str = ''

@dataclass
class ParagraphRelation:
    paragraphIdx: int = None
    tableRelation = list()

## TEST MODE
TEST_TARGET = '리그 오브 레전드'
TEST_MODE = False
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
                ### Remove Deco Tables - 2021.09.17
                existedHeadTableList = tableHeaderExtractor.RemoveNoExistedTableHeaderTalbe(normalTableList)
                ###
                onlyTextTableList = namuTextExtractor.ExtractTextAtTable(existedHeadTableList) # only use normal tables

                ### Remove Deco Tables - 2021.09.17
                meaningTableList = namuParser.RemoveDecoTables(onlyTextTableList)
                ###

                paragraph[1] = meaningTableList

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

                    tableRelation.sentences = paragraph[2][val]
                    paragraphRelation.tableRelation.append(tableRelation)

            else:
                # exist only table
                if 0 < len(paragraph[1]): # table
                    for table in paragraph[1]:
                        tableRelation = TableRelation()
                        tableRelation.table = table
                        tableRelation.sentences = ''

                        paragraphRelation.tableRelation.append(tableRelation)

            paragraphRelationList.append(paragraphRelation)


        #### TEST ####
        if TEST_MODE:
            for test_paragraph in paragraphRelationList:
                print("para idx: ", test_paragraph.paragraphIdx)

                for test_tableRelation in test_paragraph.tableRelation:
                    print(test_tableRelation.table)
                    print(test_tableRelation.sentences)

                print('\n===============')

            if TEST_TEXT_PRINT:
                print(document[DOC_TEXT])
        ###############

        ### Tokenize
        for paragraphRelation in paragraphRelationList:
            paraIdx = paragraphRelation.paragraphIdx

            tableTokenList = []
            sentenceTokenList = []
            for tableRelation in paragraphRelation.tableRelation:
                if not tableRelation.table:
                    continue

                table = tableRelation.table
                sentences = tableRelation.sentences

                ## tokenize table
                for row in table:
                    for col in row:
                        wordTokenList = tokenizer.tokenize(col)
                        for wordToken in wordTokenList:
                            tableTokenList.append(wordToken)

                ## tokenize sentences
                sequenceText = ''
                splitSentenceList = sentences.split('.')
                for spSentence in splitSentenceList:
                    if 64 < len(tokenizer.tokenize(sequenceText)):
                        break
                    elif 0 >= len(spSentence):
                        continue
                    sequenceText += spSentence + '. '

                sentenceTokenList = tokenizer.tokenize(sequenceText)
                sentenceTokenList.insert(0, '[CLS]')
                sentenceTokenList.append('[SEP]')

                rowList = [ 0 for _ in range(len(sentenceTokenList)) ]
                colList = [ 0 for _ in range(len(sentenceTokenList)) ]
                segmentList = [ 0 for _ in range(len(sentenceTokenList)) ]

                ## MASKING
                labelTokenList = []
                labelPositionList = []

                for rIdx, row in enumerate(table):
                    for cIdx, col in enumerate(row):
                        if not col:
                            continue

                        wordTokenList = tokenizer.tokenize(col)
                        for wordToken in wordTokenList:
                            if -1 != sequenceText.find(col):
                                labelTokenList.append(wordToken)
                                labelPositionList.append(len(sentenceTokenList))
                                sentenceTokenList.append('[MASK]')
                            else:
                                sentenceTokenList.append(wordToken)

                            segmentList.append(1)
                            rowList.append(rIdx + 1)
                            colList.append(cIdx + 1)

                sentenceTokenListLen = len(sentenceTokenList)
                maskingNum = int(sentenceTokenListLen * 0.25 * rand()) # num_masking
                if MAX_MASKING < (maskingNum + len(labelTokenList)):
                    maskingNum = MAX_MASKING - len(labelTokenList)

                # masking tokens
                maskingLen = sentenceTokenListLen - 1
                if MAX_LENGTH < maskingLen:
                    maskingLen = MAX_LENGTH

                for _ in range(maskingNum):
                    maskIdx = int((maskingLen - 1) * rand())

                    # origin code were used index()
                    if ( maskIdx in labelPositionList) or \
                        ('[CLS]' == sentenceTokenList[maskIdx]) or \
                        ('[SEP]' == sentenceTokenList[maskIdx]):
                        continue

                    labelTokenList.append(sentenceTokenList[maskIdx])
                    labelPositionList.append(maskIdx)
                    sentenceTokenList[maskIdx] = '[MASK]'

                idList = tokenizer.convert_tokens_to_ids(tokens=sentenceTokenList)
                labelTokenIdList = tokenizer.convert_tokens_to_ids(tokens=labelTokenList)

                for idx in range(maskingLen):
                    print(len(sequence_has_ans), len(idList))
                    sequence_has_ans[COUNT, idx] = idList[idx]
                    segments_has_ans[COUNT, idx] = segmentList[idx]
                    masks_has_ans[COUNT, idx] = 1
                    cols_has_ans[COUNT, idx] = colList[idx]
                    rows_has_ans[COUNT, idx] = rowList[idx]

                labelTokenIdListLen = len(labelTokenIdList)
                if MAX_MASKING < labelTokenIdListLen:
                    labelTokenIdListLen = MAX_MASKING

                for idx in range(labelTokenIdListLen):
                    label_ids[COUNT, idx] = labelTokenIdList[idx]
                    label_position[COUNT, idx] = labelPositionList[idx]
                    label_weight[COUNT, idx] = 1.0

        COUNT += 1

#### end paragraph parsing loop
namuTokenizer = NamuTokenizer()
namuTokenizer.SaveTensorDataSet(COUNT, MAX_LENGTH, MAX_MASKING,
                                sequence_has_ans, segments_has_ans, masks_has_ans,
                                rows_has_ans, cols_has_ans, label_ids, label_position, label_weight)
