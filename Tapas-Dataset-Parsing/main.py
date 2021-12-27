import os
import sys

from Utils.TranslateTable import TableTranslator
from Preprocessing.Definition import PreprocDef
from Preprocessing import GenerateWikiSQL

import pickle

if "__main__" == __name__:
    # Load 2D tables to dict
    gen_wikiSQL = GenerateWikiSQL.WikiSqlGenerator()

    dataset_path = "./Preprocessing/Dataset/WikiSQL/data"
    train_jsonl = dataset_path + "/train.jsonl"
    table_jsonl = dataset_path + "/train.tables.jsonl"

    gen_wikiSQL.SetTableFilePath(table_jsonl)
    table_dict = gen_wikiSQL.ConvertTableData()

    # Check Total Request Size
    CHECK_TOTAL_CHAR = True
    if CHECK_TOTAL_CHAR:
        total_len = 0
        for key, val in table_dict.items():
            curr_join_str = ""
            for row in val:
                row = str(row)
                curr_join_str = "".join(row)
            total_len += len(curr_join_str)
        print("ToTal Table Len:", total_len)

    print(table_dict["1-10006830-1"])

    ### Make Requst ID Process
    MAKE_REQ_ID_PROC = False
    if MAKE_REQ_ID_PROC:
        # Init
        LIMIT_BYTES = 10000
        api_header = {
            "id": "ph7wz3gf0z",  # User_Client_ID
            "key": "VelHVcmwXQh8Eah81iuuc3cm1Iyec2hJDISp4Vgy",  # User_Client_Key(Secret)
        }
        tableTranslator = TableTranslator(client_id=api_header["id"], client_key=api_header["key"])

        # already made origin files
        already_made_origin_files = os.listdir("./Utils/TranslatedTable/origin")

        # Translate Table
        table_ids_file_path = "./Utils/TranslatedTable/table_ids_wikiSQL"
        with open(table_ids_file_path, "r", encoding="utf-8") as table_ids_file:
            table_ids_lines = table_ids_file.readlines()
            print("Total tables:", len(table_ids_lines))

            table_ids_count = 0
            curr_byte_size = 0
            req_url_list = []
            for table_ids in table_ids_lines:
                table_ids = str(table_ids.strip())

                # Check Made File
                for already_made_file in already_made_origin_files:
                    if table_ids in already_made_file:
                        continue

                # check byte len
                curr_table = table_dict[table_ids]
                table_join_str = ""
                for row in curr_table:
                    table_join_str += "".join(str(row))

                # STOP POINT
                curr_byte_size = len(table_join_str.encode("utf-8"))
                if curr_byte_size >= LIMIT_BYTES:
                    print("BREAK :", curr_byte_size, ">=", LIMIT_BYTES)
                    print("STOP Point: ", table_ids, "Processed Table Count:", table_ids_count)
                    break

                table_ids_count += 1
                if 0 == (table_ids_count % 500):
                    print("Processing", table_ids_count, "id:", table_ids)

                # Make request ids
                origin_table_path = "./Utils/TranslatedTable/origin"
                request_ids_path = "./Utils/TranslatedTable/request_ids.txt"

                req_url = tableTranslator.TranslateTable(src_table=curr_table,
                                                         save_path=origin_table_path,
                                                         file_name=table_ids,
                                                         ids_path=request_ids_path)
                if 0 < len(req_url):
                    req_url_list.append(req_url)
                else:
                    print("ERR - Make Req URL:", table_ids)

            # Make Request ID file
            with open(request_ids_path, mode="wb") as req_wf:
                pickle.dump(req_url_list, req_wf)

    ### Download Process
    DOWNLOAD_PROC = False
    if DOWNLOAD_PROC:
        request_ids_path = "./Utils/TranslatedTable/request_ids.txt"
        tableTranslator.DownloadDocument(txt_path=request_ids_path,
                                         target_path="./Utils/TranslatedTable/target")