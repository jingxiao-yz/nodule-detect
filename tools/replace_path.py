import os

# 切换路径函数
def replace(old_path, frm, to):
    # pre, match, post = old_path.rpartition(frm)  # 从 右 往 左 判断，以 frm 字符开始分
    re_path = old_path.replace(frm,to)
    new_dir, backslash, the_name = re_path.rpartition("/")
    new_path = new_dir + "/"

    # 创建文件夹
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path, the_name

# 虽然 python 字符串自己有 replace 函数，但为了方便，稍微增加一些功能，如创建文件夹，减少重复代码

# 当re_path是：/A/B/E/d.png
# 返回的new_path是：/A/B/E/
# 返回的the_name是：d.png
