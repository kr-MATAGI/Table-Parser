### module
from namu_parser import NamuWikiParser
from namu_def import TABLE_REL
from utils import find_table_content, remove_namu_syntax

### Global
SRC_NAMU_JSON_PATH = "./data/namuwiki_20210301.json"
TEST_TARGET = "오버워치" # defulat: NONE (테스트 X)
IS_WRITE_FILE = True

### MAIN ###
if "__main__" == __name__:
    docCnt = 0

    if IS_WRITE_FILE:
        write_file = open("./output.txt", mode="w", encoding="utf-8")

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

                if 0 >= len(table_rel_info.sent_list):
                    continue
                table_rel_info_list.append(table_rel_info)
                if table_rel_info.doc_title == TEST_TARGET:
                    print(f"title: {table_rel_info.doc_title}")
                    print(f"parag_idx: {table_rel_info.parag_idx}")
                    print(f"table:")
                    for table_r in table_rel_info.table:
                        print(table_r)
                    print("sent: \n", table_rel_info.sent_list, "\n")

                if IS_WRITE_FILE:
                    write_file.write("title: " + table_rel_info.doc_title + "\n")
                    write_file.write("parag_idx: " + str(table_rel_info.parag_idx) + "\n")
                    write_file.write("table: \n")
                    for table_r in table_rel_info.table:
                        for table_c in table_r:
                            write_file.write(table_c + "\t")
                        write_file.write("\n")
                    write_file.write("sent: \n")
                    for write_sent in table_rel_info.sent_list:
                        write_file.write(write_sent + "\n")
                    write_file.write("\n\n")

    write_file.close()