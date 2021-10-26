import random

from Definition.QueryDef import *
from Utils.QueryUtils import *

class QueryGenerator:
    ### VAR ###


    ### PRIVATE ###
    def __init__(self):
        print("INIT - Query Generator !")

    def __ChooseArg(self, enumArg):
        '''
        :param enum: Enum class
        :note
            If enum.value is None, it will be re-generate...
        :return: retArg: chose item by random from list
        '''
        if type(Enum) != type(enumArg):
            print("__ChooseArg - Check input type")
            return

        enumList = [item for item in enumArg]
        retArg = random.choice(enumList)
        while not retArg.value:
            retArg = random.choice(enumList)

        return retArg

    def __ChooseColumn(self, alphanumTable):
        if type(list()) != type(alphanumTable):
            print("__ChooseColumn - Check input type")
            return

        rowLen = len(alphanumTable)
        colLen = len(alphanumTable[0])

        retChosePos = POS()
        retChosePos.row = 0
        retChosePos.col = random.randrange(0, colLen)

        return retChosePos

    def __VerifyConditionChoseItems(self, alphanumTable, chosePos, choseArg):
        '''
        :param alphanumTable: only included alphanum items
        :param chosePos: head cell position
        :param choseArg: WhenArg / StateArg
        :return: isValid: Boolean
        '''
        isValid = False

        rowLen = len(alphanumTable)
        colLen = len(alphanumTable[0])

        colItemList = [alphanumTable[idx][chosePos.col] for idx in range(1, rowLen)]

        if WhenArg.GREATER == choseArg or \
            WhenArg.LESS == choseArg:
            try:
                for item in colItemList:
                    int(float(item))
                isValid = True
            except:
                return isValid

        elif WhenArg.IS == choseArg:
            isValid = True

        return isValid

    def __GenerateConditionItems(self, alphanumTable, chosePos, choseArg):
        '''
        :param alphanumTable: only include alphanum items
        :param chosePos: head cell position
        :param choseArg: WhenArg
        :return:
            retItemsPos: head and items positions in table
            randVal: If arg is greater / then, the value is return
        '''
        retItemsPos = list()
        randVal = None

        rowLen = len(alphanumTable)
        colLen = len(alphanumTable[0])

        # Not include table head
        choseColItemList = [alphanumTable[rdx][chosePos.col] for rdx in range(1, rowLen)]

        if WhenArg.GREATER == choseArg or \
            WhenArg.LESS == choseArg:
            minVal = round(min(choseColItemList))
            maxVal = round(max(choseColItemList))
            randVal = minVal
            if minVal != maxVal:
                randVal = random.randrange(minVal, maxVal)

            # Search Item
            searchedItemList = list()
            if WhenArg.GREATER == choseArg:
                searchedItemList = [item for item in choseColItemList
                                    if item > randVal]
            elif WhenArg.LESS == choseArg:
                searchedItemList = [item for item in choseColItemList
                                    if item < randVal]

            if 0 == len(searchedItemList):
                choseArg = WhenArg.IS
            else:
                uniqItemList = set(searchedItemList)
                for uniqItem in uniqItemList:
                    for rdx, colItem in enumerate(choseColItemList):
                        if uniqItem == colItem:
                            itemPos = POS()
                            itemPos.row = (rdx+1)
                            itemPos.col = chosePos.col
                            retItemsPos.append(itemPos)

        if WhenArg.IS == choseArg:
            randVal = random.choice(choseColItemList)
            itemPos = POS()
            itemPos.row = (choseColItemList.index(randVal) + 1)
            itemPos.col = chosePos.col
            retItemsPos.append(itemPos)

        retItemsPos.insert(0, chosePos)
        return retItemsPos, randVal

    def __MakeConditionList(self, alphanumTable):
        '''
        :param alphanumTable: only include alphanum data
        :return:
            retCondiPosList: list of item's positions (Type: POS)
            choseArg: generate WhenArg by random
            condiRandVal: if arg is greater / less, it is return
        '''
        retCondiPosList = list()

        # Choose Col/Arg
        choseCondiPos = None
        choseArg = None

        while True:
            # Choose Column
            choseCondiPos = self.__ChooseColumn(alphanumTable)

            # Choose Argument
            choseArg = self.__ChooseArg(WhenArg)

            # Verify
            isValid = self.__VerifyConditionChoseItems(alphanumTable, choseCondiPos, choseArg)
            if isValid:
                break

        # Make Condition - index 0 is table head
        retCondiPosList, condiRandVal = self.__GenerateConditionItems(alphanumTable, choseCondiPos, choseArg)

        return retCondiPosList, choseArg, condiRandVal

    def __VeriftyStatementChoseItems(self, alphanumTable, choseStatePos, condiPosList, choseArg):
        '''
        :param alphanumTable: only include alphanum data
        :param choseStatePos: statement head position
        :param condiPosList: condition list of cell positions
        :param choseArg: statement argument
        :return: isValid: Boolean
        '''
        isValid = False

        # Same Head
        if choseStatePos == condiPosList[0]:
            return isValid

        colItemList = [alphanumTable[item.row][choseStatePos.col] for idx, item in enumerate(condiPosList)
                       if 0 != idx]

        if StateArg.GREATER == choseArg or \
            StateArg.LESS == choseArg or \
            StateArg.SUM == choseArg or \
            StateArg.AVG == choseArg or \
            StateArg.GREATEST == choseArg or \
            StateArg.LOWEST == choseArg:

            if 2 > len(colItemList):
                return isValid
            try:
                for item in colItemList:
                    int(float(item))
                isValid = True
            except:
                return isValid

        elif StateArg.DIFF == choseArg or \
            StateArg.SAME == choseArg or \
            StateArg.FIRST == choseArg or \
            StateArg.LAST == choseArg:

            if 2 > len(colItemList):
                return isValid

        elif StateArg.IS == choseArg or \
            StateArg.COUNT == choseArg:
            isValid = True

        return isValid

    def __GenerateStatementItems(self, alphanumTable, choseStatePos, condiPosList, choseArg):
        '''
        :param alphanumTable: only include alphanum data
        :param choseStatePos: head cell position
        :param condiPosList: list of condition item positions
        :param choseArg: StateArg
        :return:
            retItemPos: chose cell position (Type: POS)
            randVal: if arg is greater / less, it is return
        '''
        retItemPos = list()
        randVal = None

        condiItemRowList = [item.row for idx, item in enumerate(condiPosList) if 0 != idx]
        if StateArg.DIFF == choseArg or \
            StateArg.SAME == choseArg:
            randRow = random.choice(condiItemRowList)
            itemPos = POS()
            itemPos.row = randRow
            itemPos.col = choseStatePos.col
            retItemPos.append(itemPos)

        elif StateArg.FIRST == choseArg or \
            StateArg.LAST == choseArg or \
            StateArg.COUNT == choseArg or \
            StateArg.SUM == choseArg or \
            StateArg.AVG == choseArg or \
            StateArg.GREATEST == choseArg or \
            StateArg.LOWEST == choseArg:
            for row in condiItemRowList:
                itemPos = POS()
                itemPos.row = row
                itemPos.col = choseStatePos.col
                retItemPos.append(itemPos)

        elif StateArg.GREATER == choseArg or \
            StateArg.LESS == choseArg:
            itemValList = [alphanumTable[row][choseStatePos.col] for row in condiItemRowList]

            minVal = round(min(itemValList))
            maxVal = round(max(itemValList))

            if StateArg.LESS == choseArg:
                randVal = int(maxVal * 1.5)
            elif StateArg.GREATER == choseArg:
                randVal = int(minVal * 0.7)

            for row in condiItemRowList:
                itemPos = POS()
                itemPos.row = row
                itemPos.col = choseStatePos.col
                retItemPos.append(itemPos)

        if StateArg.IS == choseArg:
            randRow = random.choice(condiItemRowList)
            itemPos = POS()
            itemPos.row = randRow
            itemPos.col = choseStatePos.col
            retItemPos.append(itemPos)


        retItemPos.insert(0, choseStatePos)
        return retItemPos, randVal

    def __MakeStatementList(self, alphanumTable, condiPosList):
        '''
        :param alphanumTable: only include alphanum data
        :return:
            retItemPosList: list of item's positions (Type: POS)
            choseArg: generate StateArg by random
            stateRandVal: if greater / less, it is return
        '''
        retStatePosList = list()

        # Choose Col / Arg
        choseStatePos = None
        chooseArg = None

        while True:
            # Choose Column
            choseStatePos = self.__ChooseColumn(alphanumTable)

            # Choose Argument
            choseArg = self.__ChooseArg(StateArg)

            # Verify
            isValid = self.__VeriftyStatementChoseItems(alphanumTable, choseStatePos,
                                                        condiPosList, choseArg)
            if isValid:
                break

        # Make Statement - index 0 is table head
        retStatePosList, stateRandVal = self.__GenerateStatementItems(alphanumTable, choseStatePos,
                                                                      condiPosList, choseArg)

        return retStatePosList, choseArg, stateRandVal

    def __MakeConditionQuery(self, originTable, alphanumTable, condiPosList, condiArg, condiRandVal):
        retStrList = list()
        retStrList.append("when")
        retStrList.append(str(originTable[condiPosList[0].row][condiPosList[0].col]))
        retStrList.append(str(condiArg.value))
        if condiRandVal:
            retStrList.append(str(condiRandVal))

        return retStrList


    def __MakeStatementQuery(self, originTable, alphanumTable, statePosList, stateArg, stateRandVal):
        retStrList = list()

        headPos = statePosList[0]
        if StateArg.IS == stateArg:
            retStrList.append(originTable[headPos.row][headPos.col])
            retStrList.append(str(stateArg.value))
            retStrList.append(originTable[statePosList[1].row][statePosList[1].col])

        elif StateArg.DIFF == stateArg or \
            StateArg.SAME == stateArg:
            retStrList.append(originTable[statePosList[1].row][statePosList[1].col])
            retStrList.append(str(stateArg.value))
            retStrList.append(originTable[statePosList[2].row][statePosList[2].col])

        elif StateArg.FIRST == stateArg or \
            StateArg.LAST == stateArg:
            sortedPosList = statePosList[1:]
            sortedPosList.sort(key=lambda x:x.row)

            if StateArg.FIRST == stateArg:
                firstItemPos = sortedPosList[0]
                retStrList.append(originTable[firstItemPos.row][firstItemPos.col])
                retStrList.append(str(stateArg.value))
                retStrList.append(originTable[statePosList[0].row][statePosList[0].col])
            elif StateArg.LAST == stateArg:
                lastItemPos = sortedPosList[-1]
                retStrList.append(originTable[lastItemPos.row][lastItemPos.col])
                retStrList.append(str(stateArg.value))
                retStrList.append(originTable[statePosList[0].row][statePosList[0].col])

        elif StateArg.COUNT == stateArg:
            countVal = len(statePosList) - 1
            retStrList.append(str(countVal))
            retStrList.append(str(stateArg.value))
            retStrList.append(originTable[statePosList[0].row][statePosList[0].col])

        elif StateArg.GREATER == stateArg or \
            StateArg.LESS == stateArg:
            retStrList.append(originTable[statePosList[0].row][statePosList[0].col])
            retStrList.append(str(stateArg.value))
            retStrList.append(str(stateRandVal))

        elif StateArg.SUM == stateArg or \
            StateArg.AVG == stateArg:
            itemValueList = [alphanumTable[pos.row][pos.col] for pos in statePosList[1:]]
            sumVal = sum(itemValueList)

            if StateArg.SUM == stateArg:
                retStrList.append(str(sumVal))
            elif StateArg.AVG == stateArg:
                retStrList.append(str(round(sumVal/len(itemValueList), 2)))
            retStrList.append(str(stateArg.value))
            retStrList.append(originTable[statePosList[0].row][statePosList[0].col])

        elif StateArg.GREATEST == stateArg or \
            StateArg.LOWEST == stateArg:
            sortedValueList = [alphanumTable[pos.row][pos.col] for pos in statePosList[1:]]
            sortedValueList.sort()

            if StateArg.GREATEST == stateArg:
                retStrList.append(str(sortedValueList[-1]))
            elif StateArg.LOWEST == stateArg:
                retStrList.append(str(sortedValueList[0]))
            retStrList.append(str(stateArg.value))
            retStrList.append(originTable[statePosList[0].row][statePosList[0].col])

        return retStrList

    ### PUBLIC ###
    def MakeQuery(self, originTable, alphanumTable):
        if type(list()) != type(originTable) or \
            type(list()) != type(alphanumTable):
            print("MakeQuery - Check input table types,", type(originTable), type(alphanumTable))
            return

        ## Condition Positions / Arg
        conditionItemPosList, whenArg, condiRandVal = self.__MakeConditionList(alphanumTable)

        ## Statement Positions / Arg
        stateItemPosList, stateArg, stateRandVal = self.__MakeStatementList(alphanumTable, conditionItemPosList)

        ## Make Condition Query String
        conditionQuery = self.__MakeConditionQuery(originTable, alphanumTable,
                                                   conditionItemPosList, whenArg, condiRandVal)

        ## Make Statement Query String
        statementQuery = self.__MakeStatementQuery(originTable, alphanumTable,
                                                   stateItemPosList, stateArg, stateRandVal)

        print(conditionItemPosList, whenArg, condiRandVal)
        print(stateItemPosList, stateArg, stateRandVal)

        endQuery = statementQuery
        endQuery.extend(conditionQuery)
        print(" ".join(endQuery).lower())


if "__main__" == __name__:
    testExample_1 = list()
    testExample_1.append(['Country', 'Player', 'Rank', 'Seed'])
    testExample_1.append(['JPN', 'Go Soeda', '107', '1'])
    testExample_1.append(['THA', 'Danai Udomchoke', '160', '2'])
    testExample_1.append(['AUS', 'Brydan Klein', '206', '3'])
    testExample_1.append(['AUS', 'Colin Ebelthite', '243', '4'])
    testExample_1.append(['AUS', 'Joseph Sirianni', '246', '5'])
    testExample_1.append(['AUS', 'Marinko Matosevic', '283', '6'])
    testExample_1.append(['AUS', 'Nick Lindahl', '312', '7'])
    testExample_1.append(['RSA', 'Raven Klaasen', '327', '8'])


    testExample_2 = list()
    testExample_2.append(['Rank', 'Player', 'Country', 'Earnings', 'Events', 'Wins'])
    testExample_2.append(['1', 'Greg Norman', 'Australia', '1,654,959', '1.6', '3'])
    testExample_2.append(['2', 'Billy Mayfair', 'United States', '1,543,192', '2.8', '2'])
    testExample_2.append(['3', 'Lee Janzen', 'United States', '1,378,966', '2.8', '3'])
    testExample_2.append(['4', 'Corey Pavin', 'United States', '1,340,079', '2.2', '2'])
    testExample_2.append(['5', 'Steve Elkington', 'Australia', '1,254,352', '2.1', '2'])

    #----------------------------------------------

    srcTable = testExample_1

    generator = QueryGenerator()
    alphanumTable = MakeAlphanumTable(srcTable)

    generator.MakeQuery(originTable=srcTable, alphanumTable=alphanumTable)




