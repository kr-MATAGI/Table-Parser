import os
import json

from Definition.PreprocDef import *

class WikiSqlGenerator:
    ### PRIVATE ###
    def __init__(self):
        self.isSetSrcFile = False
        self.isSetTableFile = False
        print("INIT - WikiSql Generator")

    ### PUBLIC ###
    def SetSourceFilePath(self, srcFile):
        if not os.path.isfile(srcFile):
            print("Check File -", srcFile)
            return

        self.isSetSrcFile = True
        self.srcFile = srcFile

    def SetTableFilePath(self, tableFile):
        if not os.path.isfile(tableFile):
            print("Check File -", tableFile)
            return

        self.isSetTableFile = True
        self.tableFile = tableFile

    def ConvertTableData(self):
        if not self.isSetTableFile:
            print("ERR - Set Table File Path !")
            return

        # Return variable
        tableDict = dict() # Key is table's id

        with open(self.tableFile, mode="r", encoding="utf-8") as tableFile:
            print("Convert Table Data Path -", self.tableFile)

            while True:
                jsonLine = tableFile.readline()

                if not jsonLine:
                    break

                parser = json.loads(jsonLine)

                id = parser["id"]
                headList = parser["header"]
                rowList = parser["rows"]

                table2D = list()
                table2D.append(headList)
                for row in rowList:
                    table2D.append(row)

                tableDict[id] = table2D

        print("End to Convert Table !")
        return tableDict


    def GenerateWikiDataset(self, tableDict):
        queryRelationList = list()

        if not self.isSetSrcFile:
            print("ERR - Set Src File Path !")
            return

        print("Start - Generate Wiki Dataset")
        print(f"srcFile: {self.srcFile}\ntableFile: {self.tableFile}")

        with open(self.srcFile, mode="r", encoding="utf-8") as srcFile:

            while True:
                jsonLine = srcFile.readline()
                if not jsonLine:
                    break

                queryRelation = QueryRelation()
                queryRelation.table2D = list()
                queryRelation.labelTags = list()
                queryRelation.query = ""
                queryRelation.answer = list()

                parser = json.loads(jsonLine)
                tableId = parser["table_id"]
                question = parser["question"]
                sqlObj= parser["sql"]
                condList = sqlObj["conds"]
                answer = ""
                if 0 < len(condList): # Empty conds is existed
                    answer = condList[0][-1]

                # talbe mapping with table id
                table2D = tableDict[tableId]

                queryRelation.table2D = table2D
                queryRelation.query = question
                queryRelation.answer = answer

                queryRelationList.append(queryRelation)

        return queryRelationList

if "__main__" == __name__:
    wikiSqlGenerator = WikiSqlGenerator()

    # Set Path
    srcFile = "./Dataset/WikiSQL/data/train.jsonl"
    tableFile = "./Dataset/WikiSQL/data/train.tables.jsonl"
    wikiSqlGenerator.SetSourceFilePath(srcFile)
    wikiSqlGenerator.SetTableFilePath(tableFile)

    # Convert Origin Table to 2D List
    tableDict = wikiSqlGenerator.ConvertTableData()
    print(tableDict["1-1000181-1"])
    exit()

    # Make Generate dataset
    queryRelationList = wikiSqlGenerator.GenerateWikiDataset(tableDict)
    print(len(queryRelationList))
