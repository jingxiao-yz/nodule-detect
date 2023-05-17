from tools import png2svg
from tools import outline, outline_back_mixed
import json
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from unet import Unet
from classification import Classification
classfication = Classification()


unet = Unet()


# 获取同一结节的全部信息
def get_one_node_name(data):
    #IOU计算#
    def IOU(o_left, o_right, o_upper, o_lower, left, right, upper, lower):
        Sleft = max(o_left, left)
        Sright = min(o_right, right)
        Supper = max(o_upper, upper)
        Slower = min(o_lower, lower)
        #确保两个框有重叠部分#
        if Sright < Sleft or Supper > Slower:
            IOUloss = 0
            # print('flase')
        else:
            S1 = (Sright - Sleft) * (Slower - Supper)
            S2 = (right - left) * (lower - upper)
            S3 = (o_right - o_left) * (o_lower - o_upper)
            IOUloss = S1 / (S2 + S3 - S1)
        return IOUloss

    # 肺结节列表，每一个元素为一组肺结节图片名（列表），该列表长度为独立肺结节个数
    NODES = []
    # 坐标框列表，每一个元素为对应NODES中肺结节最近的一张图片中肺结节的坐标，有多少独立肺结节，就应当有多少坐标框
    BOXS = []
    nodeflag = []
    # 同一结节的全部TXT信息
    TXT_FILE = []
    for i in range(len(data)):
        json_data = data[i]
        KEYS = list(json_data.keys())
        VALUES = list(json_data.values())
        pngname = VALUES[1]
        patientname = VALUES[2]
        probability = VALUES[3]
        diameter = VALUES[8]
        node_box = VALUES[9]
        node_BM_class = VALUES[11]

        box = []
        txt_name_list = []
        txt_name_list.append(pngname)
        nodeflag1 = []
        class_box = []

        # 将直径信息与种类信息存进列表中
        for node_num in range(len(node_box)):
            node_info = node_box[node_num] + \
                diameter[node_num] + str(',') + probability[node_num]
            node_box[node_num] = node_info

        # 根据符号对列表元素划分
        for node_num in range(len(node_box)):
            for node_box_num in range(len(node_box[node_num].split(','))):
                box.append(node_box[node_num].split(',')[node_box_num])
        for node_num1 in range(len(node_BM_class)):
            for node_BM_class_num in range(len(node_BM_class[node_num1].split(','))):
                class_box.append(node_BM_class[node_num1].split(',')[node_BM_class_num])

        # 根据IOU获取良恶性种类
        for box_num in range(int(int(len(box)) / 9)):
            left = int(box[2 + 9 * box_num])
            upper = int(box[1 + 9 * box_num])
            right = int(box[4 + 9 * box_num])
            lower = int(box[3 + 9 * box_num])
            for class_box_num in range(int(int(len(class_box)) / 6)):
                o_left = int(class_box[2 + 6 * class_box_num])
                o_upper = int(class_box[1 + 6 * class_box_num])
                o_right = int(class_box[4 + 6 * class_box_num])
                o_lower = int(class_box[3 + 6 * class_box_num])
                IOUloss = IOU(o_left, o_right, o_upper, o_lower,left, right, upper, lower)
                print('class_box_num',class_box_num,'IOUloss',IOUloss)
                if class_box_num == 0:
                    IOUloss_MAX = IOUloss   
                    if IOUloss > 0:
                        box[0 + 9 * box_num] = class_box[0 + 6 * class_box_num]
                else:
                    if IOUloss > IOUloss_MAX:
                        IOUloss_MAX = IOUloss
                        box[0 + 9 * box_num] = class_box[0 + 6 * class_box_num]
                
        # 生成初始信息列表
        if i == 0:
            # 获取初始独立肺结节数量，flag为独立肺结节数量
            flag = int(int(len(box)) / 9)
            # print(flag)
            for y in range(flag):
                nodeflag1.append(y)
            nodeflag.append(nodeflag1)
            for v in range(flag):
                TXT_INFOR = []
                KONG = []
                for num in range(9):
                    TXT_INFOR.append(box[num + v * 9])
                KONG.append(TXT_INFOR)
                TXT_FILE.append(KONG)

        # 对每一个结节进行判断
        for j in range(int(int(len(box)) / 9)):
            BBOX = []
            KONG = []
            TXT_INFOR = []
            updata = 0
            left = int(box[2 + 9 * j])
            upper = int(box[1 + 9 * j])
            right = int(box[4 + 9 * j])
            lower = int(box[3 + 9 * j])
            for box_num in range(9):
                TXT_INFOR.append(box[box_num + j * 9])
            KONG.append(TXT_INFOR)
            BBOX.append(left)
            BBOX.append(lower)
            BBOX.append(right)
            BBOX.append(upper)
            if i == 0:
                updata = 1
                # 建立初始独立肺结节名称列表
                txt_names = []
                txt_names.append(txt_name_list)
                NODES.append(txt_names)
                # 建立初始独立肺结节坐标框列表
                BOXS.append(BBOX)
            else:
                # 将最新读取的坐标与BOXS中保存的每一个坐标进行IOU计算，若大于0.7则为当前坐标的下一位置，若全不为0.7则为新结节
                for x in range(len(nodeflag[-1])):
                    k = nodeflag[-1][x]
                    o_left = BOXS[k][0]
                    o_right = BOXS[k][2]
                    o_lower = BOXS[k][1]
                    o_upper = BOXS[k][3]
                    IOUloss = IOU(o_left, o_right, o_upper,
                                  o_lower, left, right, upper, lower)
                    # 同一结节更新信息
                    if IOUloss >= 0.2:
                        # 更新坐标
                        updata = 1
                        BOXS[k][0] = left
                        BOXS[k][2] = right
                        BOXS[k][1] = lower
                        BOXS[k][3] = upper
                        # 保存当前更新结节的序号
                        nodeflag1.append(k)
                        # 在对应位置添加图片名
                        NODES[k].append(txt_name_list)
                        # 添加结节相关信息
                        TXT_FILE[k].append(TXT_INFOR)
            # 新结节
            if updata == 0:
                flag = flag + 1
                # 创建新的肺结节列表
                txt_names = []
                txt_names.append(txt_name_list)
                NODES.append(txt_names)
                # 对该新肺结节列表添加坐标
                BOXS.append(BBOX)
                TXT_FILE.append(KONG)
                # 保存结节序号
                nodeflag1.append(flag-1)
        nodeflag.append(nodeflag1)

    return NODES, TXT_FILE

# 获取良恶性种类

def get_BM_class(file):
    Benign = 0
    Malignant = 0
    Unkonwn = 0
    for i in range(len(file)):
        if file[i][0][2] == 'B':
            Benign += 1
        elif file[i][0][2] == 'M':
            Malignant +=1
        else:
            Unkonwn += 1

    if Benign != 0 or Malignant != 0:
        if Benign >= Malignant:
            node_bm_class = 'Benign'
        else:
            node_bm_class = 'Malignant'
    else:
        node_bm_class = 'Unkonwn'
    print('Unkonwn',Unkonwn)
    print('Benign',Benign)
    print('Malignant',Malignant)
    return node_bm_class

# def get_BM_class(file):
#     Benign = 0
#     Malignant = 0
#     for i in range(len(file)):
#         if file[i][0][2] == 'B':
#             Benign += 1
#         else:
#             Malignant += 1
#     if Benign >= Malignant:
#         node_bm_class = 'Benign'
#     else:
#         node_bm_class = 'Malignant'
#     return node_bm_class

# 获取结节置信度


def get_pro(file):
    pro = 0
    for i in range(len(file)):
        pro += float(file[i][8])
    pro = pro/len(file)
    return pro

# 获取结节最大尺寸


def get_node_max_diameter(file):
    tilt_size = []
    transverse_size = []
    vertical_size = []
    for i in range(len(file)):
        tilt_size.append(float(file[i][5][:-2]))
        transverse_size.append(float(file[i][6][4:-2]))
        vertical_size.append(float(file[i][7][4:-2]))
    tilt_max_size = max(tilt_size)
    transverse_max_size = max(transverse_size)
    vertical_max_size = max(vertical_size)
    size_info = str(tilt_max_size) + 'cm,' + '横：' + str(transverse_max_size) + \
        'cm,' + '竖：' + str(vertical_max_size) + 'cm,'
    return size_info

# 获取中心坐标


def get_coord(file):
    left = []
    upper = []
    lower = []
    right = []
    for j in range(int(len(file))):
        left.append(int(file[j][2]))
        upper.append(int(file[j][1]))
        right.append(int(file[j][4]))
        lower.append(int(file[j][3]))
    min_left = max(left)
    min_right = min(right)
    min_upper = max(upper)
    min_lower = min(lower)
    coord = str(float(min_right+min_left)/2)+';'+ str(float(min_upper+min_lower)/2)
    return coord

# 生成结果文件


def make_result(NODES, TXT_FILE, RESULT_PATH, imgpath,prename):
    new_node = []
    new_txt_file = []
    for i in range(len(NODES)):
        if len(NODES[i]) != 1:
            new_node.append(NODES[i])
            new_txt_file.append(TXT_FILE[i])
    NODES = new_node
    TXT_FILE = new_txt_file
    for i in range(len(NODES)):
        # print(NODES)
        imgname_list = []
        crop_img = []
        json_name_list = ["image_id","file_name", "coordinates","probability", "status", "texture_category", "diameter" ]

        # result_save_path = RESULT_PATH + str(i + 1) + '_' + NODES[0][0][0].split('.')[0].split('_')[1] + '/'
        result_save_path = RESULT_PATH + str(i + 1) + '_' + prename + '/'
        img_save_path = result_save_path + "layer/"
        if not os.path.exists(img_save_path):
            os.makedirs(img_save_path)
        # if not os.path.exists(os.path.join(result_save_path, 'json')):
        #     os.makedirs(os.path.join(result_save_path, 'json'))
        pro = get_pro(TXT_FILE[i])
        node_diameter = get_node_max_diameter(TXT_FILE[i])
        coord = get_coord(TXT_FILE[i])
        node_bm_class = get_BM_class(TXT_FILE[i])
        for j in range(len(NODES[i])):
            imgname = NODES[i][j][0]
            imgname_list.append(imgname)
            left = int(TXT_FILE[i][j][2])
            upper = int(TXT_FILE[i][j][1])
            right = int(TXT_FILE[i][j][4])
            lower = int(TXT_FILE[i][j][3])
            img = Image.open(imgpath + imgname).convert('RGB')
            cropped = img.crop((left, upper, right, lower))
            # 加一个unet预测
            unet_cropped = unet.detect_image(cropped)
            # unet预测贴图
            crop_line_img = outline.generate_outline(unet_cropped, cropped)
            img = outline_back_mixed.resize_getloc(
                img, crop_line_img, left, upper, right, lower)
            #------------------#
            crop_img.append(cropped)
            # 画框

            draw = ImageDraw.Draw(img)
            # 根据种类获取颜色
            if node_bm_class == 'Benign':
                color = 'green'
                label = 'Benign'
            elif node_bm_class == 'Malignant':
                color = 'red'
                label = 'Malignant'
            else:
                color = 'orange'
                label = 'Nodule'
            # 绘制框线
            blank = 0
            draw.rectangle([left - blank, upper - blank, right + blank, lower + blank], outline=color)
            # 绘制文本实心框
            draw.rectangle([left - 5, upper - 21, right + 40, upper - 6], fill=color)
            # 绘制良恶性种类文本
            draw.text([left - 5, upper - 21], label, fill='white')
            img.save(img_save_path + imgname)

        ####展示最后一张svg
        png2svg.tosvg(img_save_path, imgname_list[-1])

        # 获取磨玻璃实性种类
        s = 0
        g = 0
        for i in range(len(crop_img)):
            texture_class_name = classfication.detect_image(crop_img[0])
            if texture_class_name == 'Solid':
                s = s + 1
            else:
                g = g + 1
        if s != 0 and g != 0:
            texture_class_name = 'Mixed'
        elif s == 0:
            texture_class_name = 'Glass'
        else:
            texture_class_name = 'Solid'

        # 同一结节裁剪下的图片

        dictionary = dict.fromkeys(json_name_list)
        dictionary["image_id"] = imgname_list[-1].split('.')[0].split('_')[0]
        dictionary['file_name'] = imgname_list[-1]
        dictionary["probability"] = str(pro)
        dictionary['status'] = node_bm_class
        dictionary['diameter'] = node_diameter
        dictionary['coordinates'] = coord
        # 磨玻璃实性种类
        dictionary["texture_category"] = texture_class_name
        json_path = result_save_path
        open(json_path + 'analyse.json', 'w')
        with open(json_path + 'analyse.json', 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, indent=4, ensure_ascii=False)


def make_result_main(json_path, RESULT_PATH, imgpath,prename):
    # #yolo生成json路径
    # json_path = r"C:\Users\DL\Desktop\tryagain\TRY/"
    # # result存放路径
    # RESULT_PATH = r'C:\Users\DL\Desktop\tryagain\RESULT/'
    # # 原图存放路径
    # imgpath = r'C:\Users\DL\Desktop\tryagain\PNG/'

    jsonnames = os.listdir(json_path)
    nums = []
    jsondata = []
    for i in range(len(jsonnames)):
        if jsonnames[i].endswith(".json"):
            num = int(jsonnames[i].split('_')[0])
            # jsonname = jsonnames[i].split('_')[1]
            jsonname = prename+'.json'
            nums.append(num)
    nums = sorted(nums)
    for i in range(len(nums)):
        json_name = str(nums[i]) + '_' + jsonname
        path = os.path.join(json_path, json_name)
        with open(path, 'r', encoding='UTF-8') as f:
            data = json.load(f)
            jsondata.append(data)
    NODES, TXT_FILE = get_one_node_name(jsondata)

    make_result(NODES, TXT_FILE, RESULT_PATH, imgpath,jsonname)

