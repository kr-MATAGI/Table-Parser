import os
import pickle

import requests

import uuid
import pandas as pd
import json
from requests_toolbelt import MultipartEncoder

class TableTranslator:
    ## PRIVATE ##
    def __init__(self, client_id, client_key):
        self.client_id = client_id
        self.client_key = client_key

        self.header = {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_key
        }

        print(f"Init Table Translator - client [id: {self.client_id}, key: {self.client_key}]")

    ## PUBLIC ##
    def TranslateTable(self, src_table, save_path, file_name, ids_path):
        if not os.path.exists(save_path):
            print("Not existed directory - ", save_path)
            os.mkdir(save_path)
            print("Made directory - ", save_path)

        # Config *.xlsx file path
        src_table_excel_path = save_path + "/" + file_name + "_origin.xlsx"
        print("src_excel:", src_table_excel_path)

        # Save src_table to file
        pd_df = pd.DataFrame(src_table, columns=None, index=None)
        pd_df.to_excel(
            src_table_excel_path,
            sheet_name="1",
            header=False,
            columns=None,
            index=False,
            encoding="utf-8"
        )

        # Request
        request_data = {
            'source': 'en',
            'target': 'ko',
            'file': (src_table_excel_path, open(src_table_excel_path, mode='rb'),
                     'application/octet-stream',
                     {'Content-Transfer-Encoding': 'binary'}
                    )
        }

        multipart_encoder = MultipartEncoder(request_data, boundary=uuid.uuid4())
        self.header["Content-Type"] = multipart_encoder.content_type
        url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/translate"

        # Download
        ret_url = ""
        try:
            response = requests.post(url, headers=self.header, data=multipart_encoder.to_string()).json()
            req_id = str(response["data"]["requestId"])
            ret_url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/download?requestId="+req_id
        except Exception as e:
            print(file_name)
            print("Translate ERR:", e)
            exit()


        return ret_url

    def DownloadDocument(self, txt_path, target_path):
        count = 0
        with open(txt_path, mode="rb") as tf:
            readList = pickle.load(tf)
            for line in readList:
                count += 1
                url = line.strip()
                if 0 >= len(url):
                    break

                print("Download URL:", url)

                res = requests.get(url, headers=self.header)
                file_name = str(line.split("=")[-1])
                with open(target_path+"/"+file_name+".xlsx", "wb") as wf:
                    wf.write(res.content)

    def CheckTranslateStatus(self, url):
        res = requests.get(url, headers=self.header)
        print(res.text)

    def ReadTableXlsxFiles(self, src_path):
        ret_table_list = []

        xlsx_files = os.listdir(src_path)
        print("xlsx file size:", len(xlsx_files))

        for xlsx_file in xlsx_files:
            table_xlsx = pd.read_excel(src_path+"/"+xlsx_file)
            ret_table_list.append(table_xlsx.values.tolist())

        return ret_table_list

if "__main__" == __name__:
    ### TEST CODE ####
    testTable = [['Aircraft', 'Description', 'Max Gross Weight', 'Total disk area', 'Max disk Loading']]

    # Header Info
    header = {
        "id": "ph7wz3gf0z",  # User_Client_ID
        "key": "VelHVcmwXQh8Eah81iuuc3cm1Iyec2hJDISp4Vgy",  # User_Client_Key(Secret)
    }
    tableTranslator = TableTranslator(client_id=header["id"], client_key=header["key"])

    # Translate
    translate_start = False
    if translate_start:
        save_path = "./TranslatedTable/origin"
        file_name = "test"

        req_url_list = []
        req_url = tableTranslator.TranslateTable(src_table=testTable, save_path=save_path, file_name=file_name,
                                                 ids_path="./TranslatedTable/request_ids.txt")
        if 0 < len(req_url):
            req_url_list.append(req_url)
            req_url_list.append(req_url)

        with open("./TranslatedTable/request_ids.txt", mode="wb") as wf:
            pickle.dump(req_url_list, wf)

    # Download
    download_strat = True
    if download_strat:
        tableTranslator.DownloadDocument(txt_path="./TranslatedTable/request_ids.txt",
                                         target_path="./TranslatedTable/target")

    # Read
    xlsx_read_start = True
    if xlsx_read_start:
        table_list = tableTranslator.ReadTableXlsxFiles(src_path="./TranslatedTable/target")