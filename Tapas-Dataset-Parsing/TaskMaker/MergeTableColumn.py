import random

class MergeColTableMaker:
    ### VAR ###


    ### PRIVATE ###
    def __init__(self):
        print("INIT - MergeColTableMaker")

    def __FilterOutTableByRowLen(self, baselineRowLen, totalTable):
        retFilteredTableList = list()

        for table in totalTable:
            if baselineRowLen <= len(table):
                retFilteredTableList.append(table)

        return retFilteredTableList

    ### PUBLIC ###
    def MakeMergedColumnTable(self, baselineTable, totalTable):
        retMergedTable = list()
        retUsedColIdx = list()
        retInsertedColIdx = list()

        # Check length of baseline table
        baselineRowLen = len(baselineTable)
        baselineColLen = len(baselineTable[0])

        # Filter out totalTable by baselineRowLen
        filteredTableList = self.__FilterOutTableByRowLen(baselineRowLen, totalTable)

        # Radon choose in filteredTables
        randChoseTable = random.choice(filteredTableList)

        # Slice Row if lager rowLen of randChoseTable
        if baselineRowLen < len(randChoseTable):
            randChoseTable = randChoseTable[:baselineRowLen]

        ## Insert Column Process
        # generate choose size
        chooseSize = random.randrange(1, 3)

        # random generate - using column index (randChoseTable)
        for chooseCnt in range(chooseSize):
            randCdx = random.randrange(0, len(randChoseTable[0]))
            while randCdx in retUsedColIdx:
                randCdx = random.randrange(0, len(randChoseTable[0]))
            retUsedColIdx.append(randCdx)
        retUsedColIdx.sort()

        # random generate - insert column index
        for chooseCnt in range(chooseSize):
            randCdx = random.randrange(0, baselineColLen)
            while randCdx in retInsertedColIdx:
                randCdx = random.randrange(0, baselineColLen)
            retInsertedColIdx.append(randCdx)
        retInsertedColIdx.sort()

        # Make Merged Table
        for chooseIdx in range(chooseSize):
            for rdx, row in enumerate(randChoseTable):
                for cdx, col in enumerate(row):
                    if cdx == retUsedColIdx[chooseIdx]:
                        baselineTable[rdx].insert(retInsertedColIdx[chooseIdx], col)
        retMergedTable = baselineTable

# TEST
        print(randChoseTable)
        print(retUsedColIdx)
        print(retInsertedColIdx)
        for row in baselineTable:
            print(row)

        return retMergedTable, retUsedColIdx, retInsertedColIdx


# Test
if "__main__" == __name__:
    # Example
    baselineTable = [ ['A','B','C','D','E'],
                      ['a','b','c','d','e'],
                      ['a','b','c','d','e'],
                      ['a','b','c','d','e']]

    totalTableList = list()

    table_1 = [ [1, 1, 5],
                [1, 1, 5],
                [1, 1, 5],
                [1, 1, 5]]

    table_2 = [ [2,2,2,2,5],
                [2,2,2,2,5],
                [2,2,2,2,5]]

    table_3 = [[3, 3, 3, 5],
               [3, 3, 3, 5],
               [3, 3, 3, 5],
               [3, 3, 3, 5],
               [3, 3, 3, 5],
               [3, 3, 3, 5]]

    table_4 = [[4, 4, 4, 5],
               [4, 4, 4, 5],
               [4, 4, 4, 5],
               [4, 4, 4, 5],
               [4, 4, 4, 5],
               [4, 4, 4, 5]]

    table_5 = [[6, 5],
               [6, 5],
               [6, 5],
               [6, 5]]

    totalTableList.append(table_1)
    totalTableList.append(table_2)
    totalTableList.append(table_3)
    totalTableList.append(table_4)
    totalTableList.append(table_5)

    # Call
    maker = MergeColTableMaker()
    maker.MakeMergedColumnTable(baselineTable, totalTableList)