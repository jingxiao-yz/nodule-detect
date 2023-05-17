import os
import base64


def tosvg(img_path, img_name):
    # analysed_file= r'/opt/analysed/'
    # if not os.path.exists(analysed_file):
    #     os.makedirs(analysed_file)

    startSvgTag = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
        <svg version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        width="240px" height="240px" viewBox="0 0 240 240">"""
    endSvgTag = """</svg>"""

    # 编码图片
    pngFile = open(img_path+img_name, "rb")
    base64data = base64.b64encode(pngFile.read())
    base64String = '<image xlink:href="data:image/png;base64,{0}" width="240" height="240" x="0" y="0" />'.format(
        base64data.decode("utf-8")
    )
    f = open(img_path.replace("layer/", "/") + img_name.replace(".jpg", ".svg"), "w")
    f.write(startSvgTag + base64String + endSvgTag)
