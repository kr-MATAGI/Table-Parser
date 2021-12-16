import os
import json

from Definition.PreprocDef import *
from lib.dbengine import DBEngine

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


    def GenerateWikiDataset(self, tableDict, dbPath):
        queryRelationList = list()

        if not self.isSetSrcFile:
            print("ERR - Set Src File Path !")
            return

        print("Start - Generate Wiki Dataset")
        print(f"srcFile: {self.srcFile}\ntableFile: {self.tableFile}")

        dbEngine = DBEngine(fdb=dbPath)
        with open(self.srcFile, mode="r", encoding="utf-8") as srcFile:
            procCount = 0
            while True:
                jsonLine = srcFile.readline()
                if not jsonLine:
                    break

                procCount += 1
                if 0 == (procCount % 500):
                    print("ProcCount ", procCount, "-", jsonLine)

                queryRelation = QueryRelation()
                queryRelation.table2D = list()
                queryRelation.labelTags = list()
                queryRelation.query = ""
                queryRelation.answer = list()

                parser = json.loads(jsonLine)
                tableId = parser["table_id"]
                question = parser["question"]
                sqlObj= parser["sql"]
                sel = sqlObj["sel"]
                agg = sqlObj["agg"]
                conds = sqlObj["conds"]

                # talbe mapping with table id
                table2D = tableDict[tableId]

                queryRelation.table2D = table2D
                queryRelation.query = question
                # queryRelation.labelTags.append((0, int(sel)))

                # Exec SQL Query
                if 0 < len(conds):
                    try:
                        dbResultList, queryType, additionalList = dbEngine.execute(table_id=tableId,
                                         select_index=sel,
                                         aggregation_index=agg,
                                         conditions=conds)
                    except:
                        continue

                    for cond in conds:
                        #queryRelation.labelTags.append((0, int(cond[0])))
                        pass

                    for dbResult in dbResultList:
                        if queryType.name == QueryType.NONE.name:
                            rdx = dbResult["rdx"]
                            result = dbResult["result"]

                            if None != result:
                                queryRelation.answer.append(result)
                                queryRelation.labelTags.append((int(rdx)-1, int(sel)))
                        else:
                            # COUNT, MAX, MIN, SUM, AVG
                            result = dbResult["result"]
                            if None != result:
                                queryRelation.answer.append(result)
                                for addi in additionalList:
                                    rdx = addi["rdx"]
                                    queryRelation.labelTags.append((int(rdx)-1, int(sel)))
                            else:
                                queryRelation.answer.append(0)

                    queryRelationList.append(queryRelation)
                else:
                    continue

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

    # Make Generated dataset
    dbPath = "./Dataset/WikiSQL/data/train.db"
    queryRelationList = wikiSqlGenerator.GenerateWikiDataset(tableDict, dbPath)
    print(len(queryRelationList))
