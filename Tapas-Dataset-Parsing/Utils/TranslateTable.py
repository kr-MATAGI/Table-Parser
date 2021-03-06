import os
import pickle
import time

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
    def MakeRequestIDs(self, src_table, save_path, file_name):
        if not os.path.exists(save_path):
            print("Not existed directory - ", save_path)
            os.mkdir(save_path)
            print("Made directory - ", save_path)

        # Config *.xlsx file path
        file_name = file_name.replace("-", "_")
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

    def DownloadDocument(self, txt_path, target_path, except_list):
        count = 0

        already_download_list = os.listdir(target_path)

        with open(txt_path, mode="rb") as tf:
            readList = pickle.load(tf)
            for line in readList:
                count += 1
                url = line.strip()
                if 0 >= len(url):
                    break

                file_name = str(line.split("=")[-1])
                download_path = target_path+"/"+file_name+".xlsx"

                if download_path in except_list:
                    print("PASS: ", download_path)
                    continue

                is_pass = False
                for already_download in already_download_list:
                    if download_path in already_download:
                        is_pass = True
                        break
                if is_pass:
                    continue

                print(count, "Download URL:", url)
                res = requests.get(url, headers=self.header)
                with open(download_path, "wb") as wf:
                    wf.write(res.content)

    def RequsetTranslate(self, xlsx_path):
        req_url_list = []
        err_status_list = []

        request_count = 0
        xlsx_list = os.listdir(xlsx_path)
        for xlsx_file in xlsx_list:
            full_xlsx_path = xlsx_path + "/" + xlsx_file
            request_data = {
                'source': 'en',
                'target': 'ko',
                'file': (full_xlsx_path, open(full_xlsx_path, mode='rb'),
                         'application/octet-stream',
                         {'Content-Transfer-Encoding': 'binary'})
            }

            multipart_encoder = MultipartEncoder(request_data, boundary=uuid.uuid4())
            self.header["Content-Type"] = multipart_encoder.content_type
            url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/translate"

            try:
                request_count += 1
                print("Request Count:", request_count)

                response = requests.post(url, headers=self.header, data=multipart_encoder.to_string())
                res_status = response.status_code
                if res_status == 200:
                    res_json = json.loads(response.text)
                    req_id = str(res_json["data"]["requestId"])
                    req_url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/download?requestId=" + req_id
                    print("Req URL:", req_url)
                    req_url_list.append(req_url)

                    # Check Status
                    status_url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/status?requestId=" + req_id
                    while True:
                        time.sleep(1)
                        status_json = requests.get(status_url, headers=self.header).json()
                        print(status_json)
                        status_res = str(status_json["data"]["status"]).lower()
                        print(status_res, status_url)
                        if ("complete" == status_res) or ("failed" == status_res):
                            break
                else:
                    print('ERROR - Response Status', res_status)
                    err_status_list.append(xlsx_file)

            except Exception as e:
                print(full_xlsx_path)
                print("Translate ERR:", e)

        return req_url_list, err_status_list

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
    testTable = [['Aircraft', 'Description', 'Max Gross Weight', 'Total disk area', 'Max disk Loading'],
                 ['Robinson R-22', 'Light utility helicopter', '1,370 lb (635 kg)', '497 ft?? (46.2 m??)', '2.6 lb/ft?? (14 kg/m??)'],
                 ['Bell 206B3 JetRanger', 'Turboshaft utility helicopter', '3,200 lb (1,451 kg)', '872 ft?? (81.1 m??)', '3.7 lb/ft?? (18 kg/m??)'],
                 ['CH-47D Chinook', 'Tandem rotor helicopter', '50,000 lb (22,680 kg)', '5,655 ft?? (526 m??)', '8.8 lb/ft?? (43 kg/m??)'],
                 ['Mil Mi-26', 'Heavy-lift helicopter', '123,500 lb (56,000 kg)', '8,495 ft?? (789 m??)', '14.5 lb/ft?? (71 kg/m??)'],
                 ['CH-53E Super Stallion', 'Heavy-lift helicopter', '73,500 lb (33,300 kg)', '4,900 ft?? (460 m??)', '15 lb/ft?? (72 kg/m??)']]

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
        req_url = tableTranslator.MakeRequestIDs(src_table=testTable, save_path=save_path, file_name=file_name,
                                                 ids_path="./TranslatedTable/request_ids.txt")
        if 0 < len(req_url):
            req_url_list.append(req_url)

        with open("./TranslatedTable/request_ids.txt", mode="wb") as wf:
            pickle.dump(req_url_list, wf)

    # Download
    download_start = True
    if download_start:
        tableTranslator.DownloadDocument(txt_path="./TranslatedTable/request_ids.txt",
                                         target_path="./TranslatedTable/target")

    # Read
    xlsx_read_start = False
    if xlsx_read_start:
        table_list = tableTranslator.ReadTableXlsxFiles(src_path="./TranslatedTable/target")