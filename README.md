# nodule-detect

logs 和 model_data 文件夹内文件太大, 暂没有上传

## <center> 检测代码目录结构说明

#### classification_utils/

#### logs/

#### model_data/

#### tools/

- `dic2img.py`
   dicom格式转图片格式（.png）
- `json2execl.py`
   josn格式数据转excel表
- `outline_back_mixed.py`
   边缘线贴回图片脚本，起勾勒结节外形的作用
- `outline.py`
   画边缘线的脚本
- `png2svg.py`
   图片转svg脚本，网站的前端页面支持svg格式的图片显示
- `replace_path.py`
   路径替换函数

#### unet_nets/

#### unet_utils/

#### yolox_nets/

#### yolox_utils/

#### `awake_manage.log`

`awake_manage.sh`的后台输出日志

#### `awake_manage.sh`

定时重启检测算法的shell脚本

#### `classification.py`

#### `first_yolo.py`

#### `image_operate.py`

主要用来从数据库拉取网页端上传的待检测dicom文件，下载到我们规定的文件夹里面

#### `make_result.py`

#### `manage.py`

控制检测流程的脚本，主要有两个while循环：

- 不停监察网页端是否有上传文件的操作，当网页端上传完毕，也就是当用户上传待检测文件到数据库里面，我们再把这些文件拿出来放到我们规定的文件夹里面，配和`image_operate.py`使用
- 不停监察是否有待检测的文件，有就开是检测，配和`predict_ksn.py`使用

#### `manage.log`

  `manage.py`的后台台输出日志

#### `predict_ksn.py`

检测部分的 核心流程

#### `recongnize_one.py`

#### `second_yolo.py`

#### `summary.py`

#### `unet.py`

## <center> 与 网站后台交互 文件目录结构 说明

检测代码（python）和网站后台代码（Java）都会操作相应的文件，这些文件全部都位于根目录下的 `/opt` 文件夹里面：
![opt](/readmefile/opt目录.png)

主要是这两个文件夹：`/opt/analysed`、`/opt/excel`，其它是Java后台相关的目录

1. `/opt/analysed` 是python检测代码主要操作文件的地方，它里面的文件结构一般长这样：
![analysed](/readmefile/analysed.png)
每个数字（文件夹）代表一次检测，里面都是一位用户的数据，检测代码在里面进行文件格式转换、检测、提取信息等操作，数字文件夹里面结构如下（以433文件夹为例）：
![433](/readmefile/433.png)
在检测过程中，几乎所有的操作产生的文件都在这里面：

   - `1_xxxxxxx.txt`文件只是用来标识这份dicom数据的病人名字。用来和Java后台交互，网页显示的姓名就是读的这个文件，
   - `result`文件夹里面放的是最后的检测结果，包括检测结果信息，最终展示的图片等，Java后台从这里取数据，展示到网页端
   - `source`里面放的是dicom源文件、检测过程中产生的临时文件等
   - `success.txt`就是个状态文件，和`1_xxxxxxx.txt`的作用类似，告诉Java后台这个用户检测完成了，具体其它状态可以看 `manage.py`
2. `/opt/excel`文件夹主要是放结果excel表，对应工具脚本里面的 `tools/json2execl.py` ，表格主要给到网页端供用户下载
