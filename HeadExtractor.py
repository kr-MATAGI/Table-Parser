import re
import numpy as np
from enum import Enum

## DefF
# Instance Type, link, image, digit, font, background color, and span
class INST_TYPE(Enum):
    NONE = 0
    LINK = 1
    IMAG = 2
    DIGIT = 3
    FONT = 4
    BG_COLOR = 5
    SPAN = 6

# Content pattern, Word(Str), Digit, Tag, specific charter
class CONTENT_PATT(Enum):
    NONE = 0
    WORD = 1
    DIGIT = 2
    TAG = 3
    SP_CHAR = 4

# Heurisitc Regex
HEURI_2_TBG = r'<tbg>{1}'
HEURI_2_BG = r'<bg>{1}'

HEURI_3_TEXT_ATTR = r'\'\'\'.+\'\'\''

HEURI_4_LINK = r'\[\[.+\]\]'
HEURI_4_IS_FLOAT = r'[\d]+\.[\d]+'
HEURI_4_IS_FONT = r'<ft>'
HEURI_4_IS_RBG_COLOR = r'<rbg>{1}'
HEURI_4_IS_SPAN = r'<rs>{1}|<cs>{1}'

HEURI_5_IS_FLOAT = HEURI_4_IS_FLOAT
HEURI_5_IS_TAG = HEURI_4_LINK

HEURI_6_ROW_SPAN = r'<rs>{1}'
HEURI_6_COL_SPAN = r'<cs>{1}'

HEURI_7_EMPTY = r'<[\w]+>|[\s]+'

class Extractor:
    ### VAR ###

    ### INIT ###
    def __init__(self):
        print('INIT Extractor !!')

    ### PRIVATE ###
    '''
        @Heuristic
            Heuristic 5.1. If a <th> tag expresses a cell, then it has a high probability of being part of a HEAD.
        @Note
            Namuwiki data is not used '<th>', just use '||'
    '''
    def __Heuristic_1(self, srcTable):
        pass

    '''
            @Heuristic
                If a table is divided into two areas by background color, 
                the upper-side area or the left-side area has a high probability of being a HEAD.    
        '''

    def __Heuristic_2(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.int32)

        # Check Divide with Background Color
        isTbg = False
        isBg = False
        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                if re.search(HEURI_2_TBG, col):
                    isTbg = True
                if re.search(HEURI_2_BG, col):
                    isBg = True


        # Add Score
        if (True == isTbg) and (True == isBg):
            for rIdx, row in enumerate(retNpTable):
                for cIdx, col in enumerate(row):
                    if (0 == rIdx) or (0 == cIdx):
                        retNpTable[rIdx, cIdx] = 1

        return retNpTable

    '''
        @Heuristic
            If a table is divided into two areas by font attributes,
            the upper-side area or the left-side area has a high probability of being a HEAD.
    '''
    def __Heuristic_3(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.int32)

        isTextAttr = False

        rowAttrList = [] # table[0][?] List
        colAttrList = [] # table[?][0] List

        # Check Text Attribute row[0] or col[0]
        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                if 0 == rIdx and re.search(HEURI_3_TEXT_ATTR, col):
                    rowAttrList.append((rIdx, cIdx))
                elif 0 == cIdx and re.search(HEURI_3_TEXT_ATTR, col):
                    colAttrList.append((rIdx, cIdx))

        # Add Score
        for idxPair in rowAttrList:
            retNpTable[idxPair[0], idxPair[1]] = 1
        for idxPair in colAttrList:
            retNpTable[idxPair[0], idxPair[1]] = 1

        return retNpTable

    '''
            Check Elements Type
        '''

    def __IsSameElements(self, targetList):
        retValue = True

        # Type Check
        firstElement = targetList[0]
        for idx in range(1, len(targetList)):
            if firstElement != targetList[idx]:
                retValue = False
                break

        return retValue


    '''
        @Heuristic
            If the cells in a row or a column are filled with a specific content instance type, 
            then a cell located in the extreme of the row or the column 
            (i.e., the left-hand or uppermost cell, respectively) has a high probability of being a part of the HEAD, 
            irrespective of its content instance type.
            In many meaningful tables, the content instance types
            (i.e., link, image, digit, font, background color, and span) are repetitive in some order in BODY.
    '''
    def __Heuristic_4(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.int32)

        typeTable = [ [ INST_TYPE.NONE for _ in range(tableShape[1]) ] for _ in range(tableShape[0]) ]

        ## Check Elements
        for rIdx, row in enumerate(srcTable):
            isRbg = False
            for cIdx, col in enumerate(row):
                # Check Link
                if re.search(HEURI_4_LINK, col):
                    typeTable[rIdx][cIdx] = INST_TYPE.LINK

                ## Check Image - Not Used, Remove Tag in parsing step

                # Check Digit
                elif str(col).isdigit() or re.search(HEURI_4_IS_FLOAT, col):
                    typeTable[rIdx][cIdx] = INST_TYPE.DIGIT

                # Check Font - TODO
                elif re.search(HEURI_4_IS_FONT, col):
                    typeTable[rIdx][cIdx] = INST_TYPE.FONT

                # Check Background color
                elif re.search(HEURI_4_IS_RBG_COLOR, col):
                    isRbg = True
                    typeTable[rIdx][cIdx] = INST_TYPE.BG_COLOR

                # Check Span
                elif re.search(HEURI_4_IS_SPAN, col):
                    typeTable[rIdx][cIdx] = INST_TYPE.SPAN

                if isRbg:
                    typeTable[rIdx][cIdx] = INST_TYPE.BG_COLOR

        ## Is same elements?
        rowMaxLen = tableShape[0]
        colMaxLen= tableShape[1]

        # Row
        for rIdx in range(1, rowMaxLen):
            targetList = []
            isSame = True
            for cIdx in range(1, colMaxLen):
                targetList.append(typeTable[rIdx][cIdx])

            isSame = self.__IsSameElements(targetList)
            if isSame:
                retNpTable[rIdx, 0] = 1

        # Col
        for cIdx in range(1, colMaxLen):
            targetList = []
            for rIdx in range(1, rowMaxLen):
                targetList.append(typeTable[rIdx][cIdx])

            isSame = self.__IsSameElements(targetList)
            if isSame:
                retNpTable[0, cIdx] = 1

        return retNpTable

    '''
        @Heuristic
            If the cells in a row or a column are filled with a specific content pattern, 
            then a cell located in the extreme of the row or the column
            (i.e., the most left-hand or uppermost, respectively) has a high probability of being a part of the HEAD, 
            irrespective of its content pattern.
            Cells have a particular sequence of token types.
            A token is a part of a sentence separated by specific delimiters such as space and punctuation marks,
            among others.
            We divide the into four type: word, digit, tag and specific charter.
    '''
    def __Heuristic_5(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.int32)

        # Init to Word
        patternTable = [ [ CONTENT_PATT.WORD for _ in range(tableShape[1]) ] for _ in range(tableShape[0]) ]
        specificChTable = [ [ '' for _ in range(tableShape[1]) ] for _ in range(tableShape[0]) ]

        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                # Check Digit
                if not str(col).isalpha() and (str(col).isdigit() or re.search(HEURI_5_IS_FLOAT, col)):
                    patternTable[rIdx][cIdx] = CONTENT_PATT.DIGIT

                # Check Tag
                elif re.search(HEURI_5_IS_TAG, col):
                    patternTable[rIdx][cIdx] = CONTENT_PATT.TAG

                # Insert Specific Charter (Ends with ac specific character.)
                else:
                    justStr = str(col).lstrip().rstrip()
                    justStr = re.sub(HEURI_2_TBG, '', justStr)
                    justStr = re.sub(HEURI_2_BG, '', justStr)
                    justStr = re.sub(HEURI_3_TEXT_ATTR, '', justStr)
                    justStr = re.sub(HEURI_4_LINK, '', justStr)
                    justStr = re.sub(HEURI_4_IS_SPAN, '', justStr)
                    justStr = re.sub(HEURI_4_IS_RBG_COLOR, '', justStr)
                    if 0 < len(justStr):
                        specificChTable[rIdx][cIdx] = justStr[-1]

        ## Check is same pattern (word, digit, tag)?
        # Row
        for rIdx in range(1, tableShape[0]):
            targetList = []
            isSame = True
            for cIdx in range(1, tableShape[1]):
                targetList.append(patternTable[rIdx][cIdx])

            isSame = self.__IsSameElements(targetList)
            if isSame:
                retNpTable[rIdx, 0] = 1

        # Col
        for cIdx in range(1, tableShape[1]):
            targetList = []


        ## Check is same specific character?


        return retNpTable

    '''
        @Heuristic
            The rows and columns containing the “rowspan” or the “colspan” attributes of the <td> tag can be estimated 
            as being part of a HEAD when they are located in the extreme row or the column 
            (the left-hand or uppermost areas, respectively).
    '''
    def __Heuristic_6(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.int32)

        colSpanList = [] # (row, idx), table[0][col]
        rowSpanList = [] # (row, idx), table[row][0]

        # Check Row/Col Span
        for rIdx, row in enumerate(srcTable):
            for cIdx, col in enumerate(row):
                if (0 == rIdx) and re.search(HEURI_6_COL_SPAN, col):
                    colSpanList.append((rIdx, cIdx))

                if (0 == cIdx) and re.search(HEURI_6_ROW_SPAN, col):
                    rowSpanList.append((rIdx, cIdx))

        # Add Score
        for spanPair in colSpanList:
            retNpTable[spanPair[0], spanPair[1]] = 1
        for spanPair in rowSpanList:
            retNpTable[spanPair[0], spanPair[1]] = 1

        return retNpTable

    '''
        @Heuristic
            If a table has an empty cell in the first row or first column, 
            the row and column that include that empty cell have a high probability of being the HEAD.
    '''
    def __Heuristic_7(self, srcTable):
        tableShape = (len(srcTable), len(srcTable[0]))
        retNpTable = np.zeros(tableShape, dtype=np.int32)

        # Check Empty table[0][0]
        cmpStr = re.sub(HEURI_7_EMPTY, '', srcTable[0][0])
        if 0 == len(cmpStr):
            # Add Score
            for ridx in range(tableShape[0]):
                retNpTable[ridx, 0] = 1
            for cIdx in range(tableShape[1]):
                retNpTable[0, cIdx] = 1
        return retNpTable

    '''
        @Note
            Compute (14), (15) equations of Section 5.3                         
    '''
    def __CoputeBinaryMatrices(self, scoreTableList):
        pass


    ### PUBLIC ###
    '''
        Extract Table Header
        @Note
            reference paper: A_scalable_hybrid_approach_for_extracting_head_components_from_Web_tables
            Please See a extracting heuristics of Section 6 in paper
        @Return
            Score Table List
    '''
    def GiveScoreToHeadCell(self, tableList):
        retTableList = []

        for table in tableList:
            tableScore = []

            # Use Heuristic
            # Not use Heuristic5_1, <th> was not included naum wiki data
            # resHeuri_1 = self.__Heuristic5_1(table)
            resHeuri_2 = self.__Heuristic_2(table) # Check <tbg> and <bg>
            resHeuri_3 = self.__Heuristic_3(table) # Check Text Attribute
            resHeuri_4 = self.__Heuristic_4(table)
            resHeuri_5 = self.__Heuristic_5(table)
            resHeuri_6 = self.__Heuristic_6(table)
            resHeuri_7 = self.__Heuristic_7(table)

            # Use Linear interpolation
            # Please See a Section 5.3 in paper
            finalTable = self.__CoputeBinaryMatrices([resHeuri_2, resHeuri_3, resHeuri_4,
                                                      resHeuri_5, resHeuri_6, resHeuri_7])

            # Append to return
            retTableList.append(finalTable)

        return retTableList