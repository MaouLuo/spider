# -*- encoding:utf-8 -*-
"""
@作者：maou
@文件名：indoor_1.py
@时间：2019/12/14
@文档说明:爬虫入门练习系列1，爬取网站为 https://www.ivsky.com/tupian/dongwutupian/
单线程爬取少量图片
"""

import requests
import threading
import re
import time
from bs4 import BeautifulSoup
import urllib
import os
import random
import threading


# 所要抓取的页面路径
urls = []

# 所要抓取的图组路径
group_urls = {}

# 线程锁
threadLock = threading.Lock()


class Spider(threading.Thread):    
    def __init__(self, target_url, headers, start_page=1, end_page=1, Debug=False, threadId=0, mode='get_urls'):
        threading.Thread.__init__(self)
        self.target_url = target_url
        self.headers = headers
        if start_page > end_page:
            raise ValueError('end_page must be greater than or equal to start_page')
        self.start_page = start_page
        self.end_page = end_page        
        self.Debug = Debug
        self.threadId = threadId
        self.mode = mode


    # 线程创建提示
    def born(self):
        print('thread {} was born.'.format(self.threadId))


    # 线程结束提示
    def leave(self):
        print('thread {} is leaving.'.format(self.threadId))


    # 获取所有要抓取的页面路径
    def get_page_urls(self):
        global urls
        for i in range(self.start_page, self.end_page+1):
            if i == 1:
                url = 'https://www.ivsky.com/tupian/dongwutupian/'
            else:
                url = self.target_url % i # 将页数补入链接中
            urls.append(url)
        print('已获取所要抓取页面地址')
        #print(self.urls)


    # 获取单页中所有图组路径
    def get_urls(self):
        while True:            
            # 获取锁，用于线程同步
            threadLock.acquire()
            if len(urls) > 0:
                #print('线程{}开始获取图组url'.format(self.threadId))
                page_url = urls.pop()
                threadLock.release()  # 释放锁，开启下一个线程
            else:
                threadLock.release()
                self.leave()
                return
            resp = requests.get(page_url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'lxml')

            # 先定位含图组路径父节点
            father = soup.find_all('div', attrs={'class':'il_img'})

            # 定位二级节点
            tags = []
            for children in father:
                tags += children.find_all('a')

            # 获取所有二级节点的链接
            global group_urls
            for tag in tags:
                threadLock.acquire()
                group_urls[tag['title']] = tag['href']  
                threadLock.release()



    # 获取一图组内所有图片路径
    def get_img(self):
        head_url = 'https://www.ivsky.com/'
        while True:
            threadLock.acquire()
            if len(group_urls) > 0:
                group_name, group_url = group_urls.popitem()
                threadLock.release()
            else:
                threadLock.release()
                self.leave()
                return
            print('开始处理{0}'.format(group_name))
            resp = requests.get(head_url+group_url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'lxml')

            # 先定位含图组路径父节点
            father = soup.find_all('div', attrs={'class':'il_img'})

            # 定位二级点
            tags = []
            for children in father:
                tags += children.find_all('a')

            # 定位三级节点
            c_tags = []
            for tag in tags:
                c_tags += tag.find_all('img')

            # 获取所有图片的链接
            thumb_urls = [] # 缩略图
            for tag in c_tags:
                #print(link['href'])
                thumb_urls.append(tag['src'])

            #该链接下为缩略图，链接转化为大图链接
            # 缩略图  //img.ivsky.com/img/tupian/t/201906/18/juzuiniao.jpg
            # 大图  //img.ivsky.com/img/tupian/pre/201906/18/juzuiniao.jpg
            img_urls = []
            for url in thumb_urls:
                head = 'https://img.ivsky.com/img/tupian/pre/'
                tail = re.findall(r'//img.ivsky.com/img/tupian/t/(.*?).jpg', url)
                img_url = head + tail[0] + '.jpg'
                img_urls.append(img_url)
            self.download(group_name, img_urls)
            time.sleep(5 * (random.random() + 1))


    # 下载图片
    def download(self, folder, urls): 
        # 图组名
        path = 'F:\\code\\img\\' + folder
        if os.path.exists(path): # 判断文件夹是否存在
            print('{}文件夹已存在'.format(folder))
            return
        else:
            os.mkdir(path) # 创建文件夹

        for url in urls:            
            pattern = r'https://img.ivsky.com/img/tupian/pre/\d*?/\d*?/(.*?)$'
            name = re.findall(pattern, url)[0]

            # 将远程数据下载到本地，第二个参数就是要保存到本地的文件名.py2不加.request
            urllib.request.urlretrieve(url, path+'\\'+name)
            time.sleep(random.random() + 1)
        print('{0}下载完成'.format(folder))


    # 爬虫主函数
    def run(self):
        self.born()
        if self.mode == 'get_urls':
            if self.Debug:
                print('1')
            self.get_urls()
        elif self.mode == 'get_imgs':
            if self.Debug:
                print('2')
            self.get_img()
        else:
            print('thread {} mode error')


def main():
    Debug = True
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    target_url = 'https://www.ivsky.com/tupian/dongwutupian/index_%d.html'
    threads = []

    st = time.time()

    for i in range(1, 3):
        t = Spider(target_url, headers, threadId=i, mode='get_urls')
        if i == 1:
            t.get_page_urls()
        t.start()
        # t.join() # 调用join后主线程会暂停，等待该线程结束
        threads.append(t)
    for t in threads:
        t.join()

    threads.clear()

    for i in range(3, 8):
        t = Spider(target_url, headers, threadId=i, mode='get_imgs')  
        t.start()              
        threads.append(t)
    for t in threads:
        t.join()

    et = time.time()
    print('times:{:.2f}'.format(et-st))


if __name__ == '__main__':
    main()



