# coding=utf-8
# 作者      : WU
# 创建时间   : 2019/7/29
# 文件名    : 协程
# IDE      : PyCharm
import asyncio


async def test1():
	rs = {
		"code": 200,
		"msg": "测试1"
	}
	return rs


async def test2():
	rs = await test1()
	rs.update({"result": "测试数据"})
	print(rs)
	return rs


# loop = asyncio.get_event_loop()
# tasks = [asyncio.ensure_future(test2())]
# loop.run_until_complete(asyncio.wait(tasks))
# print(tasks[0].result())
# loop.close()

# import gevent
# from gevent import monkey
#
# monkey.patch_all()
#
#
# def test3(n):
# 	print(n)
# 	return n
#
#
# gevent.joinall([gevent.spawn(test3, 6)])

import requests


async def request():
	url = 'https://www.baidu.com'
	status = requests.get(url)
	return status


def callback(task):
	print('Status:', task.result())


# task = asyncio.ensure_future(request())
# task.add_done_callback(callback)
# print('Task:', task)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(task)
# print('Task:', task)


# from concurrent.futures import ThreadPoolExecutor
# import requests
# from bs4 import BeautifulSoup
#
#
# def get_title(i):
# 	url = 'https://movie.douban.com/top250?start={}&filter='.format(i * 25)
# 	r = requests.get(url)
# 	soup = BeautifulSoup(r.content, 'html.parser')
# 	lis = soup.find('ol', class_='grid_view').find_all('li')
# 	for li in lis:
# 		title = li.find('span', class_="title").text
# 		print(title)
#
#
# async def main():
# 	with ThreadPoolExecutor(max_workers=10) as executor:
# 		loop = asyncio.get_event_loop()
# 		futures = [loop.run_in_executor(executor, get_title, i) for i in range(10)]
# 		for _ in await asyncio.gather(*futures):
# 			pass
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())


