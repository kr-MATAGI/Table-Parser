from NamuWiki.NamuParser import DOC_TEXT, DOC_TITLE, NamuWikiParser
from HeadExtractor import TableHeaderExtractor

# Definition
SRC_JSON_PATH = './dataset/docData200302.json'
WRITE_TABLE_DEST_PATH = './Tables'

# TEST
TEST_TAGET_TITLE = '크레이지레이싱 카트라이더' #'백 평짜리 숲(킹덤 하츠)'
TEST_MODE = True

if __name__ == '__main__':

    # Make instance
    namuParser = NamuWikiParser(SRC_JSON_PATH)
    headExtractor = TableHeaderExtractor()

    docCount = 0
    for docItem in namuParser.ParsingJSON():
        docCount += 1

        if 0 == docCount % 1000:
            print('Processing....', docItem[DOC_TITLE], docCount)

        #### TEST ####
        if TEST_MODE and TEST_TAGET_TITLE != docItem[DOC_TITLE]: continue

        tableList = namuParser.ParseTableFromText(docItem[DOC_TEXT])

        if 0 < len(tableList):
            newTableList = []
            modifiedTableList = namuParser.ModifyHTMLTags(tableList)

            for table in modifiedTableList:
                preprocessedTable = namuParser.PreprocessingTable(table)

                if 2 <= len(preprocessedTable):
                    newTableList.append(preprocessedTable)
            normalTableList, infoBoxList = namuParser.ClassifyNormalTableOrInfoBox(newTableList)

            # Write Table to Directory
            #namuParser.WriteTableToFile(normalTableList, docItem[DOC_TITLE], WRITE_TABLE_DEST_PATH+'/normal', True)
            #namuParser.WriteTableToFile(infoBoxList, docItem[DOC_TITLE], WRITE_TABLE_DEST_PATH+'/infobox', False)

            scoreTable = headExtractor.GiveScoreToHeadCell(normalTableList)
            #### TEST ####
            if TEST_MODE and TEST_TAGET_TITLE == docItem[DOC_TITLE]:
                print(normalTableList)
                print(infoBoxList)
                print(scoreTable)

        #### TEST ####
        if TEST_MODE and TEST_TAGET_TITLE == docItem[DOC_TITLE]:
            print("NOT EXISTED TABLE")
            # print(docItem[DOC_TEXT])
            break