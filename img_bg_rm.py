# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: img_bg_rm.py
# Time: 12月 17, 2021
import cv2
import numpy as np
from math import floor, degrees, atan
from scipy import misc, ndimage
from PIL import Image
from collections import Counter
from removebg import RemoveBg


# 图片纠正
def img_correct(**kwargs):
    img_path = kwargs.get("img_path", "")
    if not img_path: return None
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    # 霍夫变换
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 0)
    rotate_angle = 0
    for rho, theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        if x1 == x2 or y1 == y2:
            continue
        t = float(y2 - y1) / (x2 - x1)
        rotate_angle = degrees(atan(t))
        if rotate_angle > 45:
            rotate_angle = -90 + rotate_angle
        elif rotate_angle < -45:
            rotate_angle = 90 + rotate_angle
    rotate_img = ndimage.rotate(img, rotate_angle)
    cv2.imwrite(img_path, rotate_img)


# 图片裁剪
def img_cut(**kwargs):
    img_path = kwargs.get("img_path", "")
    if not img_path: return None
    img = cv2.imread(img_path)
    # print(img.shape)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("img", gray_image)
    ret, binary = cv2.threshold(gray_image, 145, 255, cv2.THRESH_BINARY)
    h = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours = h[0]
    draw_img = cv2.drawContours(img.copy(), h[0], -1, (0, 0, 255), 1)
    # cv2.imshow("draw_img", draw_img)
    x_list = []
    y_list = []
    for x, col in enumerate(draw_img):
        for y, i in enumerate(col):
            if list(i) == [0, 0, 255]:
                x_list.append(x)
                y_list.append(y)
    x_list = Counter(x_list).most_common(len(x_list))
    y_list = Counter(y_list).most_common(len(y_list))
    x_list = [x_list[0][0], x_list[1][0]]
    y_list = [y_list[0][0], y_list[1][0]]
    pad = kwargs.get("pad", 6)
    x_min, x_max, y_min, y_max = int(min(x_list)) + pad,int(max(x_list)) - pad,int(min(y_list)) + pad,int(max(y_list)) - pad
    cropped = img[x_min:x_max, y_min:y_max]
    cv2.imwrite(img_path, cropped)
    # cv2.imshow("draw_img2", cropped)
    # cv2.waitKey(0)


# 去除背景
def img_rm_bg_api(**kwargs):
    img_path = kwargs.get("img_path", "")
    key = kwargs.get("key", "")
    if not (img_path and key): return None
    rmbg = RemoveBg(key, "./error.log")
    rmbg.remove_background_from_img_file(img_path)


# 筛选列表连续元素
def list_filter_series(**kwargs):
    """
    :param kwargs:{"list":[],offset:5}
    :return: []
    """
    source_list = kwargs.get("list", "")
    if not source_list: return []
    offset = kwargs.get("offset", 5)
    new_list = []
    for i, x in enumerate(source_list):
        if x + offset in source_list or x - offset in source_list:
            new_list.append(x)
    return new_list


# 去背景
def img_rm_bg(**kwargs):
    img_path = kwargs.get("img_path", "")
    if not img_path: return None
    img = cv2.imread(img_path)
    rows, cols, channels = img.shape
    # cv2.imshow('input', img)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # cv2.imshow('hsv', hsv)

    lower_blue = np.array([0, 70, 100])
    upper_blue = np.array([15, 160, 190])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)  # 蓝色范围内变白，其余之外全部变黑
    erode = cv2.erode(mask, None, iterations=1)
    dilate = cv2.dilate(mask, None, iterations=1)
    # cv2.imshow('dilate', dilate)

    y_list = []
    x_list = []
    for y, i in enumerate(range(rows)):
        for x, j in enumerate(range(cols)):
            if dilate[i, j] == 0:
                y_list.append(y)
                x_list.append(x)

    x_list = Counter(x_list).most_common(len(x_list))
    y_list = Counter(y_list).most_common(len(y_list))
    x_list = list_filter_series(**{"list": sorted([x[0] for x in x_list if x[1] > (rows / 2)])})
    y_list = list_filter_series(**{"list": sorted([y[0] for y in y_list if y[1] > (cols / 2)])})
    x_min, x_max, y_min, y_max = min(x_list), max(x_list), min(y_list), max(y_list)
    print(x_min, x_max, y_min, y_max)
    for y, i in enumerate(range(rows)):
        for x, j in enumerate(range(cols)):
            if y < y_min or y > y_max or x < x_min or x > x_max:
                dilate[i, j] = 255
            if dilate[i, j] == 255:  # 像素点为0表示的是黑色,255表示的是白色，范围外的黑色其余改为白色
                img[i, j] = [255, 255, 255]
    cv2.imwrite(f'{img_path}_no_bg2.png', img)
    # cv2.imshow('output', img)
    # cv2.waitKey(0)


# 背景变透明
def bg_clear(**kwargs):
    img_path = kwargs.get("img_path", "")
    if not img_path: return None
    img = Image.open(img_path)
    new_im = img.convert("RGBA")
    datas = new_im.getdata()
    new_list = []
    for item in datas:
        if item[0] > 225 and item[1] > 225 and item[2] > 225:
            new_list.append((255, 255, 255, 0))
        else:
            new_list.append(item)
    new_im.putdata(new_list)
    # new_im.show()
    new_im.save(img_path)


if __name__ == '__main__':
    meta = {
        "img_path": "Card.jpg",
        "pad": 3,
        "key": "hvidkdXLxsQaqpmM2KtGwSUH"
    }
    img_correct(**meta)
    # img_cut(**meta)
    # img_rm_bg(**meta)
    # bg_clear(**meta)
