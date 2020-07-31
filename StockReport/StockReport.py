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
import mplfinance as mpf
import matplotlib as mpl# 用于设置曲线参数
from cycler import cycler# 用于定制线条颜色
import pandas as pd# 导入DataFrame数据
import tushare as ts


class StockReport(object):
    def __init__(self,range=10,showline=True):
        super().__init__()
        self.token = '5e67f5dc948cd6e6b616ed0265e55f0b8db58c0bfb951272e7e2e50f'
        self.headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"}
        # self.startdate = '2018-01-01'
        # self.enddate = time.strftime("%Y%m%d", time.localtime())
        self.stockRange = range
        #300 days。
        now=datetime.datetime.now()
        delta=datetime.timedelta(days=360)
        n_days=now-delta      
        self.enddate = now.strftime('%Y%m%d')
        self.startdate = n_days.strftime('%Y%m%d')
        self.showLine = showline
        #print (self.startdate)

        if not os.path.exists("./report"):
            os.mkdir("./report")
        
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

    def draw_report_from_dict(self,dicdata,RANGE, heng=1):
        #dicdata：字典的数据。
        #RANGE：截取显示的字典的长度。
        #heng=0，代表条状图的柱子是竖直向上的。heng=1，代表柱子是横向的。考虑到文字是从左到右的，让柱子横向排列更容易观察坐标轴。
        #by_value = sorted(dicdata.items(), key = lambda kv:(kv[1], kv[0]), reverse = True) 
        try:
            x = []
            y = []
            ct = time.time()
            local_time = time.localtime(ct)
            t = time.strftime("%Y-%m-%d", local_time)
            fig = plt.figure(figsize=(10,5))
            fig.suptitle('Stock Report(%s)'%t)
            #解决中文显示问题
            #plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
            #plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
            for d in dicdata:
                x.append(d[0])
                y.append(d[1])
            if heng == 0:
                plt.bar(x[0:RANGE], y[0:RANGE])
                plt.rcParams['font.sans-serif'] = ['FangSong', 'KaiTi']
                plt.savefig('./report/Stock Report(%s).jpg'%t)
                #plt.show()
                return 
            elif heng == 1:
                plt.barh(x[0:RANGE], y[0:RANGE])
                plt.rcParams['font.sans-serif'] = ['FangSong', 'KaiTi']
                plt.savefig('./report/Stock Report(%s).jpg'%t)
                #plt.show()
                return 
            else:
                return "heng的值仅为0或1！"
        except Exception as e:
            print(e)

    def show_stock_report(self,Range):
        try:
            stock_list = []
            for i in range(1,10):
                stock_url = r'http://vis.10jqka.com.cn/free/ybzx/index/ctime/-3/pageNum/589/curPage/%d'%i

                list = []
                list=self.get_stock_report_list(stock_url)
                stock_list.extend(list)

            dict = {}
            for s in stock_list:
                dict[s] = dict.get(s, 0) + 1

            dicdata = sorted(dict.items(), key = lambda kv:(kv[1], kv[0]), reverse = True) 
            print(dicdata)
            self.draw_report_from_dict(dicdata,Range)
            #print(dicdata)
            return dicdata
        except Exception as e:
            print(e)

    def get_daily_data(self,stock_code):
        try:
            ts.set_token(self.token)
            pro = ts.pro_api()
            #out = pro.daily(ts_code=stock_code, start_date = self.startdate, end_date = self.enddate)
            out = ts.pro_bar(ts_code =stock_code, start_date = self.startdate, end_date = self.enddate, adj='qfq') #需要权限
            daily_data = out.sort_values(by=['trade_date'])
            daily_data.reset_index(level=0,inplace=True)
            daily_data.drop(['index'],axis=1,inplace=True)
            #print(daily_data)
            return daily_data
        except Exception as e:
            print(e)

    def import_ts_data(self,stock_code):
        try:
            ts_data = self.get_daily_data(stock_code)
                
            pd.set_option('display.max_rows', None)
            df=pd.DataFrame(data=ts_data)   
            # 格式化列名，用于之后的绘制
            df.rename(
                    columns={
                    'trade_date': 'Date', 'open': 'Open', 
                    'high': 'High', 'low': 'Low', 
                    'close': 'Close', 'vol': 'Volume'}, 
                    inplace=True)
            # 转换为日期格式
            df['Date'] = pd.to_datetime(df['Date'])
            # 将日期列作为行索引
            df.set_index(['Date'], inplace=True)
            #print(df)
            return df
        except Exception as e:
            print(e)
    
    def import_csv(self,stock_code):
        # 导入股票数据      
        df = pd.read_csv(stock_code + '.csv')
        # 格式化列名，用于之后的绘制
        df.rename(
                columns={
                'date': 'Date', 'open': 'Open', 
                'high': 'High', 'low': 'Low', 
                'close': 'Close', 'volume': 'Volume'}, 
                inplace=True)
        # 转换为日期格式
        df['Date'] = pd.to_datetime(df['Date'])
        # 将日期列作为行索引
        df.set_index(['Date'], inplace=True)
        return df

    def parse_stock_code(self,stock_str):
        line = stock_str[stock_str.index('(')+1:stock_str.index(')')]
        if line[0] == '6':
            stock_code = line+'.SH'      
            pass
        else:
            stock_code = line+'.SZ'
            pass
        return stock_code

    def draw_k_line(self,stock_str):
        try:
        # 导入数据
            symbol = self.parse_stock_code(stock_str)
            period = 500
            #df = self.import_csv(symbol)[-period:]
            df = self.import_ts_data(symbol)[-period:]
            # 设置基本参数
            # type:绘制图形的类型，有candle, renko, ohlc, line等
            # 此处选择candle,即K线图
            # mav(moving average):均线类型,此处设置7,30,60日线
            # volume:布尔类型，设置是否显示成交量，默认False
            # title:设置标题
            # y_label:设置纵轴主标题
            # y_label_lower:设置成交量图一栏的标题
            # figratio:设置图形纵横比
            # figscale:设置图形尺寸(数值越大图像质量越高)
            kwargs = dict(
                type='candle', 
                mav=(7, 30, 60), 
                volume=True, 
                title='\nA_stock %s candle_line' % (stock_str),    
                ylabel='OHLC Candles', 
                ylabel_lower='Shares\nTraded Volume', 
                figratio=(15, 10), 
                figscale=1.1)
            
            # 设置marketcolors
            # up:设置K线线柱颜色，up意为收盘价大于等于开盘价
            # down:与up相反，这样设置与国内K线颜色标准相符
            # edge:K线线柱边缘颜色(i代表继承自up和down的颜色)，下同。详见官方文档)
            # wick:灯芯(上下影线)颜色
            # volume:成交量直方图的颜色
            # inherit:是否继承，选填
            mc = mpf.make_marketcolors(
                up='red', 
                down='green', 
                edge='i', 
                wick='i', 
                volume='in', 
                inherit=True)
                
            # 设置图形风格
            # gridaxis:设置网格线位置
            # gridstyle:设置网格线线型
            # y_on_right:设置y轴位置是否在右
            s = mpf.make_mpf_style(
                gridaxis='both', 
                gridstyle='-.', 
                y_on_right=False, 
                marketcolors=mc)
                
            # 设置均线颜色，配色表可见下图
            # 建议设置较深的颜色且与红色、绿色形成对比
            # 此处设置七条均线的颜色，也可应用默认设置
            mpl.rcParams['axes.prop_cycle'] = cycler(
                color=['dodgerblue', 'deeppink', 
                'navy', 'teal', 'maroon', 'darkorange', 
                'indigo'])
            
            # 设置线宽
            mpl.rcParams['lines.linewidth'] = .5
        
            # 图形绘制
            # show_nontrading:是否显示非交易日，默认False
            # savefig:导出图片，填写文件名及后缀
            # mpf.plot(df, 
            #     **kwargs, 
            #     style=s, 
            #     show_nontrading=False,
            #     savefig='A_stock-%s %s_candle_line'
            #     % (symbol, period) + '.jpg',
            #     block = False)
            mpf.plot(df, 
                **kwargs, 
                style=s, 
                show_nontrading=False,
                block = False)
            plt.rcParams['font.sans-serif'] = ['FangSong', 'KaiTi']  
            plt.savefig('./report/A_stock-%s %s_candle_line.jpg'% (stock_str, period))
        except Exception as e:
            print(e)
        #     % (symbol, period))     
        #plt.show()

    def run(self):
        try:
            stock_code = '上汽集团(600104)'
            self.draw_k_line(stock_code)
            dicdata = self.show_stock_report(self.stockRange)
            if self.showLine == True:
                for i in range(0,self.stockRange):
                    #stock_tup = dicdata[0]
                    stock_code = dicdata[i][0]
                    self.draw_k_line(stock_code)
            plt.show()
        except Exception as e:
            print(e)
 
if __name__ == "__main__":
    pass
    stock_range = 20
    show_line = 1
    stockReport = StockReport(stock_range,show_line) 
    stockReport.run()
    