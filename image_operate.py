import requests
import wget
import json
import os


#### 下载数据库的dicom到规定目录，用于检测，同时返回文件夹的数字id
def download_image(download_path):
    res = requests.get("http://47.111.159.70:8095/api/v0.1/compresses/images")
    image_group_list = res.json()["message"]
    ####下载图片到本地路径
    group_id=''
    # print('gggggggggggggggggggggggggggg',image_group_list)
    for group in image_group_list:
        ####建立group文件夹中的source文件夹
        group_id = str(group['group_id'])
        print("\ngroup_id是是是是是是是是是是是是：",group_id)
        dcm_file_dir = download_path + group_id + "/source"
        if not os.path.exists(dcm_file_dir):
            os.makedirs(dcm_file_dir)
        #### 获取文件
        for image in group['image_infos']:
            temp = image["image_url"].split(".")[-1]
            if temp == "dcm":
                wget.download(image["image_url"], dcm_file_dir + "/" + str(image["id"]) + "." + temp)
                # print("\nimage_id是是是是是是是是是是是是：",image["id"])
    return group_id


#### 请求云端接口保存结节信息
def save_nodule_info(request_json):
    #### print(request_json)
    url = "http://47.111.159.70:8095/api/v0.1/nodules?page_no=1&page_size=100000"

    payload = {
        "image_id": int(request_json["imageId"].split('_')[0]),  ##图片标识
        "file_name" : request_json["file_name"],
        "coordinates": ';'.join(request_json["coordinates"]),  ##坐标
        "probability": ';'.join(request_json["probability"]),  ##概率
        "status":';'.join(request_json["status"]),##大体好坏判断，现在改到二轮添加了
        "texture_category": ';'.join(request_json["textureCategory"]),  ##具体纹理类别判断，二轮判断结果
        # 'volumeCategory': request_json["volumeCategory"],##体积类别
        "diameter": ';'.join(request_json["diameter"]),  ##直径
        # "resolve_status": 1
    }
    #### print("payloaddddddddddddddddddddddd:",payload)
    headers = {"content-type": "application/json"}
    ret = requests.post(url, data=json.dumps(payload), headers=headers)
    if ret.status_code == 200:
        print("保存结节信息成功")
    else:
        print("保存结节信息失败")


# 更新图片对应的影响可见、参考意见信息
def update_image_info(image_id, videoSeeContent, referencesContent):
    url = "http://47.111.159.70:8095/api/v0.1/images/" + image_id
    payload = {
        "videoSeeContent": videoSeeContent,  ##影像可见
        "referencesContent": referencesContent,  ##参考意见
    }
    headers = {"content-type": "application/json"}
    ret = requests.put(url, data=json.dumps(payload), headers=headers)
    if ret.status == 200:
        print("保存图片结节信息成功")

#文件对应分析标志
def mark_predict_complete(image_id,flag):
    ##  flag：1有结节，2没有结节，3该文件无法处理
    url = "http://47.111.159.70:8095/api/v0.1/images/"+image_id+"/status?status="+str(flag)
    headers = {"content-type": "application/json"}
    ret = requests.put(url)
    if ret.status_code == 200:
        print("completed!：",image_id)

#名字
def upload_name(image_name):
    ##image_name格式：123_张三.jpg
    url = "http://47.111.159.70:8095/api/v0.1/images/"+image_name.split('_')[0]+"/users?name="+str(image_name.split('_')[1].split('.')[0])
    headers = {"content-type": "application/json"}
    ret = requests.put(url)
    if ret.status_code == 200:
        print("已成功传名字：",image_name)