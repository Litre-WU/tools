# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: ProxyManager.py
# Time: 7月 29, 2021
import requests
from user_agent import generate_user_agent
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
import socket
import threading
from json import load, dump, loads
from time import sleep
import os

timeout = 10
none_time = 3


def pub_req(**kwargs):
    method = kwargs.get("method", "GET")
    url = kwargs.get("url", "")
    params = kwargs.get("params", {})
    data = kwargs.get("data", {})
    headers = {**{"User-Agent": generate_user_agent()}, **kwargs.get("headers", {})}
    proxy = kwargs.get("proxy", {})
    timeout = kwargs.get("timeout", 5)
    try:
        with requests.Session() as client:
            with client.request(method=method, headers=headers, url=url, params=params, data=data, proxies=proxy,
                                timeout=timeout) as rs:
                if rs.status_code == 200:
                    return rs.text
                else:
                    retry = kwargs.get("retry", 0)
                    retry += 1
                    if retry >= 2:
                        return None
                    kwargs["retry"] = retry
                    return pub_req(**kwargs)
    except Exception as e:
        # print(e)
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 2:
            return None
        kwargs["retry"] = retry
        return pub_req(**kwargs)


def spider(**kwargs):
    # 开心代理
    page = kwargs.get("page", 1)
    kwargs = {
        "url": f'http://www.kxdaili.com/dailiip/1/{page}.html'
    }
    html = pub_req(**kwargs)
    html = etree.HTML(html)
    trs = html.xpath('//table[@class="active"]/tbody/tr')
    if trs:
        return [tr.xpath('td/text()')[:2] for tr in trs]
    # # jiangxianli
    # kwargs = {
    #     "url": 'https://ip.jiangxianli.com/api/proxy_ips',
    #     "params": {"country": "中国",
    #                "page": page}
    # }
    # text = pub_req(**kwargs)
    # text = loads(text)
    # data = text["data"]["data"]
    # if data:
    #     proxies = [[x["ip"], x["port"]] for x in data]
    #     if page == 1:
    #         pages = text["data"]["total"] // text["data"]["per_page"] + 1
    #         with ThreadPoolExecutor(pages - 1) as executor:
    #             futures = [executor.submit(get_ip, **{"page": i}) for i in
    #                        range(2, pages + 1)]
    #             for future in futures:
    #                 if future.result():
    #                     proxies += future.result()
    #         return proxies
    #     return proxies


def check_ip(**kwargs):
    ip = kwargs.get("ip", "127.0.0.1")
    port = kwargs.get("port", 80)
    kwargs = {
        "url": 'http://httpbin.org/get?show_env=1',
        "proxy": {"http": f'http://{ip}:{port}', "https": f'https://{ip}:{port}'},
    }
    text = pub_req(**kwargs)
    if text:
        info = {"ip": ip, "port": port}
        with open('proxy_list.txt', 'a') as f:
            f.write(f'{str(info)}\n')
        return info


def run_spider():
    proxy_list = []
    with ThreadPoolExecutor(10) as executor:
        futures = [executor.submit(spider, **{"page": i}) for i in range(1, 11)]
        for future in futures:
            if future.result():
                proxy_list += future.result()
    if proxy_list:
        with ThreadPoolExecutor(len(proxy_list)) as executor:
            futures = [executor.submit(check_ip, **{"ip": proxy_list[i][0], "port": proxy_list[i][1]}) for i in
                       range(len(proxy_list))]
            proxies = [future.result() for future in futures if future.result()]
            with open('proxy_list.json', 'w') as f:
                dump(proxies, f)
            if proxies:
                return proxies[0]


def get_proxy():
    if not os.path.exists('proxy_list.json'):
        with open('proxy_list.json', 'w') as f:
            dump([], f)
    with open('proxy_list.json', 'r') as f:
        proxy_list = load(f)
    if proxy_list:
        with open('proxy_list.json', 'r') as f:
            proxy_list = load(f)
            proxy = proxy_list.pop()
        with open('proxy_list.json', 'w') as f:
            dump(proxy_list, f)
        return proxy
    else:
        return run_spider()


def t2c(conn, to_px):
    i = 0
    j = 0
    while i < timeout:
        try:
            content = to_px.recv(1024)
            if not content:
                if j > none_time:
                    conn.close()
                    to_px.close()
                    return
                j += 1
            try:
                conn.sendall(content)
            except Exception as e:
                # print("send data to client error")
                pass
        except Exception as e:
            if j > none_time:
                conn.close()
                to_px.close()
                return
            j += 1
            # print("get data from px error")


def c2t(conn, to_px):
    j = 0
    i = 0
    while i < timeout:
        try:
            content = conn.recv(1024)
            if not content:
                if j > none_time:
                    conn.close()
                    to_px.close()
                    return
                j += 1
            try:
                to_px.sendall(content)
            except Exception as e:
                print("send data to px error")
            i += 1
        except Exception as e:
            if j > none_time:
                conn.close()
                to_px.close()
                return
            j += 1


def switch(*args, **kwargs):
    conn, addr = args
    print(f'{addr[0]} 已连接 {kwargs.get("ip","")}:{kwargs.get("port","")}')
    try:
        to_px = socket.socket()
        to_px.connect((kwargs.get("ip", ""), int(kwargs.get("port", ""))))
        threading.Thread(target=c2t, args=(conn, to_px)).start()
        threading.Thread(target=t2c, args=(conn, to_px)).start()
    except Exception as e:
        # print(e)
        print("切换代理...")
        kwargs = get_proxy()
        return switch(*args, **kwargs)


def run():
    sever = socket.socket()
    sever.bind(("0.0.0.0", 1080))
    sever.listen(10)
    print("1080 代理服务已启动!")
    while True:
        try:
            conn, addr = sever.accept()
            kwargs = get_proxy()
            threading.Thread(target=switch, args=(conn, addr), kwargs=kwargs).start()
        except Exception as e:
            print("代理连接错误!")


if __name__ == "__main__":
    run()
