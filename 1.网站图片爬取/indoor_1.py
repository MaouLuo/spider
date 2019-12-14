# -*- encoding:utf-8 -*-
"""
@作者：maou
@文件名：indoor_1.py
@时间：2019/12/14
@文档说明:爬虫入门练习系列1，爬取网站为 https://www.ivsky.com/tupian/dongwutupian/
"""

import requests
import threading
import re
import time
from bs4 import BeautifulSoup

# 存放图组列表路径
urls = []

# 存放图组路径
g_urls = []

# 初始化线程锁
g_lock = threading.Lock()


class Spider():
    
	def __init__(self, target_url, headers):
		self.target_url = target_url
		self.headers = headers

	# 获取所有url
	def get_urls(self, start_page, end_page):
		global urls
		for i in range(start_page, end_page+1):
			if i == 1:
				url = 'https://www.ivsky.com/tupian/dongwutupian/'
			else:
				url = self.target_url % i
			urls.append(url)


# 生产者，从每个列表页提取图组路径
class Producer(threading.Thread):

	def run(self):
		headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko.20100101 Firefox/52.0' , 
				'HOST' : 'www.ivsky.com'}
		global urls
		while len(urls) > 0 :
			g_lock.acquire() # 上锁
			page_url = urls.pop()
			g_lock.release() # 解锁

			try:
				print('分析' + page_url)
				resp = requests.get(page_url, headers=headers, timeout=5)
				print(resp.text)

				# re.s 当文本有多行时会作为一行进行正则，否则默认为对单行正则
				# <a href="/tupian/heye_v56613/" title="可爱的猫鼬图片(16张)" target="_blank">
				# <img src="//img.ivsky.com/img/tupian/li/201906/12/Hippopx__7__71591.jpg" alt="可爱的猫鼬图片"></a>
				# all_img_url = re.findall('<a href="(.*?)"> title=".*?" target="_blank"', resp.text, re.S)
				
				# 定位子节点
                children = []
                for c in text:
                    children += c.find_all('a')

                # 获取所有子节点的链接
                for c in children:
                    print(c['href'])

				global g_urls
				g_lock.acquire()
				g_urls += all_img_url
				print(g_urls)
				g_lock.release()
				time.sleep(0.5)
			except:
				pass





if __name__ == '__main__':
	headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko.20100101 Firefox/52.0' , 
				'HOST' : 'www.ivsky.com'}
	target_url = 'https://www.ivsky.com/tupian/dongwutupian/index_%d.html'

	spider = Spider(target_url, headers)
	spider.get_urls(1, 10)
	print(urls)

	for x in range(2):
		t = Producer()
		t.start()

