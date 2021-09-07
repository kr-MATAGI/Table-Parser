from NamuParser import DOC_TEXT, DOC_TITLE, NamuWikiParser
from HeadExtractor import Extractor

# Definition
SRC_JSON_PATH = './dataset/docData200302.json'

if __name__ == '__main__':
    # Make instance    
    namuParser = NamuWikiParser(SRC_JSON_PATH)
    headExtractor = Extractor()

    docCount = 0
    for docItem in namuParser.ParsingJSON():
        docCount += 1

        if 0 == docCount % 1000:
            print('Processing....', docCount)

        if 257000 >= docCount: continue  # For Test '한국전력공사'

        # if '백 평짜리 숲(킹덤 하츠)'== docItem[DOC_TITLE]:
        if '한국전력공사' == docItem[DOC_TITLE]:
            tableList = namuParser.ParseTableFromText(docItem[DOC_TEXT])
            
            if 0 < len(tableList):
                newTableList = []
                namuParser.ModifyHTMLTags(tableList)
                
                for table in tableList:
                    colSplitTable = namuParser.SplitColSpan(table)
                    rowSplitTable = namuParser.SplitRowSpan(colSplitTable)
                    organizedTable = namuParser.RemoveEmptyCells(rowSplitTable)
                    sliceLenTable = namuParser.SliceTableLength(organizedTable)

                    if 2 <= len(sliceLenTable):
                        newTableList.append(sliceLenTable)
                normalTableList, infoBoxList = namuParser.ClassifyNormalTableOrInfoBox(newTableList)
                print(infoBoxList)

                # Finish Parse and Regex Expression Process
                tableList = normalTableList
                tableList.extend(infoBoxList)

                # Extract Table Head and Make Tensor
                #scoreTable = headExtractor.GiveScoreToHeadCell(newTableList)

                break # TEST STOP
