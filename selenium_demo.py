import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from user_agent import generate_user_agent
import time
import sys
sys.setrecursionlimit(3000)  # 将默认的递归深度修改为3000


async def main():
    proxies = 'http://127.0.0.1:8080'
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--proxy-server={proxies}")
    chrome_options.add_argument(f'user-agent={generate_user_agent()}')
    # chrome = webdriver.Chrome(options=chrome_options)
    chrome = webdriver.Chrome(options=chrome_options, executable_path='chromedriver.exe')
    chrome.implicitly_wait(20)
    url = 'http://rcpu.cwun.org/PERInfo.aspx'
    chrome.get(url=url)
    await change_page(chrome, 1)


async def change_page(chrome, num):
    print(num)
    if num <= 61927:
        page = chrome.find_element_by_id('ctl00$ContentPlaceHolder1$AspNetPager1_input')
        page.clear()
        page.send_keys(num)
        page.send_keys(Keys.ENTER)
        time.sleep(2)
        return await change_page(chrome, num + 1)
    else:
        chrome.close()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
