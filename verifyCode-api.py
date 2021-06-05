# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: verifyCode-api.py
# Time: 6月 05, 2021
from typing import Optional, List
from fastapi import FastAPI, Header, Cookie, Depends, BackgroundTasks
from starlette.requests import Request
from fastapi.responses import JSONResponse, ORJSONResponse
from pydantic import BaseModel
import muggle_ocr
import base64

app = FastAPI()


@app.get("/")
async def index(request: Request, response_class=ORJSONResponse, user_agent: Optional[str] = Header(None),
                x_token: List[str] = Header(None), ):
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
    return result


async def recognise(img_b64):
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
    text = sdk.predict(image_bytes=base64.b64decode(img_b64))
    # print(text)
    return text.strip()


class OCRItem(BaseModel):
    img_b64: str = None


@app.post("/")
async def ocr(item: OCRItem, request: Request, response_class=ORJSONResponse, user_agent: Optional[str] = Header(None),
              x_token: List[str] = Header(None), ):
    kwargs = item.dict()
    # print(kwargs)
    if not kwargs.get("img_b64", ""): return {"code": 400, "msg": "请传入正确的参数"}
    text = await recognise(kwargs.get("img_b64", ""))
    return {"code": 200, "msg": "OK", "result": text}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
