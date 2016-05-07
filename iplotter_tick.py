import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
from traders import *
from strategist import *

ip=None
st=None


class IPlot:
    def __init__(self,stock=None,num_axes=4):
        self.date='2016-05-05'
        #import ipdb; ipdb.set_trace()
        self.strat=None
        self.stock=stock
        self.num_axes=num_axes
        if stock is not None: self.set_stock(stock)
        self.setup()
    #one time call creates axes   
    def reset_trades(self):
        self.buy_signals=None
        self.sell_signals=None
        self.buys=None
        self.sells=None  
    def _get_stock(self,stock):
        self.df=load_sec_from_ts_tick(stock,self.date)
        #connect_db('day_stock.db')
        #self.df=load_sec_from_db_date(stock,self.start,self.end)

        if self.df is None: return
        self.fig.suptitle(str(stock),fontsize=10)
        self.reset_trades()

        #fill some indicators that you want for all strategies
        self.df=fill_df_MACD_ratio(self.df)
        self.df=fill_df_KDJ(self.df)


    def setup(self):
        #plt.ion()
        self.axes,self.fig=make_axes(5)
        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.98, top=0.98, wspace=0, hspace=0)
    

    def set_strat(self,strat):
        #before aassigning a new strategist
        #clear drawn graphics and disconnect events
        if self.strat is not None:
            self.strat.remove()
            self.fig.canvas.mpl_disconnect(self.strat_cid)

        #assign a new strategist
        strat.set_plotter(self)
        strat.set_data(self.df)
        self.strat_cid=self.fig.canvas.mpl_connect('key_press_event', strat.key_press)
        self.strat=strat
        self.run()

    def clear_axes(self,nums=[0,1]):
        axes=self.axes
        for i in nums:
            axes[i].lines=axes[i].lines[:1]
            axes[i].collections=[]


    def plot(self):
        if self.df is None: 
            print('no data')
            return
        axes=self.axes
        df=self.df

        self.clear_axes([0,1,2])   
        plot_price(axes[0],df)
        plot_MACD(axes[1],df)
        plot_KDJ(axes[2],df)

        if self.buy_signals is None: self.buy_signals=self.axes[0].plot([],'o',color='#ffaaaa')
        if self.sell_signals is None: self.sell_signals=self.axes[0].plot([],'o',color='#aaffaa')
        if self.buys is None: self.buys=self.axes[0].plot([],'o',color='r',ms=20,alpha=0.3,mew=0)
        if self.sells is None: self.sells=self.axes[0].plot([],'o',color='g',ms=20,alpha=0.3,mew=0)

        if self.strat is not None:
            self.strat.plot()


    def set_stock(self,stock,start=None,end=None):
        if start is not None:self.start=start
        if end is not None:self.end=end
        self._get_stock(stock)
        if self.df is None:return
        self.stock=stock
        if self.strat is not None:
            self.set_strat(self.strat)
            self.run()
        plt.draw()
        self.plot()

    #this method let the strategist evaluate data at each tick
    def run(self):
        if self.strat is None: 
            print('please assign a strategist')
            return
        for i in range(35,len(self.df.index)):
            self.strat.evaluate(i)

        if len(self.strat.trades)>0:
            rate=0
            for t in self.strat.trades:
                rate+=t.profit_rate*100
            rate/=len(self.strat.trades)
            self.fig.suptitle(self.stock+" total rate=%-3.1f%%"%rate)


if __name__ == '__main__':
    ip=IPlot()
    stock=ip.set_stock
  
    #stock('000728')
    stock('600006')
    strat=ip.set_strat
    #st=Stg_ma()
    st=Stg_reverse_short()
    strat(st)
    st.update(10,20)
    df=ip.df
    plt.show()

    


