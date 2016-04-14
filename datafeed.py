import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
from traders import *
from strategist import *

class DataFeed():
    def __init__(self):
        self.strategist=[]
        self.strategist=None
        return
    def get_data(self,sec_num,start,end):
        df=load_sec_from_ts_date(sec_num,start,end)
        return df

    def feed(self,draw=True,log=True):
        sec_num_s=600000
        sec_num_e=600001
        start='2015-01-01'
        end='2016-01-01'
        for sec_num in range (sec_num_s,sec_num_e):
            self.feed_one(sec_num,start,end,draw=draw,log=log)


    def feed_one(self,sec_num,start,end,draw=True,log=True):
        df=self.get_data(str(sec_num),start,end)
        if df is None : return
        #self.strategist=Stg_testing(df)
        self.strategist=Stg_tight(df)


        print("evaluating %d"%sec_num)
        for i in range(24,len(df.index)):
            self.strategist.evaluate(i)
        print('done eval')



def main():
    feed=DataFeed()
    #feed.feed()
    feed.feed_one(600006,'2015-01-01','2016-04-01',draw=True,log=True)


    #----------------------------------------------------
    #-----------------  PLOTTING  -----------------------
    #----------------------------------------------------
    draw=False
    draw=True
    print('flag 1-')
    if draw & (feed.strategist is not None):
        print('flag 2')
        df=feed.strategist.df
        bs=feed.strategist.buy_signals
        ss=feed.strategist.sell_signals

        axes=make_axes(5)
        plot_price(axes[0],df)
        plot_MACD(axes[1],df,names=['macds','signals','htgs'])
        plot_MACD(axes[2],df)
        plot_MACD(axes[3],df,names=['macdl','signall','htgl'])
        #plot_MACD(axes[3],df,macd_name_c,color=['#00ff00','#77ff77','#ddffdd'])
        plot_KDJ(axes[4],df)

        
        axes[1].scatter(df.hsu.index,df.hsu,color='r')
        axes[1].scatter(df.hsd.index,df.hsd,color='g')

        #axes[2].scatter(df.htg_uc.index,df.htg_uc,color='r')
        #axes[2].scatter(df.htg_dc.index,df.htg_dc,color='g')
        axes[2].scatter(df.hu.index,df.hu,color='r')
        axes[2].scatter(df.hd.index,df.hd,color='g')

        axes[3].scatter(df.hlu.index,df.hlu,color='r')
        axes[3].scatter(df.hld.index,df.hld,color='g')
        axes[3].scatter(df.mlu.index,df.mlu,color='r')
        axes[3].scatter(df.mld.index,df.mld,color='g')

        axes[4].scatter(df.kduc.index,df.kduc,color='r')

        if len(bs)>0: axes[0].scatter(bs.index,bs,color='r')
        if len(ss)>0: axes[0].scatter(ss.index,ss,color='g')

        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.98, top=0.98, wspace=0, hspace=0)
        plt.show()

if __name__ == '__main__':
    main()


