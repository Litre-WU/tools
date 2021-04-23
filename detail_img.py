import base64
import io
import numpy as np
from PIL import Image
import aircv as ac
import easyocr


def img_deal(img):
    try:
        img_b64decode = base64.b64decode(img)
        image = io.BytesIO(img_b64decode)
        img = Image.open(image)
    except Exception as e:
        img = Image.open(img)
    img = img.convert('L')  # 图像灰度化
    arr = np.array(img)
    x, y = arr.shape  # 行，列数赋值
    # print(x, y)
    # 阈值
    fix_data = 200
    # 二值化
    for a in range(x):
        for b in range(y):
            if arr[a, b] > fix_data:
                arr[a, b] = 255
            else:
                arr[a, b] = 0
    # 裁边
    new_arr = []
    for b in range(y):
        new_arr += [[a, b] for a in range(x) if arr[a, b] == 0]
    row = [x[0] for x in new_arr]
    row_min = min(row)
    row_max = max(row)
    col = [x[1] for x in new_arr]
    col_min = min(col)
    col_max = max(col)
    arr = arr[row_min:row_max, col_min:col_max]
    # print(arr)
    # new_im = Image.fromarray(arr)  # 数组转图片
    # new_im.show()
    x = row_max - row_min
    y = col_max - col_min

    # 分割
    new_arr = []
    for b in range(y):
        if len([[a, b] for a in range(x) if arr[a, b] == 255]) == x:
            new_arr.append(b)
    col_split_lsit = [[0, new_arr[0]]]
    for i in range(len(new_arr)):
        if i < len(new_arr) - 1:
            if new_arr[i] + 1 != new_arr[i + 1]:
                col_split_lsit += [new_arr[i:i + 2]]
    col_split_lsit.append([new_arr[-1], -1])
    # print(col_split_lsit)
    for index, i in enumerate(col_split_lsit):
        new_im = Image.fromarray(arr[:, i[0]:i[1]])  # 数组转图片
        # new_im.show()
        new_im.save(f'test/{index}.png')


def test():
    import cv2
    img = cv2.imread('test/slide.png')
    b, g, r = cv2.split(img)
    print(b)
    blueImg = img[50:60, 50:60, 50:60]
    cv2.imshow('b', blueImg)
    import time
    time.sleep(10)
    # cv2.imshow("Blue 1", b)
    # cv2.imshow("Green 1", g)
    # cv2.imshow("Red 1", r)

    # print(img.shape)
    # arr = np.array(img)
    # print(arr)

    # pixel_sum = np.sum(arr, axis=1)
    # print(pixel_sum)

    # cropped = img[10:40, 20:40]
    # cv2.imwrite("test/slide2.png", cropped)


import pyautogui


def location(source, target):
    # pyautogui.screenshot('target.png')
    # position = ac.find_template(ac.imread('target.png'), ac.imread(source), threshold=0.5)
    position = ac.find_template(ac.imread(target), ac.imread(source), threshold=0.5, rgb=True, bgremove=True)
    print(position)
    if position:
        # for x in position:
        #     print(x)
        position = position["result"]
        return position
    else:
        return False


def ocr(img):
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    # reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, model_storage_directory='model/')

    # result = reader.detect('test/test.png')
    # print(result)
    # result = reader.recognize('test/test.png', horizontal_list=[[10, 152, 14, 38], [161, 270, 3, 46], [78, 104, 372, 396], [236, 276, 372, 396]],
    #                           free_list=[])
    # print(result)
    # result = reader.readtext(img)
    result = reader.readtext(img, detail=0)
    # result = reader.readtext('test/target.png')
    print(result)


if __name__ == '__main__':
    # img_deal("test/source.png")
    # rs = location(source="test/0.png", target="test/target.png")
    # print(rs)
    # if rs:
    #     pyautogui.moveTo(rs)
    # t = pyautogui.locateCenterOnScreen('test/0.png', grayscale=True, confidence=0.5)
    # print(t)
    # pyautogui.moveTo(t)
    # ocr('test/test.png')
    # ocr('test/target1.png')
    # ocr('pic/123.png')

    # from paddleocr import PaddleOCR, draw_ocr
    # ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    # img_path = 'test/test.png'
    # result = ocr.ocr(img_path, cls=True)
    # for line in result:
    #     print(line)

    # test()

    # img = Image.open('test/slide.png')
    # img = img.convert('L')  # 图像灰度化
    # arr = np.array(img)
    # x, y = arr.shape  # 行，列数赋值
    # print(x, y)
    # # 阈值
    # fix_data = 160
    # # 二值化
    # for a in range(x):
    #     for b in range(y):
    #         if arr[a, b] > fix_data:
    #             arr[a, b] = 255
    #         else:
    #             arr[a, b] = 0
    # new_im = Image.fromarray(arr)  # 数组转图片
    # # new_im.show()
    # new_im.save('test/test2.png')
    rs = location('test/test1.png', 'test/test2.png')
    print(rs)
    pyautogui.moveTo(rs)
    # rs = pyautogui.locateCenterOnScreen('test/test1.png')
    # print(rs)
    # pyautogui.moveTo(rs)
