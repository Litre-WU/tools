# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: api.py
# Time: 6月 05, 2021
from typing import Optional, List
from fastapi import FastAPI, Header, Cookie, Depends, BackgroundTasks, File, UploadFile
from starlette.requests import Request
from fastapi.responses import JSONResponse, ORJSONResponse, HTMLResponse
from pydantic import BaseModel
import io
from json import load
import torchvision
import onnxruntime
from PIL import Image
import numpy as np
import muggle_ocr
import base64
import os
import exifread
from geopy.geocoders import Nominatim
from user_agent import generate_user_agent

app = FastAPI()


# 首页
@app.get("/")
async def index(request: Request, user_agent: Optional[str] = Header(None),
                x_token: List[str] = Header(None)):
    result = {
        "code": 200,
        "msg": "来了！老弟",
        "result": "你看这个面它又长又宽，就像这个碗它又大又圆",
        "info": {
            "openapi_url": "/api/v1/openapi.json",
            "ip": request.client.host,
            "x-token": x_token,
            "user-agent": user_agent,
            "headers": dict(request.headers)
        }
    }
    return JSONResponse(result)


# torchvision识别
async def captcha_recognise(img_b64):
    ort_session = onnxruntime.InferenceSession('common.onnx')
    with open('charset.json', encoding='utf-8') as f:
        charset = load(f)["charset"]
    image = Image.open(io.BytesIO(base64.b64decode(img_b64)))
    image = image.resize((int(image.size[0] * (64 / image.size[1])), 64), Image.ANTIALIAS).convert('L')
    totensor = torchvision.transforms.ToTensor()
    normalize = torchvision.transforms.Normalize((0.5), (0.5))
    image = totensor(image)
    image = normalize(image)
    ort_inputs = {'input1': np.array([image.detach().cpu().numpy() if image.requires_grad else image.cpu().numpy()])}
    ort_outs = ort_session.run(None, ort_inputs)
    result = "".join([charset[x] for x in ort_outs[0][0] if x])
    return result


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
@app.post("/captcha")
async def verify_code(item: VerifyCode, request: Request, user_agent: Optional[str] = Header(None),
                      x_token: List[str] = Header(None)):
    kwargs = item.dict()
    if not kwargs.get("img_b64", ""): return {"code": 400, "msg": "请传入正确的参数"}
    # torchvision识别
    text = await muggle_ocr_recognise(kwargs.get("img_b64", ""))
    # # muggle_ocr识别
    # text = await muggle_ocr_recognise(kwargs.get("img_b64", ""))
    return JSONResponse({"code": 200, "msg": "OK", "result": text})


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


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8082)