import os
import json
import pandas as pd


def toexcel(analysed_file_dir,excel_dir):

    content_list = []  #声明列表，存储从json文件中读取的字典
    PatientName=''
    nodule_num=0
    for root, dirs, files in os.walk(analysed_file_dir):
        print(files)
        for file in files:
            if file.endswith(".json"):
                nodule_num+=1
                json_path = root + '/' + file
                with open(json_path,encoding='utf8') as f:
                    old_data = json.load(f)
                    content = {  # 结节图片的序号、坐标、概率、良性还是恶性、纹理类别、体积类型、直径
                        "nuduleID": str(nodule_num),
                        "PatientName":old_data["file_name"].split('.')[0].split('_')[1],
                        "probability": old_data["probability"],  ##概率
                        "status": old_data["status"],##好坏
                        "texture_category": old_data["texture_category"],  ##纹理类别
                        "coordinates": old_data["coordinates"],  ##坐标
                        "diameter": old_data["diameter"],  ##直径
                    }
                    PatientName = content["PatientName"]
                    # print('内',PatientName)
                    content_list.append(content)
    # print('外',PatientName)
    df = pd.DataFrame(content_list)
    print('excellllllllllllllllllllll',excel_dir + PatientName)
    df.to_excel(excel_dir + PatientName + '.xlsx',encoding='utf8')
