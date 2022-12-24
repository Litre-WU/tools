# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: 常用函数.py
# Time: 11月 01, 2021
import asyncio
from urllib import request
from requests import Session
from aiohttp import ClientSession, ClientTimeout, TCPConnector, BasicAuth
from user_agent import generate_user_agent
from time import sleep
from random import randint
import socket
from sys import platform
import os
from loguru import logger

logger.add(f'{os.path.basename(__file__)[:-3]}.log', rotation='200 MB', compression='zip', enqueue=True,
           serialize=False, encoding='utf-8', retention='7 days')

host = socket.gethostbyname(socket.gethostname())

if platform == "win32":
    asyncio.set_event_loop(asyncio.ProactorEventLoop())
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ip = ".".join([str(randint(0, 255)) for _ in range(4)])

headers = {
        "X-Forwarded-For": ip,
        "X-Forwarded": ip,
        "Forwarded-For": ip,
        "Forwarded": ip,
        "X-Forwarded-Proto": ip,
        "X-Forwarded-Host": ip,
        "X-Requested-With": ip,
        "X-Client-IP": ip,
        "X-remote-IP": ip,
        "X-remote-addr": ip,
        "X-Real-IP": ip,
        "True-Client-IP": ip,
        "Client-IP": ip,
        "X_FORWARDED_FOR": ip,
        "X_REAL_IP": ip,
        "User-Agent": generate_user_agent()
    }

# urllib
async def url_req(**kwargs):
    try:
        req = request.Request(method=kwargs.get("method", "GET"), url=kwargs["url"],
                              headers={"User-Agent": generate_user_agent()} | kwargs.get("headers", {}),
                              data=kwargs.get("data", ""))
        with request.urlopen(req) as res:
            if res.status == 200:
                return res.read()
            else:
                logger.info(f'url_req {res.read().decode()}')
                sleep(randint(1, 2))
                retry = kwargs.get("retry", 0)
                retry += 1
                if retry >= 3:
                    return None
                kwargs["retry"] = retry
                return await url_req(**kwargs)
    except Exception as e:
        logger.info(f'url_req {kwargs} {e}')
        sleep(randint(1, 2))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 3:
            return None
        kwargs["retry"] = retry
        return await url_req(**kwargs)


# requests
async def req(**kwargs):
    try:
        with Session() as client:
            with client.request(method=kwargs.get("method", "GET"), url=kwargs["url"],
                                headers=kwargs.get("headers", ""), params=kwargs.get("params", ""),
                                data=kwargs.get("data", ""), proxies=kwargs.get("proxy", ""),
                                timeout=kwargs.get("timeout", 10)) as rs:
                if rs.status_code == 200:
                    return rs.content
                else:
                    logger.info(f'req {rs.text}')
                    sleep(randint(1, 2))
                    retry = kwargs.get("retry", 0)
                    retry += 1
                    if retry >= 3:
                        return None
                    kwargs["retry"] = retry
                    return await req(**kwargs)
    except Exception as e:
        logger.info(f'req {kwargs} {e}')
        sleep(randint(1, 2))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 3:
            return None
        kwargs["retry"] = retry
        return await req(**kwargs)


# aiohttp
async def aio_req(**kwargs):
    try:
        async with kwargs.get("semaphore", asyncio.Semaphore(50)):
            async with ClientSession(timeout=ClientTimeout(total=10),
                                     connector=TCPConnector(ssl=False), trust_env=True) as client:
                client.proxy = kwargs.get("proxy", "")
                proxy_auth = BasicAuth(kwargs.get("proxy_user", ""), kwargs.get("proxy_pass", ""))
                async with client.request(method=kwargs.get("method", "GET"), url=kwargs["url"],
                                          headers={"User-Agent": generate_user_agent()} | kwargs.get("headers", {}),
                                          params=kwargs.get("params", {}), data=kwargs.get("data", {}),
                                          proxy_auth=proxy_auth, timeout=kwargs.get("timeout", 10)) as rs:
                    if rs.status == 200:
                        return await rs.read()
                    else:
                        logger.info(f'aio_req {await rs.text()}')
                        sleep(randint(1, 2))
                        retry = kwargs.get("retry", 0)
                        retry += 1
                        if retry >= 3:
                            return None
                        kwargs["retry"] = retry
                        return await aio_req(**kwargs)
    except Exception as e:
        logger.info(f'aio_req {kwargs} {e}')
        sleep(randint(1, 2))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 3:
            return None
        kwargs["retry"] = retry
        return await aio_req(**kwargs)


class Req:
    def __init__(self, method="GET", url="", params="", data="", headers={"User-Agent": generate_user_agent()},
                 proxy="", timeout=10):
        self.method = method
        self.url = url
        self.params = params
        self.data = data
        self.headers = headers
        self.proxy = proxy
        self.timeout = timeout

    def url_req(self):
        try:
            req = request.Request(method=self.method, url=self.url, headers=self.headers, data=self.data)
            with request.urlopen(req) as res:
                return res.read().decode()
        except Exception as e:
            return str(e)

    def __str__(self):
        try:
            with Session() as client:
                with client.request(method=self.method, url=self.url, headers=self.headers, params=self.params,
                                    data=self.data,
                                    proxies=self.proxy, timeout=self.timeout) as rs:
                    return rs.text
        except Exception as e:
            return str(e)


if __name__ == '__main__':
    url = "https://www.baidu.com"
    p = Req(url=url)
    print(p)
