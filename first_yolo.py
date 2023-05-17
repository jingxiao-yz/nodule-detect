import colorsys
import os
import time
import numpy as np
import torch
import torch.nn as nn
from PIL import ImageDraw, ImageFont

from yolox_nets.yolo import YoloBody

from yolox_utils.utils import cvtColor, get_classes, preprocess_input, resize_image
from yolox_utils.utils_bbox import decode_outputs, non_max_suppression

import json
import random


# 添加自己脚本

from tools import replace_path

"""
训练自己的数据集必看注释！
"""

class YOLO(object):
    _defaults = {
        # --------------------------------------------------------------------------#
        #   使用自己训练好的模型进行预测一定要修改model_path和classes_path！
        #   model_path指向logs文件夹下的权值文件，classes_path指向model_data下的txt
        #
        #   训练好后logs文件夹下存在多个权值文件，选择验证集损失较低的即可。
        #   验证集损失较低不代表mAP较高，仅代表该权值在验证集上泛化性能较好。
        #   如果出现shape不匹配，同时要注意训练时的model_path和classes_path参数的修改
        # -------------------------------------------------------------------------#
        # "model_path": "/home/predict/logs/liangexing.pth",
        # "model_path": "/home/predict/logs/yilun510.pth",
        "model_path": r"/home/predict/logs/ep360-loss4.067-val_loss3.542.pth",
        "classes_path": r"/home/predict/model_data/voc_classes.txt",
        # ---------------------------------------------------------------------#
        #   输入图片的大小，必须为32的倍数。
        # ---------------------------------------------------------------------#
        "input_shape": [640, 640],
        # ---------------------------------------------------------------------#
        #   所使用的YoloX的版本。nano、tiny、s、m、l、x
        # ---------------------------------------------------------------------#
        "phi": "x",
        # ---------------------------------------------------------------------#
        #   只有得分大于置信度的预测框会被保留下来
        # ---------------------------------------------------------------------#
        "confidence": 0.5,    ##0.5
        # ---------------------------------------------------------------------#
        #   非极大抑制所用到的nms_iou大小
        # ---------------------------------------------------------------------#
        "nms_iou": 0.3,
        # ---------------------------------------------------------------------#
        #   该变量用于控制是否使用letterbox_image对输入图像进行不失真的resize，
        #   在多次测试后，发现关闭letterbox_image直接resize的效果更好
        # ---------------------------------------------------------------------#
        "letterbox_image": True,
        # -------------------------------#
        #   是否使用Cuda
        #   没有GPU可以设置成False
        # -------------------------------#
        # "cuda": False,
        "cuda": True,
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    # ---------------------------------------------------#
    #   初始化YOLO
    # ---------------------------------------------------#
    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        for name, value in kwargs.items():
            setattr(self, name, value)

        # ---------------------------------------------------#
        #   获得种类和先验框的数量
        # ---------------------------------------------------#
        self.class_names, self.num_classes = get_classes(self.classes_path)

        # ---------------------------------------------------#
        #   画框设置不同的颜色
        # ---------------------------------------------------#
        hsv_tuples = [(x / self.num_classes, 1.0, 1.0) for x in range(self.num_classes)]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(
                lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors,
            )
        )
        
        # if
        self.generate()

    # ---------------------------------------------------#
    #   生成模型
    # ---------------------------------------------------#

    def generate(self):
        self.net = YoloBody(
            self.num_classes, self.phi
        )  # 类别数量更改!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net.load_state_dict(torch.load(self.model_path, map_location=device))
        self.net = self.net.eval()
        print("{} model, and classes loaded.".format(self.model_path))

        if self.cuda:
            self.net = nn.DataParallel(self.net)
            self.net = self.net.cuda()

    # ---------------------------------------------------#

    #   检测图片
    # ---------------------------------------------------#
    def detect_image(self, image, image_name, image_path, information):
        # ---------------------------------------------------#
        #   获得输入图片的高和宽
        # ---------------------------------------------------#
        image_shape = np.array(np.shape(image)[0:2])
        # ---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        # ---------------------------------------------------------#
        image = cvtColor(image)
        # ---------------------------------------------------------#
        #   给图像增加灰条，实现不失真的resize
        #   也可以直接resize进行识别
        # ---------------------------------------------------------#
        image_data = resize_image(image, (self.input_shape[1], self.input_shape[0]), self.letterbox_image)
        # ---------------------------------------------------------#
        #   添加上batch_size维度
        # ---------------------------------------------------------#
        image_data = np.expand_dims(np.transpose(preprocess_input(np.array(image_data, dtype="float32")), (2, 0, 1)),0,)
        with torch.no_grad():
            images = torch.from_numpy(image_data)
            if self.cuda:
                images = images.cuda()
            # ---------------------------------------------------------#
            #   将图像输入网络当中进行预测！
            # ---------------------------------------------------------#
            outputs = self.net(images)
            outputs = decode_outputs(outputs, self.input_shape)
            # ---------------------------------------------------------#
            #   将预测框进行堆叠，然后进行非极大抑制
            # ---------------------------------------------------------#
            results = non_max_suppression(
                outputs,
                self.num_classes,
                self.input_shape,
                image_shape,
                self.letterbox_image,
                conf_thres=self.confidence,
                nms_thres=self.nms_iou,
            )
            print(results[0])
            if len(results[0]) == 0:
                return 0

            top_label = np.array(results[0][:, 6], dtype="int32")
            top_conf = results[0][:, 4] * results[0][:, 5]
            top_boxes = results[0][:, :4]
        # ---------------------------------------------------------#
        #   设置字体与边框厚度
        # ---------------------------------------------------------#
        font = ImageFont.truetype(
            font="/home/predict/model_data/simhei.ttf",size=np.floor(3e-2 * image.size[1] + 0.5).astype("int32"),)
        thickness = int(max((image.size[0] + image.size[1]) // np.mean(self.input_shape), 1))

        # 结节详细json信息
        node_information_dict = {  # 结节图片的序号、坐标、概率、良性还是恶性、纹理类别、体积类型、直径
            "imageId": "imageId",
            "file_name":"",
            "PatientName": "",
            "probability": "",
            "status": "",##一轮种类
            "textureCategory": "",##二轮种类
            "coordinates": "",
            "volumeCategory": "",
            "diameter": "",
            "1zuobiao":"",
            "2textureCategory_zuobiao":"",
            "2status_zuobiao":"",
        }
        node_information_dict["probability"]=[]
        node_information_dict["status"]=[]
        node_information_dict["textureCategory"]=[]
        node_information_dict["coordinates"]=[]
        node_information_dict["volumeCategory"]=[]
        node_information_dict["diameter"]=[]
        node_information_dict["1zuobiao"]=[]
        node_information_dict["2textureCategory_zuobiao"]=[]
        node_information_dict["2status_zuobiao"]=[]

        # ---------------------------------------------------------#
        #   图像绘制
        # ---------------------------------------------------------#
        for i, c in list(enumerate(top_label)):
            predicted_class = self.class_names[int(c)]
            box = top_boxes[i]
            score = top_conf[i]
            top, left, bottom, right = box
            top = max(0, np.floor(top).astype("int32"))
            left = max(0, np.floor(left).astype("int32"))
            bottom = min(image.size[1], np.floor(bottom).astype("int32"))
            right = min(image.size[0], np.floor(right).astype("int32"))
            diameter = ((((top - bottom)-5) ** 2 + ((right - left)-5) ** 2) ** 0.5
                        * 0.35* (int(information["ReconstructionDiameter"]) / 5120))
            Shangxia  = str((abs(bottom -top)-5)*0.5*(int(information["ReconstructionDiameter"]) / 5120))[0:4]
            Zuoyou = str((abs(right - left)-5)*0.5* (int(information["ReconstructionDiameter"]) / 5120))[0:4]
            diameter = str(diameter)[0:5]
            label = "{} {:.2f}".format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)
            label = label.encode("utf-8")
            x = (left + right) / 2
            y = (top + bottom) / 2
            # print(image_name, label, top, left, bottom, right)

            # 结节文本信息
            txt_data = (str(label)  + "," + str(top) + "," + str(left) + "," + str(bottom) + "," + str(right) + "," + "\n" )

            ##yolo画图
            # -----------------------------------------------------
            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])
            for i in range(thickness):
                self.colors = [(0, 255, 0), (255, 0, 0)]
                draw.rectangle([left-5 + i, top-5 + i, right+5 - i, bottom+5 - i], outline=self.colors[c])
            draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)],fill=self.colors[c],)
            draw.text(text_origin, str(label, "UTF-8"), fill=(0, 0, 0), font=font)
            del draw

            node_information_dict["1zuobiao"].append(txt_data)
            node_information_dict["imageId"] = image_name.split(".")[-2]
            node_information_dict["file_name"] = image_name
            node_information_dict["PatientName"] = str(information["PatientName"])
            # node_information_dict["status"].append(str(predicted_class))
            node_information_dict["probability"].append(str(score))
            node_information_dict["coordinates"].append( str((left + right) / 2) + "," + str((top + bottom) / 2) )
            node_information_dict["diameter"].append(str(diameter) + "cm"+",\n 横："+Zuoyou+"cm,\n 竖："+Shangxia+"cm")
            # node_information_dict["diameter"].append(str(diameter))
            # print(node_information_dict)

        new_path1, the_name1 = replace_path.replace(image_path, "0dicom2imgs", "jsonfile")
        node_information_json = new_path1 + the_name1.split(".")[-2] + ".json"
        with open(node_information_json, "w") as f:
            json.dump(node_information_dict, f, indent=4)

        return image

    def get_FPS(self, image, test_interval):
        image_shape = np.array(np.shape(image)[0:2])
        # ---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        # ---------------------------------------------------------#
        image = cvtColor(image)
        # ---------------------------------------------------------#
        #   给图像增加灰条，实现不失真的resize
        #   也可以直接resize进行识别
        # ---------------------------------------------------------#
        image_data = resize_image(
            image, (self.input_shape[1], self.input_shape[0]), self.letterbox_image
        )
        # ---------------------------------------------------------#
        #   添加上batch_size维度
        # ---------------------------------------------------------#
        image_data = np.expand_dims(
            np.transpose(
                preprocess_input(np.array(image_data, dtype="float32")), (2, 0, 1)
            ),
            0,
        )

        with torch.no_grad():
            images = torch.from_numpy(image_data)
            if self.cuda:
                images = images.cuda()
            # ---------------------------------------------------------#
            #   将图像输入网络当中进行预测！
            # ---------------------------------------------------------#
            outputs = self.net(images)
            outputs = decode_outputs(outputs, self.input_shape)
            # ---------------------------------------------------------#
            #   将预测框进行堆叠，然后进行非极大抑制
            # ---------------------------------------------------------#
            results = non_max_suppression(
                outputs,
                self.num_classes,
                self.input_shape,
                image_shape,
                self.letterbox_image,
                conf_thres=self.confidence,
                nms_thres=self.nms_iou,
            )

        t1 = time.time()
        for _ in range(test_interval):
            with torch.no_grad():
                # ---------------------------------------------------------#
                #   将图像输入网络当中进行预测！
                # ---------------------------------------------------------#
                outputs = self.net(images)
                outputs = decode_outputs(outputs, self.input_shape)
                # ---------------------------------------------------------#
                #   将预测框进行堆叠，然后进行非极大抑制
                # ---------------------------------------------------------#
                results = non_max_suppression(
                    outputs,
                    self.num_classes,
                    self.input_shape,
                    image_shape,
                    self.letterbox_image,
                    conf_thres=self.confidence,
                    nms_thres=self.nms_iou,
                )

        t2 = time.time()
        tact_time = (t2 - t1) / test_interval
        return tact_time

    def get_map_txt(self, image_id, image, class_names, map_out_path):
        f = open(
            os.path.join(map_out_path, "detection-results/" + image_id + ".txt"), "w"
        )
        image_shape = np.array(np.shape(image)[0:2])
        # ---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        # ---------------------------------------------------------#
        image = cvtColor(image)
        # ---------------------------------------------------------#
        #   给图像增加灰条，实现不失真的resize
        #   也可以直接resize进行识别
        # ---------------------------------------------------------#
        image_data = resize_image(
            image, (self.input_shape[1], self.input_shape[0]), self.letterbox_image
        )
        # ---------------------------------------------------------#
        #   添加上batch_size维度
        # ---------------------------------------------------------#
        image_data = np.expand_dims(
            np.transpose(
                preprocess_input(np.array(image_data, dtype="float32")), (2, 0, 1)
            ),
            0,
        )

        with torch.no_grad():
            images = torch.from_numpy(image_data)
            if self.cuda:
                images = images.cuda()
            # ---------------------------------------------------------#
            #   将图像输入网络当中进行预测！
            # ---------------------------------------------------------#
            outputs = self.net(images)
            outputs = decode_outputs(outputs, self.input_shape)
            # ---------------------------------------------------------#
            #   将预测框进行堆叠，然后进行非极大抑制
            # ---------------------------------------------------------#
            results = non_max_suppression(
                outputs,
                self.num_classes,
                self.input_shape,
                image_shape,
                self.letterbox_image,
                conf_thres=self.confidence,
                nms_thres=self.nms_iou,
            )

            if results[0] is None:
                return

            top_label = np.array(results[0][:, 6], dtype="int32")
            top_conf = results[0][:, 4] * results[0][:, 5]
            top_boxes = results[0][:, :4]

        for i, c in list(enumerate(top_label)):
            predicted_class = self.class_names[int(c)]
            box = top_boxes[i]
            score = str(top_conf[i])

            top, left, bottom, right = box
            if predicted_class not in class_names:
                continue

            f.write(
                "%s %s %s %s %s %s\n"
                % (
                    predicted_class,
                    score[:6],
                    str(int(left)),
                    str(int(top)),
                    str(int(right)),
                    str(int(bottom)),
                )
            )

        f.close()
        return
