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
            sheet_name="origin",
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
        response = requests.post(url, headers=self.header, data=multipart_encoder.to_string())

        # Download
        ret_url = ""
        try:
            res_json = json.loads(response.text)
            req_id = res_json["data"]["requestId"]
            with open(ids_path, mode="a", encoding="utf-8") as id_file:
                ret_url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/download?requestId="+req_id
        except Exception as e:
            print("ERR:", e)

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
                with open(target_path+"/"+str(count)+".xlsx", "wb") as wf:
                    wf.write(res.content)

    def CheckTranslateStatus(self, url):
        res = requests.get(url, headers=self.header)
        print(res.text)

if "__main__" == __name__:
    ### TEST CODE ####
    testTable = [['Season', 'Premier', 'Runner-up', 'Score', 'Margin', 'Venue', 'Attendance'], [1960, 'Melbourne', 'Collingwood', '8.14 (62) – 2.2 (14)', 48, 'MCG', 97457], [1964, 'Melbourne', 'Collingwood', '8.16 (64) – 8.12 (60)', 4, 'MCG', 102469], [1966, 'St Kilda', 'Collingwood', '10.14 (74) – 10.13 (73)', 1, 'MCG', 101655], [1970, 'Carlton', 'Collingwood', '17.9 (111) – 14.17 (101)', 10, 'MCG', 121696], [1977, 'North Melbourne', 'Collingwood', '10.16 (76) – 9.22 (76)', 0, 'MCG', 108244], [1977, 'North Melbourne', 'Collingwood', '21.25 (151) – 19.10 (124)', 27, 'MCG', 98366], [1979, 'Carlton', 'Collingwood', '11.16 (82) – 11.11 (77)', 5, 'MCG', 113545], [1980, 'Richmond', 'Collingwood', '23.21 (159) – 9.24 (78)', 81, 'MCG', 113461]]

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

        with open("./TranslatedTable/request_ids.txt", mode="wb") as wf:
            pickle.dump(req_url_list, wf)

    # Download
    download_strat = True
    if download_strat:
        tableTranslator.DownloadDocument(txt_path="./TranslatedTable/request_ids.txt",
                                         target_path="./TranslatedTable/target")