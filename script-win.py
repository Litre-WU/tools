import winreg
import ctypes
from mitmproxy import http, ctx, proxy
import pymongo
from datetime import datetime

INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r'Software\Microsoft\Windows\CurrentVersion\Internet Settings', 0,
                                   winreg.KEY_ALL_ACCESS)

# 设置刷新
INTERNET_OPTION_REFRESH = 37
INTERNET_OPTION_SETTINGS_CHANGED = 39
internet_set_option = ctypes.windll.Wininet.InternetSetOptionW


# 修改键值
def set_key(name, value):
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, name)
    winreg.SetValueEx(INTERNET_SETTINGS, name, 0, reg_type, value)


# 启用代理
def proxy_on(*args):
    ip = args[0] if args else '127.0.0.1:8080'
    set_key('ProxyEnable', 1)  # 启用
    set_key('ProxyOverride', '*.local;<local>')  # 绕过本地
    set_key('ProxyServer', ip)  # 代理IP及端口
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)


# 停用代理
def proxy_off():
    set_key('ProxyEnable', 0)  # 停用
    internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
    internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)


class Joker:
    def __new__(cls, *args, **kwargs):
        proxy_off()
        proxy_on()

    def __init__(self):
        self.ip = ""
        self.pymongo_client = ""
        self.db = self.pymongo_client["data"]

    def clientconnect(self, layer: proxy.protocol.Layer):
        self.ip = layer.client_conn.address[0]

    def request(self, flow: http.HTTPFlow) -> None:
        print(self.ip)
        # ip = '.'.join(str(randint(0, 255)) for _ in range(4))
        # flow.request.headers.update({
        #     # "User-Agent": generate_user_agent(),
        #     # "X-Forwarded-For": ip,
        #     # "X-Real-IP": ip,
        # })

    def response(self, flow: http.HTTPFlow) -> None:
        pass
        # if 'http://rcpu.cwun.org/UnInfo.aspx' == flow.request.url:
        #     print("*" * 10)
        #     text = flow.response.text

    def save_data(self, *args):
        mycol = args[0]
        data_list = args[1]
        data_list = [{**d, **{"collect_time": datetime.now()}} for d in data_list]
        try:
            return mycol.insert_many(data_list).inserted_ids
        except Exception as e:
            # print(e)
            for x in data_list:
                try:
                    mycol.insert_one(x)
                except Exception as e:
                    # print(e)
                    mycol.find_one_and_update({"_id": x["_id"]}, {"$set": x})
        self.pymongo_client.close()

    def __str__(self):
        proxy_off()


addons = [Joker()]

if __name__ == '__main__':
    pass

