import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
from traders import *
from strategist import *

GROUP1=['600000','600007']

total_rate=0
counter=0

class DataFeed():
    def __init__(self):
        self.strategist=[]
        self.strategist=None
        return
    def get_data(self,sec_num,start,end):
        df=load_sec_from_ts_date(sec_num,start,end)
        return df

    def feed(self,draw=False,log=False,save=True):
        sec_num_s=600000
        sec_num_e=604000
        start='2015-01-01'
        end='2016-01-01'
        global counter,total_rate
        for sec_num in range (sec_num_s,sec_num_e):
            r=self.feed_one(sec_num,start,end,draw=draw,log=log,save=save)
            if r is not None:
                counter+=1
                total_rate+=r
                ar=total_rate/counter
                print(ar)


    def feed_one(self,sec_num,start,end,draw=True,log=True,save=False):
        df=self.get_data(str(sec_num),start,end)
        if df is None : return
        #self.strategist=Stg_ma(df)
        self.strategist=Stg_testing(df)
        #self.strategist=Stg_macdlfc_reverse(df)
        #self.strategist=Stg_tight(df)
        #self.strategist=Stg_normal_macdl(df,[-0.75,0.75],-0.1)
        #self.strategist.take_risk=False
        #self.strategist=Stg_macd_slope(df)


        #print("evaluating %d"%sec_num)
        for i in range(24,len(df.index)):
            self.strategist.evaluate(i)
        #print('done eval')

        if len(self.strategist.trades)>0:
            tcost=0
            tprofit=0
            for i in self.strategist.trades:
                tprofit+=i.profit
                tcost+=i.bought
            rate=tprofit/tcost
            rate*=100
            print("%s total %2d trades, return rate=%3.2f%%"%(str(sec_num),len(self.strategist.trades),rate))
            self.plot_to_save(self.strategist,"%.1f%%"%rate)
            return rate 
    def plot_to_save(self,strat,sufix):
        df=strat.df
        bs=strat.buy_signals
        ss=strat.sell_signals
        bss=strat.buys
        sss=strat.sells

        axes,fig=make_axes(5)
        plot_price(axes[0],df)
        plot_MACD(axes[1],df,names=['macds','signals','htgs'])
        plot_MACD(axes[2],df)
        plot_MACD(axes[3],df,names=['macdl','signall','htgl'])
        plot_MACD(axes[4],df,names=['macdln','signalln','htgln'])
        #plot_MACD(axes[3],df,macd_name_c,color=['#00ff00','#77ff77','#ddffdd'])
        #plot_KDJ(axes[4],df)

        
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

        #axes[4].scatter(df.kduc.index,df.kduc,color='r')

        if len(bs)>0: axes[0].scatter(bs.index,bs,color='r')
        if len(ss)>0: axes[0].scatter(ss.index,ss,color='g')
        if len(bss)>0: axes[0].scatter(bss.index,bss,color='r',s=250,alpha=0.3)
        if len(sss)>0: axes[0].scatter(sss.index,sss,color='g',s=250,alpha=0.3)

        #plot std
        std=pd.stats.moments.rolling_std(df.macdln,32)
        #cmax=std.max()
        #cmin=std.min()
        #scalep=abs(1/cmax)
        #scalen=abs(1/cmin)
        #std_macdln=df.macdln.map(lambda x: x*scalep if x>0 else x*scalen)
        #std_macdln.plot(ax=axes[4],color='#aaaaaa')
        std.plot(ax=axes[4],color='#aaaaaa')
        unkonw1=(df.macdln*df.macdln)/(std)
        unkonw1=get_normalized_series(unkonw1)

        unkonw2=(df.macdln)/(std*std)
        unkonw2=get_normalized_series(unkonw2)



        unkonw3=df.macdln-std
        unkonw3=get_normalized_series(unkonw3)

        #unkonw1.plot(ax=axes[4],color='#aaaaff')
        #unkonw2.plot(ax=axes[4],color='yellow')
        #unkonw3.plot(ax=axes[4],color='red')
        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.98, top=0.98, wspace=0, hspace=0)
        filename='../img/'+str(df.sec_num[0])+'_'+str(df.date[0])+'_'+str(df.date[len(df.date)-1])+'_'+sufix+'.png'
        fig.savefig(filename)

def main():
    feed=DataFeed()
    #feed.feed()
    #feed.feed_one('600000','2014-01-01','2016-01-01',draw=True,log=True,save=True)
    feed.feed_one('600006','2015-01-01','2016-01-01',draw=True,log=True,save=True)


    #----------------------------------------------------
    #-----------------  PLOTTING  -----------------------
    #----------------------------------------------------
    draw=False
    draw=True
    #print('flag 1-')
    if draw & (feed.strategist is not None):
        df=feed.strategist.df
        bs=feed.strategist.buy_signals
        ss=feed.strategist.sell_signals
        bss=feed.strategist.buys
        sss=feed.strategist.sells

        axes,fig=make_axes(5)
        plot_price(axes[0],df)
        plot_MACD(axes[1],df,names=['macds','signals','htgs'])
        plot_MACD(axes[2],df)
        plot_KDJ(axes[3],df,names=['k','d','j'])

        ssu,ssd=df.ssu,df.ssd
        axes[1].scatter(ssu.index,ssu,color='r')
        axes[1].scatter(ssd.index,ssd,color='g')

        if len(bs)>0: axes[0].scatter(bs.index,bs,color='r')
        if len(ss)>0: axes[0].scatter(ss.index,ss,color='g')
        if len(bss)>0: axes[0].scatter(bss.index,bss,color='r',s=250,alpha=0.3)
        if len(sss)>0: axes[0].scatter(sss.index,sss,color='g',s=250,alpha=0.3)

        feed.strategist.plot(axes)

        #unkonw3.plot(ax=axes[4],color='red')
        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.98, top=0.98, wspace=0, hspace=0)
        plt.show()

if __name__ == '__main__':
    main()


