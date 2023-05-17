import os
import cv2

def get_one_node_name(txt_path):
    #IOU计算#
    def IOU(o_left, o_right, o_upper, o_lower, left, right, upper, lower):
        Sleft = max(o_left, left)
        Sright = min(o_right, right)
        Supper = max(o_upper, upper)
        Slower = min(o_lower, lower)
        #确保两个框有重叠部分#
        if Sright<Sleft or Supper>Slower:
            IOUloss = 0
            # print('flase')
        else:
            S1 = (Sright - Sleft) * (Slower - Supper)
            S2 = (right - left) * (lower - upper)
            IOUloss = S1 / S2
        return IOUloss


    txt_path = txt_path
    # r'C:\Users\DL\Desktop\CROP7.12\LQTXT\LQ/'
    txtname = os.listdir(txt_path)
    txtname = sorted(txtname)


    #肺结节列表，每一个元素为一组肺结节图片名（列表），该列表长度为独立肺结节个数
    NODES = []
    #坐标框列表，每一个元素为对应NODES中肺结节最近的一张图片中肺结节的坐标，有多少独立肺结节，就应当有多少坐标框
    BOXS = []
    nodeflag = []
    for i in range(len(txtname)):
        box = []
        txt_name = txtname[i]
        # print(txt_name)
        txt_name_list = []
        txt_name_list.append(txt_name)
        with open(txt_path + txt_name, 'r') as file_to_read:
            while True:
                lines = file_to_read.readline()
                if not lines:
                    break
                else:
                    this_lines = lines.split(",")
                    for this_line in this_lines:
                        box.append(str(this_line))
                    nodeflag1 = []
                    # print(box)
                    if i == 0:
                        #获取初始独立肺结节数量，flag为独立肺结节数量
                        flag = int(int(len(box))/6)
                        for y in range(flag):
                            nodeflag1.append(y)
                        nodeflag.append(nodeflag1)
                        # print(nodeflag)
                    for j in range(int(int(len(box))/6)):
                        BBOX = []
                        left = int(box[2 + 6*j])
                        upper = int(box[1 + 6*j])
                        right = int(box[4 + 6*j])
                        lower = int(box[3 + 6*j])

                        # left = int(box[0 + 6*j])
                        # lower = int(box[2 + 6*j])
                        # right = int(box[1 + 6*j])
                        # upper = int(box[3 + 6*j])
                        BBOX.append(left)
                        BBOX.append(lower)
                        BBOX.append(right)
                        BBOX.append(upper)
                        # if left < right:
                        #     print('true')
                        # else:
                        #     print('flase')
                        # if upper < lower:
                        #     print('true')
                        # else:
                        #     print('flase')

                        if i == 0:
                            #建立初始独立肺结节名称列表
                            NODES.append(txt_name_list)
                            # print(NODES)
                            #建立初始独立肺结节坐标框列表
                            BOXS.append(BBOX)
                            # print(BOXS)
                        else:
                            #将最新读取的坐标与BOXS中保存的每一个坐标进行IOU计算，若大于0.7则为当前坐标的下一位置，若全不为0.7则为新结节
                            for x in range(len(nodeflag[-1])):
                                k = nodeflag[-1][x] - 1
                                # print(k)
                                #是否更新的肺结节标志
                                update = False
                                o_left = BOXS[k][0]
                                # print(BOXS[k][0][2])
                                o_right = BOXS[k][2]
                                o_lower = BOXS[k][1]
                                o_upper = BOXS[k][3]
                                IOUloss = IOU(o_left, o_right, o_upper, o_lower, left, right, upper, lower)
                                if IOUloss >= 0.5:
                                    #更新坐标
                                    BOXS[k][0] = left
                                    BOXS[k][2] = right
                                    BOXS[k][1] = lower
                                    BOXS[k][3] = upper
                                    update = True
                                    nodeflag1.append(k+1)
                                    #在对应位置添加图片名
                                    NODES[k].append(txt_name)
                                    # print('TRUE')

                            #不更新
                            if update == False:
                                #肺结节数量+1
                                flag = flag + 1
                                #创建新的肺结节列表
                                NODES.append(txt_name_list)
                                #对该新肺结节列表添加坐标
                                BOXS.append(BBOX)
                                nodeflag1.append(flag)
                            nodeflag.append(nodeflag1)
                        # print(nodeflag1)
    return NODES

if __name__ == "__main__":
    NODES = get_one_node_name(r'C:\Users\DL\Desktop\CROP7.12\LQTXT\LQ/')
    for i in range(len(NODES)):
        print(NODES[i])

