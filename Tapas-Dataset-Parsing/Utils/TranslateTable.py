import os
import requests
import urllib.request
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

    def _DownloadDocument(self, request_id, download_path):
        url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/download?requestId=" + request_id
        print("Download URL:", url)

        res = requests.get(url, headers=self.header)

    ## PUBLIC ##
    def TranslateTable(self, src_table, save_path, file_name):
        if not os.path.exists(save_path):
            print("Not existed directory - ", save_path)
            os.mkdir(save_path)
            print("Made directory - ", save_path)

        # Config *.xlsx file path
        src_table_excel_path = save_path + "/" + file_name + "_origin.xlsx"
        target_table_excel_path = save_path + "/" + file_name + "_target.xlsx"

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
            'file': ( src_table_excel_path, open(src_table_excel_path, mode='rb'),
                     'application/octet-stream',
                     {'Content-Transfer-Encoding': 'binary'}
                    )
        }

        multipart_encoder= MultipartEncoder(request_data, boundary=uuid.uuid4())
        self.header["Content-Type"] = multipart_encoder.content_type

        url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/translate"
        response = requests.post(url, headers=self.header, data=multipart_encoder.to_string())

        # Download
        try:
            res_json = json.loads(response.text)
            req_id = res_json["data"]["requestId"]
            self._DownloadDocument(request_id=req_id, download_path=target_table_excel_path)
        except Exception as e:
            print("ERR:", e)

    def WordTest(self, src):
        url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/translate"
        request_data = {
            'source': 'en',
            'target': 'ko',
            'file': (src, open(src, 'rb'),
                     'application/octet-stream',
                     {'Content-Transfer-Encoding': 'binary'}
                     )
        }

        multipart_encoder = MultipartEncoder(request_data, boundary=uuid.uuid4())
        self.header["Content-Type"] = multipart_encoder.content_type
        response = requests.post(url, headers=self.header, data=multipart_encoder.to_string())

        res_json = json.loads(response.text)
        req_id = res_json["data"]["requestId"]
        self._DownloadDocument(request_id=req_id, download_path="./TranslatedTable/")

if "__main__" == __name__:
    ### TEST CODE ####

    testTable = [['Season', 'Premier', 'Runner-up', 'Score', 'Margin', 'Venue', 'Attendance'], [1960, 'Melbourne', 'Collingwood', '8.14 (62) – 2.2 (14)', 48, 'MCG', 97457], [1964, 'Melbourne', 'Collingwood', '8.16 (64) – 8.12 (60)', 4, 'MCG', 102469], [1966, 'St Kilda', 'Collingwood', '10.14 (74) – 10.13 (73)', 1, 'MCG', 101655], [1970, 'Carlton', 'Collingwood', '17.9 (111) – 14.17 (101)', 10, 'MCG', 121696], [1977, 'North Melbourne', 'Collingwood', '10.16 (76) – 9.22 (76)', 0, 'MCG', 108244], [1977, 'North Melbourne', 'Collingwood', '21.25 (151) – 19.10 (124)', 27, 'MCG', 98366], [1979, 'Carlton', 'Collingwood', '11.16 (82) – 11.11 (77)', 5, 'MCG', 113545], [1980, 'Richmond', 'Collingwood', '23.21 (159) – 9.24 (78)', 81, 'MCG', 113461]]

    # Header Info
    header = {
        "id": "ph7wz3gf0z",  # User_Client_ID
        "key": "KVieTYveceVofD7XrZn2tCRWX4ZLKJuWEorKPnax",  # User_Client_Key(Secret)
    }
    tableTranslator = TableTranslator(client_id=header["id"], client_key=header["key"])


    # Translate
    save_path = "./TranslatedTable"
    file_name= "test"
    tableTranslator.TranslateTable(src_table=testTable, save_path=save_path, file_name=file_name)