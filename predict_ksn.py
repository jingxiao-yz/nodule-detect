import glob
import json
import os
import shutil
import sys
import time
import cv2
import numpy as np
from PIL import Image

import first_yolo
import second_yolo
from unet import Unet

#### 添加工具脚本
from tools import (
    dic2img,
    replace_path,
    json2execl,
)
import image_operate
import make_result

unet = Unet()
firstyolo = first_yolo.YOLO()
secondyolo = second_yolo.YOLO()
# prename = 'YANGZHOUXIONGYIXINDENGLEI'

prename=[]
def dir_predict(dir_path,group_id):
    
    second_round_img_list = []
    #### 第1轮良恶性判断---------------------------------------------------------------
    print ("开始一轮检测")
    pname = ''
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = root + "/" + file
            id_num = file.split('.')[0]

            try:
            # #### dcm转图片
                img_path, img_name, information = dic2img.dcm2img(file_path)
                print('11111111111111111111',img_name)
                #### 创建姓名文本文件
                
                name_txt = '1'+'_'+ str(information['PatientName'])+'.txt'
                prename=str(information['PatientName'])
                name_txt_path = dir_path.replace("source/",name_txt)
                print('2222222222222222222',name_txt_path)
                if not os.path.exists(name_txt_path):
                    open(name_txt_path, "w+")
                image = Image.open(img_path)
                # print(img_path)cd
                r_image1 = firstyolo.detect_image(image, img_name, img_path, information)
                print(img_path)
                if r_image1 == 0:
                    print("一轮no object")
                    continue
                else:
                    print("添加一轮信息")
                    new_path1, the_name1 = replace_path.replace(img_path, "0dicom2imgs", "1yolox_predictsave/imgs")
                    yolo_save_path = new_path1 + the_name1
                    print(yolo_save_path)
                    r_image1.save(yolo_save_path)
                    ####添加到二轮
                    second_round_img_list.append(img_path)
            
            except:
                    continue
    print("结束一轮检测")
    
    #### 第2轮 ----------------------------------------------------------------------
    if len(second_round_img_list)==0:
        print("一轮无检出")
        ####删除过程文件
        shutil.rmtree(dir_path.replace("source", "processfiles"))
        print(group_id,"group已完成")
        return 4
    else:
        print("开始二轮检测")
        for i in range(len(second_round_img_list)):
            img_path = second_round_img_list[i]
            image = Image.open(img_path)
            r_image1 = secondyolo.detect_image(image, img_name, img_path)
            if r_image1 == 0:
                # print("二轮no object")
                continue
        print("结束二轮检测，等待...")
        #### 生成所需信息文件
        json_path = dir_path.replace("source", "processfiles/jsonfile")
        if len(os.listdir(json_path))!=0:
            RESULT_PATH = dir_path.replace("source", "result")
            imgpath = dir_path.replace("source", "processfiles/0dicom2imgs")
            make_result.make_result_main(json_path, RESULT_PATH, imgpath,prename)
            #### 保存json信息为excel表
            analysed_file_dir = dir_path.replace("source", "result")
            if os.path.exists(analysed_file_dir):
                excel_dir=r'/opt/excel/'
                if not os.path.exists(excel_dir):
                    os.makedirs(excel_dir)
                json2execl.toexcel(analysed_file_dir,excel_dir)
                print("已生成结果文件")
                ####删除过程文件
                shutil.rmtree(dir_path.replace("source", "processfiles"))
                print(group_id,"group已完成")
                return 3
            else:
                print('二轮有过程json，make_esult未生成结果json')
                ####删除过程文件
                shutil.rmtree(dir_path.replace("source", "processfiles"))
                print(group_id,"group已完成")
                ####视为无结节
                return 4
        else:
            print('二轮无检出')
            ####删除过程文件
            shutil.rmtree(dir_path.replace("source", "processfiles"))
            print(group_id,"group已完成")
            ####视为无结节
            return 4

