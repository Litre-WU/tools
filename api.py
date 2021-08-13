# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: api.py
# Time: 6月 05, 2021
import asyncio
from typing import Optional, List
from fastapi import FastAPI, Header, Cookie, Depends, BackgroundTasks, File, UploadFile
from starlette.requests import Request
from fastapi.responses import JSONResponse, ORJSONResponse, HTMLResponse
from pydantic import BaseModel
import io
from json import load
# import torchvision
import onnxruntime
from PIL import Image
import numpy as np
import paddlehub
import muggle_ocr
import base64
import os
import exifread
from geopy.geocoders import Nominatim
from user_agent import generate_user_agent
import aiohttp
from time import sleep
from random import randint
from lxml import etree
from urllib.parse import urljoin

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

semaphore = asyncio.Semaphore(10)

app = FastAPI()


# 首页
@app.get("/")
async def index(request: Request, user_agent: Optional[str] = Header(None),
                x_token: List[str] = Header(None)):
    result = {
        "Code": 200,
        "Msg": "来了！老弟",
        "Result": "你看这个面它又长又宽，就像这个碗它又大又圆",
        "Info": {
            "OpenApi_Url": "/api/v1/openapi.json",
            "IP": request.client.host,
            "X-Token": x_token,
            "User-Agent": user_agent,
            "Headers": dict(request.headers)
        }
    }
    return JSONResponse(result)


# onnx
async def captcha_recognise(img_b64):
    ort_session = onnxruntime.InferenceSession('common.onnx')
    with open('charset.json', encoding='utf-8') as f:
        charset = load(f)["charset"]
    image = Image.open(io.BytesIO(base64.b64decode(img_b64)))
    image = image.resize((int(image.size[0] * (64 / image.size[1])), 64), Image.ANTIALIAS).convert('L')

    # totensor = torchvision.transforms.ToTensor()
    # normalize = torchvision.transforms.Normalize((0.5), (0.5))
    # image = totensor(image)
    # image = normalize(image)
    # ort_inputs = {'input1': np.array([image.detach().cpu().numpy() if image.requires_grad else image.cpu().numpy()])}

    image = np.array(image).astype(np.float32)
    image = np.expand_dims(image, axis=0) / 255.
    image = (image - 0.5) / 0.5
    ort_inputs = {'input1': np.array([image])}
    ort_outs = ort_session.run(None, ort_inputs)
    result = []
    last_item = 0
    for item in ort_outs[0][0]:
        if item and item != last_item:
            last_item = item
            result.append(charset[item])
    return "".join(result)


# PaddleOCR识别
async def ocr_recognise(img_b64):
    ocr = paddlehub.Module(name="chinese_ocr_db_crnn_mobile")
    result_list = ocr.recognize_text(images=[np.array(Image.open(io.BytesIO(base64.b64decode(img_b64))))])
    return result_list[0]["data"]


# muggle_ocr识别
async def muggle_ocr_recognise(img_b64):
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
    text = sdk.predict(image_bytes=base64.b64decode(img_b64))
    # print(text)
    return text.strip()


# 参数定义
class VerifyCode(BaseModel):
    img_b64: Optional[str] = None


# 验证码识别接口
@app.post("/{path}")
async def verify_code(item: VerifyCode, path: str, request: Request, user_agent: Optional[str] = Header(None),
                      x_token: List[str] = Header(None)):
    kwargs = item.dict()
    if not kwargs.get("img_b64", ""): return {"Code": 400, "Msg": "请传入正确的参数!"}
    path_dict = {
        "ocr": ocr_recognise,
        "captcha": captcha_recognise,
        "captcha2": muggle_ocr_recognise
    }
    result = await path_dict[path](kwargs["img_b64"]) if path in path_dict else ""
    return JSONResponse({"Code": 200, "Msg": "OK", "Result": result})


# 照片信息上传
@app.get("/photo")
async def index(request: Request, response_class=HTMLResponse, user_agent: Optional[str] = Header(None),
                x_token: List[str] = Header(None), ):
    with open('template/index.html', 'r', encoding='UTF-8') as f:
        html = f.read()

    return HTMLResponse(content=html)


# 照片信息提取接口
@app.post("/photo/upload/")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    for file in files:
        content = await file.read()
        with open(file.filename, 'wb') as f:
            f.write(content)
        tags = exifread.process_file(open(file.filename, 'rb'))
        # print(tags)
        data = {
            "机型": f'{tags.get("Image Make", "")} {tags.get("Image Model", "")}',
            "拍摄时间": f'{tags.get("Image DateTime", "")}',
            "经度": f'{tags.get("GPS GPSLongitude", "")}',
            "纬度": f'{tags.get("GPS GPSLatitude", "")}',
            "摄像头信息": f'{tags.get("EXIF Tag 0x9999", "")}',
            "长度": f'{tags.get("EXIF ExifImageLength", "")}',
            "宽度": f'{tags.get("EXIF ExifImageWidth", "")}',
        }
        if tags.get("GPS GPSLongitude", "") and tags.get("GPS GPSLatitude", ""):
            geolocator = Nominatim(user_agent=generate_user_agent())
            location = geolocator.reverse(
                f'{eval(str(tags.get("GPS GPSLatitude", "")))[0]},{eval(str(tags.get("GPS GPSLongitude", "")))[0]}')
            data["位置"] = str(location)
        print(data)
        os.remove(file.filename)
        return JSONResponse(data)


# 公共请求函数
async def pub_req(**kwargs):
    method = kwargs.get("method", "GET")
    url = kwargs.get("url", "")
    params = kwargs.get("params", {})
    data = kwargs.get("data", {})
    headers = {**{"User-Agent": generate_user_agent()}, **kwargs.get("headers", {})}
    proxy = kwargs.get("proxy", "")
    timeout = kwargs.get("timeout", 20)
    try:
        # if await ip_test():
        async with semaphore:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3),
                                             connector=aiohttp.TCPConnector(ssl=False),
                                             trust_env=True) as client:
                async with client.request(method=method, url=url, params=params, data=data, headers=headers,
                                          proxy=proxy,
                                          timeout=timeout) as rs:
                    if rs.status == 200 or 201:
                        content = await rs.read()
                        return content
                    else:
                        sleep(randint(1, 2))
                        retry = kwargs.get("retry", 0)
                        retry += 1
                        if retry >= 2:
                            return None
                        kwargs["retry"] = retry
                        return await pub_req(**kwargs)
    except Exception as e:
        sleep(randint(1, 2))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 2:
            return None
        kwargs["retry"] = retry
        return await pub_req(**kwargs)


# 商业快讯
@app.get("/business_news")
async def business_news(request: Request, RankTime: Optional[str], response_model=JSONResponse):
    meta = {
        "method": "GET",
        "url": "https://www.qcc.com/index_flashnewslist",
        "params": {
            "ajax": "true",
            "lastRankIndex": RankTime,
            "lastRankTime": RankTime
        }
    }
    res = await pub_req(**meta)
    html = etree.HTML(res.decode())
    flnews_date = html.xpath('//div[@class="flnews-date"]/text()')
    flnews_date = flnews_date[0] if flnews_date else ""
    flnews = html.xpath('//div[@class="flnews-cell"]')
    if flnews:
        try:
            data_list = [{
                "时间": f'{flnews_date} {x.xpath("div/span[last()]/text()")[0]}' if x.xpath(
                    "div/span[last()]/text()") else "",
                "标题": x.xpath("div/div/div[@class='title']/a/text()")[0].strip() if x.xpath(
                    "div/div/div[@class='title']/a/text()") else "",
                "链接": x.xpath("div/div/div[@class='title']/a/@href")[0].strip(),
                "标签": x.xpath("div/div/div[@class='tag']/span/text()")[0].strip("#") if x.xpath(
                    "div/div/div[@class='tag']/span/text()") else "",
                "简述": x.xpath("div/div/div[@class='content']/text()")[0].strip() if x.xpath(
                    "div/div/div[@class='content']/text()") else "",
                "关键字": [{a.xpath('text()')[0]: urljoin(meta["url"], a.xpath('@href')[0])} for a in
                        x.xpath('div/div/div/div/a')] if x.xpath(
                    'div/div/div/a') else []
            } for x in flnews]
            # print(data_list)
            return {"Code": "200", "Msg": "OK", "Result": data_list}
        except Exception as e:
            print('business_news', e)
            return {"Code": "501", "Msg": "Fail", "Result": []}


if __name__ == '__main__':
    # import uvicorn
    # uvicorn.run(app, host='0.0.0.0', port=8082)
    rs = asyncio.get_event_loop().run_until_complete(business_news(Request, RankTime=''))
    print(rs)
