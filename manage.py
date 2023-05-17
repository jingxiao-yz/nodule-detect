from operator import truediv
import threading
from threading import Lock, Thread
import image_operate
import os
import time
import shutil
import os
import random
from fnmatch import fnmatch, fnmatchcase

import predict_ksn

# 监察周期（秒）
period = 5

# 请求云端接口获取数据

def download_file():

    while True:

        # 调试可以将try-expect关掉，不然错误无法输出显示
        try:
            # 尝试下载dcm，并获取group_id
            group_id = image_operate.download_image(whole_file_dir)
            if group_id == '':
                time.sleep(period)
                # print('there are no files to download')
                continue
            else:
                # 已获取group_id
                if len(os.listdir(whole_file_dir + group_id + "/source/")) != 0:
                    print('已下载该组所有文件')
                    # 创建该group状态文本文件：wait: 等待分析；analysing: 分析中；success：分析结束有结节；success-empty: 分析结束无结节
                    state_file_path = whole_file_dir + group_id + "/wait.txt"
                    if not os.path.exists(state_file_path):
                        open(state_file_path, "w")
                else:
                    # fail,不符合检测要求，该group的source文件夹中没有符合要求的dcm
                    state_file_path = whole_file_dir + group_id + "/fail.txt"
                    if not os.path.exists(state_file_path):
                        open(state_file_path, "w")
                    continue
        except:
            continue


# 监查目录随时准备分析
def detect_file():

    while True:

        # 调试可以将try-expect关掉，不然错误无法输出显示
        try:
            # 查看每个数字文件夹里面的状态文本
            group_list = os.listdir(whole_file_dir)
            for group in group_list:
                group_id = group
                state1 = whole_file_dir + group_id + "/wait.txt"
                state2 = whole_file_dir + group_id + "/analysing.txt"
                state3 = whole_file_dir + group_id + "/success.txt"
                state4 = whole_file_dir + group_id + "/success-empty.txt"
                # 若存在wait状态文件,把状态文件名置为analysing
                if os.path.exists(state1):
                    os.rename(state1, state2)
                    # 开始分析
                    print('detect')
                    dcm_file_path = whole_file_dir + group_id + "/source/"
                    # 开始调用函数检测，返回状态码
                    flag_num = predict_ksn.dir_predict(dcm_file_path, group_id)
                    # 该group分析完成，状态文件名置为success或者success_empty

                    if flag_num == 3:
                        # 状态码 3 表明 分析过程正常结束，有结节
                        os.rename(state2, state3)
                    elif flag_num == 4:
                        # 状态码 4 表明 分析过程正常结束，没有结节
                        os.rename(state2, state4)
                else:
                    continue
            time.sleep(period)
            # print('there are no files to detect')

        except:
            continue


if __name__ == '__main__':
    localtime = time.asctime(time.localtime(time.time()))
    print(localtime, ": dection starts--------------------")

    # 所有的流程文件都在这个目录里面
    whole_file_dir = r"/opt/analysed/"
    if not os.path.exists(whole_file_dir):
        os.makedirs(whole_file_dir)

    ta = threading.Thread(None, download_file)
    tb = threading.Thread(None, detect_file)

    ta.start()
    tb.start()
