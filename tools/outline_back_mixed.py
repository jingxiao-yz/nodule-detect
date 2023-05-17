from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import skimage




# img_path = r'.\SOURCEandIFOMATION_FILE\2img_send_to_unet\img2unet_1/'  # 已筛选过的原始CT图片
# predict_path = r'.\SOURCEandIFOMATION_FILE\4outline_imgs\samll_mixed_imgs/'  # 带边框预测小图片
# txt_path = r'.\SOURCEandIFOMATION_FILE\1yolox_predictsave\txts/'  # yolo边框预测文档
# final_mixed_path = r'.\SOURCEandIFOMATION_FILE\4outline_imgs\big_mixed_imgs/'  # 贴回图片路径


# img_list = os.listdir(img_path)
# img_list.sort()
# predict_list = os.listdir(predict_path)
# predict_list.sort()
# txt_list = os.listdir(txt_path)
# txt_list.sort()
# path_len = len(os.listdir(img_path))


# 获取肺结节坐标，将图片回复原尺寸，并贴回原来位置
def resize_getloc(img1,crop_img,left, upper, right, lower):
    W = abs(right - left)
    H = abs(upper - lower)
    X = left
    Y = upper
    crop_img = crop_img.resize((W, H), Image.ANTIALIAS)  # 修改尺寸
    img1.paste(crop_img, (X, Y), mask=None)  # 贴回原位
    return img1

    # return imgame, txtname

