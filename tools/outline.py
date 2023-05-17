from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import skimage
from  PIL import Image
# from numpy import dtype

from tools import replace_path


def generate_outline(unet_output,cropped):
    # print('xdcfyvguhijo',unet_output,cropped)
    unet_output=unet_output.convert("L")
    cropped=cropped.convert("L")

    # img = cv2.imdecode(np.array(unet_output,dtype==np.uint8).cv2.IMREAD_GRAYSCALE)
    # img1 = cv2.imdecode(np.array(cropped,dtype ==np.uint8).cv2.IMREAD_GRAYSCALE)

    img = np.array(unet_output,dtype=np.uint8)
    img1 = np.array(cropped,dtype=np.uint8)
    mean = np.mean(img)
    # print(mean)
    edges = cv2.Canny(img, 10, mean + 10, True)
    mean = np.mean(edges)


    ret, img = cv2.threshold(edges, mean, 255, cv2.THRESH_BINARY)
    img3 = cv2.add(img, img1)
    img3 = Image.fromarray(img3)

    img3=img3.convert("RGB")
    return img3
    # print(small_mixed_imgs_path_list)
    # return small_mixed_imgs_path_list

# generate_outline()
