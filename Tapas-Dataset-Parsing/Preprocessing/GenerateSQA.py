import os
import re
import pandas as pd

from Definition.PreprocDef import *

RE_LABEL_TAG = r"\(\d+, \d+\)"

class SQAGenerator:
    ### VAR ###

    ### PRIVATE ###
    def __init__(self):
        print("INIT - SQA Generator")

    def __LoadTableCSV(self, tableName):
        retTable = list()

        tablePath = self.tableCSV_path + "/" + tableName
        tableDataFrame = pd.read_csv(tablePath, sep=",", encoding="utf-8")

        # Read Table Data
        tableHeadList = list(tableDataFrame.keys())
        retTable.append(tableHeadList)

        for idx, rowElem in tableDataFrame.iterrows():
            newRow = list()
            for head in tableHeadList:
                newRow.append(rowElem[head])
            retTable.append(newRow)

        return retTable

    def __ConvertLabelTags(self, labelTags):
        retValList = list()

        labelTags = labelTags.replace('[', '')
        labelTags = labelTags.replace(']', '')
        labelTags = labelTags.replace('\'', '')
        labelTags = re.findall(RE_LABEL_TAG, labelTags)

        # Re-make
        for item in labelTags:
            item = item.replace("(", "")
            item = item.replace(")", "")
            splitItem = item.split(",")
            row = int(splitItem[0])
            col = int(splitItem[1])
            retValList.append((row, col))

        return retValList


    ### PUBLIC ###
    def SetDataSetFiles(self, table_csv_path, srcFileList):
        self.tableCSV_path = table_csv_path
        self.srcFileList = srcFileList

    def ConvertSqaDataset(self):
        print("Convert Start !")
        print("table csv path:", self.tableCSV_path)
        print("srcFile List:", self.srcFileList)

        #Init
        queryRelationList = list()

        for srcFile in srcFileList:
            srcDataframe = pd.read_csv("./Dataset/SQA/"+srcFile, sep="\t", encoding="utf-8")

            for idx, rowElement in srcDataframe.iterrows():
                queryRelation = QueryRelation()
                queryRelation.table2D = list()
                queryRelation.labelTags = list()
                queryRelation.query = ""
                queryRelation.answer = list()

                question = rowElement["question"]
                tableFile = rowElement["table_file"].split("/")[-1]
                answerCoord = rowElement["answer_coordinates"]
                answerText = rowElement["answer_text"]

                # Load Table CSV
                queryRelation.table2D = self.__LoadTableCSV(tableFile)
                queryRelation.labelTags = self.__ConvertLabelTags(answerCoord)
                queryRelation.query = question
                queryRelation.answer = answerText

                queryRelationList.append(queryRelation)

        return queryRelationList


if "__main__" == __name__:
    # Config
    tableCSV_Path =  "./Dataset/SQA/table_csv"
    srcFileList = ["random-split-1-train.tsv"]

    # INIT
    sqaGenerator = SQAGenerator()
    sqaGenerator.SetDataSetFiles(tableCSV_Path, srcFileList)

    # Convert Dataset
    tableRelationList = sqaGenerator.ConvertSqaDataset()
