import pydicom
import shutil
# import matplotlib.pyplot as plt
# import scipy.misc
# import pandas as pd
import numpy as np
# import os
# import glob
# import cv2
from PIL import Image
# import pathlib

from tools import replace_path


def set_windows(img, dcm):
    # img = dcm.pixel_array * dcm.RescaleSlope + dcm.RescaleIntercept
    center = -400
    width = 1400
    a = (2 * center - width) / 2 + 0.5  # -1099.5
    b = (2 * center + width) / 2 + 0.5  # 300.5
    dfactor = 255.0 / (b - a)  #255/1400
    h, w = np.shape(img)
    for i in range(h):
        for j in range(w):
            img[i, j] = int((img[i, j] - a) * dfactor)
    min_index = img < 0
    img[min_index] = 0
    max_index = img > 255
    img[max_index] = 255
    return img

# 加载Dicom图片中的Tag信息
def loadFileInformation(ds):
    information = {}
    
    # information['PatientID'] = ds.PatientID
    information['PatientName'] = ds.PatientName
    information['ReconstructionDiameter'] = ds.ReconstructionDiameter
    
    # print(dir(ds))
    # print(type(information))
    return information

def dcm2img(dicom_actual_path):
    img_type = ".jpg"  # 转换图片类型
    #if dicom_actual_path.lower().endswith((".dcm",".DCM")):
    # print(dicom_actual_path)
    try:
        dcm = pydicom.dcmread(dicom_actual_path, force=True)  # 加载dicom数据
        ds = pydicom.read_file(dicom_actual_path, force=True)

        #except无下面的这一行
        dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        # print(dcm)
        # name 
        # print(ds.RescaleSlope , ds.RescaleIntercept)
        data_img = np.array(dcm.pixel_array)
        # print()
        img = data_img * ds.RescaleSlope + ds.RescaleIntercept
        dcm_img = set_windows(img, dcm)
        # print(dcm)
        dcm_img = Image.fromarray(dcm_img)  # 将Numpy转换为PIL.Image
        dcm_img = dcm_img.convert("L")

        new_path, the_name = replace_path.replace(
            dicom_actual_path, "source", "processfiles/0dicom2imgs"
        )

        # img_name = the_name.split(".")[0] + img_type
        img_name = the_name.split(".")[0] +'_'+str(ds.PatientName)+ img_type
        # print(img_name)

        img_save_path = new_path + img_name

        dcm_img.save(img_save_path)
        imformation = loadFileInformation(ds)
        return img_save_path, img_name,imformation
        
    except(ValueError):
        dcm = pydicom.dcmread(dicom_actual_path, force=True)  # 加载dicom数据
        ds = pydicom.read_file(dicom_actual_path, force=True)
        
        # dcm.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        # print(dcm)
        # name 
        # print(ds.RescaleSlope , ds.RescaleIntercept)
        data_img = np.array(dcm.pixel_array)
        # print()
        img = data_img * ds.RescaleSlope + ds.RescaleIntercept
        dcm_img = set_windows(img, dcm)
        # print(dcm)
        dcm_img = Image.fromarray(dcm_img)  # 将Numpy转换为PIL.Image
        dcm_img = dcm_img.convert("L")

        new_path, the_name = replace_path.replace(
            dicom_actual_path, "source", "processfiles/0dicom2imgs"
        )

        # img_name = the_name.split(".")[0] + img_type
        img_name = the_name.split(".")[0] +'_'+str(ds.PatientName) + img_type
        # print(img_name)

        img_save_path = new_path + img_name

    dcm_img.save(img_save_path)
    imformation = loadFileInformation(ds)
    return img_save_path, img_name,imformation


