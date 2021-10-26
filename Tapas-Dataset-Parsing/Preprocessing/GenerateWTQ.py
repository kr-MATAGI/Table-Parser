import os
import json
import pandas as pd

from Definition.PreprocDef import *

class WtqGenerator:
    ### PRIVATE ###
    def __init__(self):
        self.isSetSrcFile = False
        self.isSetTableFile = False
        print("INIT - WTQ Generator")

    def __LoadTableCSV(self, targetTablePath):
        retTable = list()

        try:
            tableDataFrame = pd.read_csv(targetTablePath, sep="\t", encoding="utf-8")
        except:
            return retTable

        # Read Table Data
        tableHeadList = list(tableDataFrame.keys())
        retTable.append(tableHeadList)

        for idx, rowElem in tableDataFrame.iterrows():
            newRow = list()
            for head in tableHeadList:
                newRow.append(rowElem[head])
            retTable.append(newRow)

        return retTable

    ### PUBLIC ###
    def SetTableDirRootPath(self, tableRootPath):
        if not os.path.isdir(tableRootPath):
            print("ERROR - Check root of table dir,", tableRootPath)
            return

        self.tableRootPath = tableRootPath
        print("Set Table Root Path:", self.tableRootPath)

    def GenerateWtqDataset(self, targetFile):
        if not os.path.isfile(targetFile):
            print("ERROR - Check Target File,", tagetFile)
            return
        print("Set Target File:", targetFile)

        # Return value
        queryRelationList = list()

        # Read File
        targetDataFrame = pd.read_csv(targetFile, sep="\t", encoding="utf-8")

        for idx, rowElem in targetDataFrame.iterrows():
            if 0 == (idx % 1000):
                print(idx, "Processing...")
            queryRelation = QueryRelation()
            queryRelation.table2D = list()
            queryRelation.labelTags = list()
            queryRelation.query = ""
            queryRelation.answer = list()

            # Set Data
            targetTablePath = self.tableRootPath + "/" + rowElem["context"]
            targetTablePath = targetTablePath.replace(".csv", ".tsv")
            queryRelation.table2D = self.__LoadTableCSV(targetTablePath)
            if 0 >= len(queryRelation.table2D):
                continue
            queryRelation.query = rowElem["utterance"]
            queryRelation.answer = rowElem["targetValue"]
            queryRelationList.append(queryRelation)

        return queryRelationList

if "__main__" == __name__:
    wtqGenerator = WtqGenerator()

    # Set Root of Table Directory
    wtqGenerator.SetTableDirRootPath("./Dataset/WTQ")

    # Generate WTQ dataset
    tagetFile = "./Dataset/WTQ/data/training.tsv"
    queryRelationList = wtqGenerator.GenerateWtqDataset(tagetFile)