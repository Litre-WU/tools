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
import muggle_ocr
import base64
import os
import exifread
from geopy.geocoders import Nominatim
from user_agent import generate_user_agent

app = FastAPI()


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


async def recognise(img_b64):
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
    text = sdk.predict(image_bytes=base64.b64decode(img_b64))
    # print(text)
    return text.strip()


class VerifyCode(BaseModel):
    img_b64: Optional[str] = None


@app.post("/captcha")
async def verify_code(item: VerifyCode, request: Request, user_agent: Optional[str] = Header(None),
                      x_token: List[str] = Header(None)):
    kwargs = item.dict()
    if not kwargs.get("img_b64", ""): return {"code": 400, "msg": "请传入正确的参数"}
    text = await recognise(kwargs.get("img_b64", ""))
    return JSONResponse({"code": 200, "msg": "OK", "result": text})


@app.get("/photo")
async def index(request: Request, response_class=HTMLResponse, user_agent: Optional[str] = Header(None),
                x_token: List[str] = Header(None), ):
    with open('template/index.html', 'r', encoding='UTF-8') as f:
        html = f.read()

    return HTMLResponse(content=html)


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
