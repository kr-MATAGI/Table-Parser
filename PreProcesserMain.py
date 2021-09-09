from NamuWiki.NamuParser import DOC_TEXT, DOC_TITLE, NamuWikiParser
from HeadExtractor import Extractor

# Definition
SRC_JSON_PATH = './dataset/docData200302.json'
WRITE_TABLE_DEST_PATH = './Tables'

if __name__ == '__main__':
    # Make instance    
    namuParser = NamuWikiParser(SRC_JSON_PATH)
    headExtractor = Extractor()

    docCount = 0
    for docItem in namuParser.ParsingJSON():
        docCount += 1

        if 0 == docCount % 1000:
            print('Processing....', docCount)

        tableList = namuParser.ParseTableFromText(docItem[DOC_TEXT])

        if 0 < len(tableList):
            newTableList = []
            namuParser.ModifyHTMLTags(tableList)

            for table in tableList:
                preprocessedTable = namuParser.PreprocessingTable(table)

                if 2 <= len(preprocessedTable):
                    newTableList.append(preprocessedTable)
            normalTableList, infoBoxList = namuParser.ClassifyNormalTableOrInfoBox(newTableList)
            #print(normalTableList)
            #print(infoBoxList)

            # Write Table to Directory
            namuParser.WriteTableToFile(normalTableList, docItem[DOC_TITLE], WRITE_TABLE_DEST_PATH+'/normal', True)
            namuParser.WriteTableToFile(infoBoxList, docItem[DOC_TITLE], WRITE_TABLE_DEST_PATH+'/infobox', False)

            # Finish Parse and Regex Expression Process
            tableList = normalTableList
            tableList.extend(infoBoxList)

            # Extract Table Head and Make Tensor
            #scoreTable = headExtractor.GiveScoreToHeadCell(newTableList)