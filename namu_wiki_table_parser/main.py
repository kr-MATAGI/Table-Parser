### module
from namu_parser import NamuWikiParser
from namu_def import TABLE_REL
from utils import find_table_content, remove_namu_syntax

### Global
SRC_NAMU_JSON_PATH = "./data/namuwiki_20210301.json"

### MAIN ###
if "__main__" == __name__:
    docCnt = 0

    namu_parser = NamuWikiParser(SRC_NAMU_JSON_PATH)
    for document in namu_parser.ParsingJSON():
        docCnt += 1

        if 0 == (docCnt % 1000):
            print('Processing...', document["title"], docCnt)

        # Make paragraph list - [paragraph index, table list, text list]
        splitParagraphList = namu_parser.ParseTableAndDetailsFromDocument(document["title"],
                                                                         document["text"])

        table_rel_info_list = []
        for paragraph in splitParagraphList:
            if 0 >= len(paragraph[1]):
                continue

            for table in paragraph[1]: # paragraph[1] is table list in doc's paragraph
                conv_table = namu_parser.ModifyHTMLTags(table)
                conv_table = namu_parser.PreprocessingTable(conv_table)
                if 1 >= len(conv_table):
                    continue

                table_rel_info = TABLE_REL(doc_title=document["title"],
                                           parag_idx=paragraph[0],
                                           table=conv_table)

                # 단락별 언급되는 문장은 테이블별로 중복 허용.
                origin_sent_list = remove_namu_syntax(paragraph[-1])
                table_rel_info.sent_list = find_table_content(conv_table, origin_sent_list)