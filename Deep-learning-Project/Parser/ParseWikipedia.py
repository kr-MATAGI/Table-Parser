# Defintion
import re

from Definition.WikiDef import *
from Definition.WikiRegexDef import *

# Utils
from Utils.DataLoader import *
from Utils.WikiRegexUtil import *

### Method
def RemoveEmptyRowFromTable(tableList:list):
    retTableList = []

    for table in tableList:
        newTable = []
        for row in table:
            if 0 < len(row):
                newTable.append(row)
        retTableList.append(newTable)

    return retTableList

def RemoveWikipediaSyntax(tableList:list):
    retTableList = []

    for table in tableList:
        newTable = []
        for row in table:
            newRow = []
            for col in row:
                if re.search(WIKI_RE.TABLE_START.value, col):
                    newRow = []
                    break
                if re.search(WIKI_RE.TABLE_TITLE.value, col):
                    newRow = []
                    break

                newCol = col.strip()
                newCol = re.sub(WIKI_RE.TABLE_HEAD.value, "<th>", newCol)
                newCol = re.sub(WIKI_RE.CLASS.value, "", newCol)
                newCol = re.sub(WIKI_RE.BG_COLOR.value, "<bgc>", newCol)
                newCol = re.sub(WIKI_RE.ALIGN.value, "", newCol)

                # <BR />
                newCol = re.sub(WIKI_RE.BR.value, "", newCol)

                # File & media
                newCol = re.sub(WIKI_RE.FILE.value, "", newCol)
                newCol = re.sub(WIKI_RE.MEDIA.value, "", newCol)

                # Font shape
                if re.search(WIKI_RE.FONT_SHAPE_5.value, newCol):
                    fontShape = re.search(WIKI_RE.FONT_SHAPE_5.value, newCol).group(0)
                    convertFontShape = fontShape.replace("'''''", "")
                    newCol = newCol.replace(fontShape, convertFontShape)
                if re.search(WIKI_RE.FONT_SHAPE_3.value, newCol):
                    fontShape = re.search(WIKI_RE.FONT_SHAPE_3.value, newCol).group(0)
                    convertFontShape = fontShape.replace("'''", "")
                    newCol = newCol.replace(fontShape, convertFontShape)
                if re.search(WIKI_RE.FONT_SHAPE_2.value, newCol):
                    fontShape = re.search(WIKI_RE.FONT_SHAPE_2.value, newCol).group(0)
                    convertFontShape = fontShape.replace("''", "")
                    newCol = newCol.replace(fontShape, convertFontShape)

                # Special Character
                newCol = re.sub(WIKI_RE.SPECIAL_CHAR.value, "", newCol)
                newCol = re.sub(WIKI_RE.SUBP_SCRIPT.value, "", newCol)

                # Tag
                newCol = re.sub(WIKI_RE.SPAN_TAG.value, "", newCol)
                newCol = re.sub(WIKI_RE.MATH_TAG.value, "", newCol)

                # Redirect
                if re.search(WIKI_RE.REDIRECT.value, newCol):
                    corresStr = re.search(WIKI_RE.REDIRECT.value, newCol).group(0)
                    convertedStr = corresStr.replace("#넘겨주기 [[", "")
                    convertedStr = convertedStr.replace("]]", "")
                    newCol = newCol.replace(corresStr, convertedStr)

                # Free Link
                if re.search(WIKI_RE.FREE_LINK_ALT.value, newCol):
                    newCol = re.sub(WIKI_RE.FREE_LINK_LHS.value, "", newCol)
                    newCol = re.sub(WIKI_RE.FREE_LINK_CLOSED.value, "", newCol)

                if re.search(WIKI_RE.FREE_LINK_BASIC.value, newCol):
                    newCol = re.sub(WIKI_RE.FREE_LINK_OPEN.value, "", newCol)
                    newCol = re.sub(WIKI_RE.FREE_LINK_CLOSED.value, "", newCol)

                # External link
                if re.search(WIKI_RE.EXT_LINK_ALT.value, newCol):
                    corresStr = re.search(WIKI_RE.EXT_LINK_ALT.value, newCol).group(0)
                    convertedStr = re.sub(WIKI_RE.EXT_LINK_ALT_LHS.value, "", corresStr)
                    convertedStr = re.sub(r"\]", "", convertedStr)
                    newCol = newCol.replace(corresStr, convertedStr)

                # Cite
                if re.search(WIKI_RE.CITE.value, newCol):
                    corresStr = re.search(WIKI_RE.CITE.value, newCol).group(0)
                    convertedStr = re.split(WIKI_RE.VERTICAL_BAR.value, corresStr)[1]
                    newCol = newCol.replace(corresStr, convertedStr)


                # Vertical bar
                newCol = re.sub(WIKI_RE.VERTICAL_BAR.value, "", newCol)

                newCol = newCol.strip()
                newRow.append(newCol)

            if 0 < len(newRow):
                newTable.append(newRow)
        retTableList.append(newTable)

    return retTableList

def ParseWikipedia(wikiPage:WikiPage):
    wikiTable = WikiTable(title=wikiPage.title, tableList=[])

    # Parse table from text
    tableList = ParseWikiTableRegex(wikiPage.text)

    # Divide rows and cols by Table Syntax
    tableList = DivideTableRowColBySyntax(tableList)
    tableList = RemoveEmptyRowFromTable(tableList)

    # Remove Wikipeida Syntax
    tableList = RemoveWikipediaSyntax(tableList)

    # TEST
    for table in tableList:
        print()
        for row in table:
            print(row)

    return wikiTable

if "__main__" == __name__:
    # Parse Wikipedia
    for pageData in ReadWikiDataset("../Dataset/kor-wiki/test.xml"):
        wikipage = WikiPage(title=pageData[0], text=pageData[1])

        wikiTable = ParseWikipedia(wikipage)

