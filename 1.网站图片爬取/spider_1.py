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


class Spider():
    
    def __init__(self, target_url, headers, start_page=1, end_page=1, Debug=False):
        self.target_url = target_url
        self.headers = headers
        if start_page > end_page:
            raise ValueError('end_page must be greater than or equal to start_page')
        self.start_page = start_page
        self.end_page = end_page
        #self.urls = []
        self.group_urls = {}
        self.Debug = Debug


    # 获取单页中所有图组路径
    def get_urls(self):
        urls = []
        for i in range(self.start_page, self.end_page+1):
            if i == 1:
                url = 'https://www.ivsky.com/tupian/dongwutupian/'
            else:
                url = self.target_url % i # 将页数补入链接中
            urls.append(url)

        while len(urls) > 0:
            page_url = urls.pop()
            resp = requests.get(page_url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(resp.text, 'lxml')

            # 先定位含图组路径父节点
            father = soup.find_all('div', attrs={'class':'il_img'})

            # 定位二级节点
            tags = []
            for children in father:
                tags += children.find_all('a')

            # 获取所有二级节点的链接
            for tag in tags:
                #print(link['href'])
                #self.group_urls.append(tag['href'])
                self.group_urls[tag['title']] = tag['href']

            print('已获取所有图组url')


    # 获取一图组内所有图片路径
    def get_img(self):
        head_url = 'https://www.ivsky.com/'
        while len(self.group_urls) > 0:
            group_name, group_url = self.group_urls.popitem()
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
            #print(c_tags)

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
            time.sleep(3*(random.random()))
        print('所有图片全下载完成')


    # 下载图片
    def download(self, folder, urls): 
        # 图组名
        path = 'F:\\code\\img\\' + folder
        if os.path.exists(path): # 判断文件夹是否存在
            print('文件夹已存在')
            return
        else:
            os.mkdir(path) # 创建文件夹

        for url in urls:            
            pattern = r'https://img.ivsky.com/img/tupian/pre/\d*?/\d*?/(.*?)$'
            name = re.findall(pattern, url)[0]

            # 将远程数据下载到本地，第二个参数就是要保存到本地的文件名.py2不加.request
            urllib.request.urlretrieve(url, path+'\\'+name)
            time.sleep(random.random())
        print('{0}下载完成'.format(folder))


    # 爬虫主函数
    def run(self):
        if self.Debug:
            print('0')
        #self.get_page_urls()
        if self.Debug:
            print('1')
        self.get_urls()
        if self.Debug:
            print('2')
        self.get_img()


def main():
    Debug = True
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    target_url = 'https://www.ivsky.com/tupian/dongwutupian/index_%d.html'
    spider = Spider(target_url, headers, 1, 1, Debug)
    #print('zz')
    st = time.time()
    spider.run()
    et = time.time()
    print('times:{:.2f}'.format(et-st))

if __name__ == '__main__':
    main()



