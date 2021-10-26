import random
import re

## RE
RE_IS_ALPHANUM = r"[a-zA-Z0-9]"
RE_IS_FLOAT = r"\b[0-9]+\.[0-9]+"

def MakeAlphanumTable(srcTable:list):
    if type(list()) != type(srcTable):
        print("Please use list() table,", type(srcTable))
        return

    alphanumTable = list()
    for row in srcTable:
        newRow = list()
        for col in row:
            newCol = ""
            for ch in col:
                if re.search(RE_IS_ALPHANUM, ch):
                    newCol += ch
                elif "," == ch:
                    pass
                elif "." == ch:
                    newCol += "."
                else:
                    newCol += " " # empty space

            # Judge int/float/str
            if newCol.isdecimal():
                newRow.append(int(newCol))
            elif re.search(RE_IS_FLOAT, newCol):
                newRow.append(float(newCol))
            else: # String
                newRow.append(newCol)

        alphanumTable.append(newRow)

    return alphanumTable