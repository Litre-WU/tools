import winreg
import ctypes
import requests
import time
from random import randint

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


def get_proxy(**kwargs):
    proxyusernm = "litreW"  # 代理帐号
    proxypasswd = "Devil2233"  # 代理密码

    url = 'http://litrew.v4.dailiyun.com/query.txt?key=NPAC4DC26C&word=&count=1&rand=true&ltime=10&norepeat=true&detail=true'
    ip = '120.236.115.197'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        "X-Forwarded-For": ip,
        "X-Real-IP": ip,
    }
    try:
        with requests.Session() as client:
            with client.get(url=url, headers=headers) as rs:
                if rs.status_code == 200:
                    # print(rs.text)
                    ip = rs.text.split(',')[0]
                    if ip:
                        return ip
                        # return f'http://{proxyusernm}:{proxypasswd}@{ip}'
                else:
                    time.sleep(randint(1, 2))
                    retry = kwargs.get("retry", 0)
                    retry += 1
                    if retry >= 3:
                        return None
                    kwargs["retry"] = retry
                    return get_proxy(**kwargs)
    except Exception as e:
        print(e)
        time.sleep(randint(1, 2))
        retry = kwargs.get("retry", 0)
        retry += 1
        if retry >= 3:
            return None
        kwargs["retry"] = retry
        return get_proxy(**kwargs)


def clock_switch(*args):
    t = args[0] if args else 10
    while True:
        proxy_off()
        ip = get_proxy()
        print(ip)
        proxy_on(ip)
        time.sleep(t)


if __name__ == '__main__':
    # proxy_on('106.45.105.178:57114')
    # proxy_off()
    clock_switch()

