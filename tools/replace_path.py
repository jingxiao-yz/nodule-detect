import os


def replace(old_path, frm, to):
    # pre, match, post = old_path.rpartition(frm)  # 从右往左判断，以frm开始分
    # three = [pre, to, post]
    re_path = old_path.replace(frm,to)
    # print("reeeeeeeeeee:",re_path)
    new_dir, backslash, the_name = re_path.rpartition("/")
    new_path = new_dir + "/"
    # print(new_path)
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    return new_path, the_name
