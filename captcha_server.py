# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: captcha_server.py
# Time: 5月 10, 2021
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64
import muggle_ocr
import json


class Server(BaseHTTPRequestHandler):
    def handler(self):
        self.wfile.write(self.rfile.readline())

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        if self.path != '/':
            response = json.dumps({
                "code": 404,
                "msg": "Not Found!",
            })
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
            return response
        html = '<title>验证码识别</title><body style="text-align:center"><h1>验证码识别</h1></body>'
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()
        self.wfile.write(html.encode())
        return html

    def do_POST(self):
        if self.path != '/captcha':
            response = json.dumps({
                "code": 404,
                "msg": "Not Found!",
            })
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
            return response
        # 解析data
        post_data = parse_qs(self.rfile.read(int(self.headers['Content-Length'])).decode())
        # 验证码识别
        image_bytes = base64.b64decode(post_data["img_b64"][0]) if post_data.get("img_b64", "") else ""
        sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
        text = sdk.predict(image_bytes=image_bytes)
        response = json.dumps({
            "code": 200,
            "msg": "ok",
            "result": text
        })
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
        return response


if __name__ == '__main__':
    server_address = ('0.0.0.0', 8082)
    print(f"Starting server, listen at: {server_address[0]}:{server_address[1]}")
    HTTPServer(server_address, Server).serve_forever()
