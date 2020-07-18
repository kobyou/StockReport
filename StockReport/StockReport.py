#-*-coding:utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup
import itertools
import io
import sys
import matplotlib.pyplot as plt
import time
import datetime

class StockReport:
    def __init__(self):
        super().__init__()
        self.headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
    
    def get_page(self,url):
        try:
            r=requests.get(url,headers=self.headers)
            #r.raise_for_status()
            #r.encoding=r.apparent_encoding      
            return r.text
        except Exception as e:
            print(e)

    def get_stock_report_list(self,stock_list_url):
        try:
            stock_list=[]
            page=self.get_page(stock_list_url)
            bs=BeautifulSoup(page,'html.parser')

            li=bs.find_all('a',class_="viewzy")
            list =[]
            for i in li:
                line= i.string     
                line=line.lstrip()
                line=line.rstrip()
                line = line[0:line.index(')')+1]
                #print(line)
                list.append(line)
            #print(list)
            return list
        except Exception as e:
            print(e)

    def draw_report_from_dict(slef,dicdata,RANGE, heng=1):
        #dicdata：字典的数据。
        #RANGE：截取显示的字典的长度。
        #heng=0，代表条状图的柱子是竖直向上的。heng=1，代表柱子是横向的。考虑到文字是从左到右的，让柱子横向排列更容易观察坐标轴。
        by_value = sorted(dicdata.items(), key = lambda kv:(kv[1], kv[0]), reverse = True) 
        x = []
        y = []
        ct = time.time()
        local_time = time.localtime(ct)
        t = time.strftime("%Y-%m-%d", local_time)
        fig = plt.figure(figsize=(11,6))
        fig.suptitle('Stock Report(%s)'%t)
        #解决中文显示问题
        plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
        plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
        for d in by_value:
            x.append(d[0])
            y.append(d[1])
        if heng == 0:
            plt.bar(x[0:RANGE], y[0:RANGE])
            plt.show()
            return 
        elif heng == 1:
            plt.barh(x[0:RANGE], y[0:RANGE])
            plt.show()
            return 
        else:
            return "heng的值仅为0或1！"

    def get_stock_report(self):
        stock_list = []
        for i in range(1,10):
            stock_url = r'http://vis.10jqka.com.cn/free/ybzx/index/ctime/-3/pageNum/589/curPage/%d'%i

            list = []
            list=self.get_stock_report_list(stock_url)
            stock_list.extend(list)

        dict = {}
        for s in stock_list:
            dict[s] = dict.get(s, 0) + 1

        self.draw_report_from_dict(dict,25)


stockReport = StockReport()
stockReport.get_stock_report()




