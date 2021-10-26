import json
from Parser.Definition import TottoDef

class TottoParser:
    ### VAR ###
    _srcFilePath = None

    ### PRIVATE ###
    def __init__(self, srcFilePath:str):
        self._srcFilePath = srcFilePath
        print("INIT - srcFilePath: ", self._srcFilePath)

    def _InsertToDataClass(self, srcTable, srcCells, srcSent):
        tottoSection = TottoDef.TottoSection()
        tottoSection.table = list()
        tottoSection.highlightInfo = list()
        tottoSection.sentences = list()

        # Table
        for row in srcTable:
            newRow = list()
            for col in row:
                tottoTableCell = TottoDef.TottoTableCell()
                tottoTableCell.value = col["value"]
                tottoTableCell.colSpan = col["column_span"]
                tottoTableCell.rowSpan = col["row_span"] - 1

                newRow.append(tottoTableCell)
            tottoSection.table.append(newRow)

        # Highlighted Cells
        for cell in srcCells:
            pos_x = cell[0]
            pos_y = cell[1]

            tottoSection.highlightInfo.append((pos_x, pos_y))

        # Sentences
        for sentenceObj in srcSent:
            tottoSentences = TottoDef.TottoSentences()
            if 0 < len(sentenceObj["original_sentence"]):
                tottoSentences.origin = sentenceObj["original_sentence"]

            if 0 < len(sentenceObj["sentence_after_deletion"]):
                tottoSentences.afterDeletion = sentenceObj["sentence_after_deletion"]

            if 0 < len(sentenceObj["sentence_after_ambiguity"]):
                tottoSentences.afterAmbiguity = sentenceObj["sentence_after_ambiguity"]

            if 0 < len(sentenceObj["final_sentence"]):
                tottoSentences.final = sentenceObj["final_sentence"]

            tottoSection.sentences.append(tottoSentences)

        return tottoSection

    def _Make2DTable(self, srcTable):
        retTable = None

        maxRowLen = len(srcTable)
        maxColLen = 0

        # Compute max len(col) + colspan Count
        for row in srcTable:
            currColLen = 0
            for col in row:
                currColLen += int(col.colSpan)

            maxColLen = maxColLen if maxColLen > currColLen else currColLen

        # Make Empty 2D list
        retTable = list()

        ## Convert span cell
        fillTable = list()
        # colSpan
        for rIdx, row in enumerate(srcTable):
            fillRow = list()
            for cIdx, col in enumerate(row):
                for spanCnt in range(col.colSpan):
                    fillRow.append(col)
            fillTable.append(fillRow)

        # rowSpan
        for rIdx, row in enumerate(fillTable):
            if 0 != rIdx:
                prevRow = fillTable[rIdx-1]

                for cIdx in range(len(prevRow)):
                    if 1 <= prevRow[cIdx].rowSpan:
                        spanRow = TottoDef.TottoTableCell()
                        spanRow.value = prevRow[cIdx].value
                        spanRow.colSpan = prevRow[cIdx].colSpan
                        spanRow.rowSpan = prevRow[cIdx].rowSpan - 1
                        fillTable[rIdx].insert(cIdx, spanRow)

        # Extract Text from totto table
        for row in fillTable:
            retRow = list()
            for col in row:
                retRow.append(col.value)
            retTable.append(retRow)

        return retTable

    def _MakeConcatSent(self, srcSentList):
        retStr = ""

        for sent in srcSentList:
            retStr += (sent.origin + " ")
        return retStr

    ### PUBLIC ###
    def ParseToTTO(self) -> None:
        if not self._srcFilePath:
            print("Plz check file path:", self._srcFilePath)
            return

        # Variable
        retSection = list() # [ [table: list(TottoTableCell), highlight: list(), sentences: concat String] ]

        # Read File
        with open(self._srcFilePath, mode="r", encoding="utf-8") as srcFile:
            readLineCount = 0
            while True:
                srcLine = srcFile.readline()
                readLineCount += 1

                if not srcLine:
                    print("Completed - Parsing")
                    break
                
                # if 0 == (readLineCount % 1000):
                #     print(f"({readLineCount})Read Line: {srcLine}")

                parser = json.loads(srcLine)
                jsonTable = parser["table"]
                jsonCells = parser["highlighted_cells"]
                jsonSentences = parser["sentence_annotations"]

                # Insert to data structure
                tottoSection = self._InsertToDataClass(jsonTable, jsonCells, jsonSentences)

                # Make Table
                table2D = self._Make2DTable(tottoSection.table)

                # Make Concat Sentences
                concatSent = self._MakeConcatSent(tottoSection.sentences)
                
                # append to results
                retSection.append( [table2D, tottoSection.highlightInfo, concatSent] )

                if 0 == readLineCount % 2000:
                    print("-----------------")
                    print(table2D[0])
                    print(table2D[1])
                    if 2 < len(table2D) : print(table2D[2])
