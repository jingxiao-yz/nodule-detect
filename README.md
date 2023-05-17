# nodule-detect

logs 和 model_data 文件夹内文件太大, 暂没有上传

## 检测代码目录结构说明

#### classification_utils/

#### logs/

#### model_data/

#### tools/

- dic2img.py
   dicom格式转图片格式（.png）
- json2execl.py
   josn格式数据转excel表
- outline_back_mixed.py
   边缘线贴回图片脚本，起勾勒结节外形的作用
- outline.py
   画边缘线的脚本
- png2svg.py
   图片转svg脚本，网站的前端页面支持svg格式的图片显示
- replace_path.py
   路径替换函数

#### unet_nets/

#### unet_utils/

#### yolox_nets/

#### yolox_utils/

#### awake_manage.sh

定时重启检测算法的shell脚本

#### classification.py

#### first_yolo.py

#### image_operate.py

主要用来从数据库拉取网页端上传的待检测dicom文件，下载到我们规定的文件夹里面

#### make_result.py

#### manage.py

控制检测流程的脚本主
要两部分：

1. 不停监察网页端是否有上传文件的操作，当网页端上传完毕，也就是当用户上传待检测文件到数据库里面，我们再把这些文件拿出来放到我们规定的文件夹里面，配和`image_operate.py`使用
2. 不停监察是否有待检测的文件，有就开是检测，配和`predict_ksn.py`使用

#### predict_ksn.py

检测部分 核心 流程控制 脚本

#### recongnize_one.py

#### second_yolo.py

#### summary.py

#### unet.py
