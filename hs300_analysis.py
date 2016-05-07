import numpy as np
import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from ts_util import *
from strategist import *



class Hs300:
    def __init__(self):
        self.df=ts.get_hist_data('hs300')
        self.df=self.df.sort_index(ascending=True)
        self.df=self.df.reset_index()

        #load hs300 stock list
        self.hsdf=pd.read_csv('hs300.csv')
        print(self.hsdf)
        print(self.hsdf.stock[0][2:])

        self.axes,self.fig=make_axes(2)
        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.98, top=0.98, wspace=0, hspace=0)
      

        self.hs_close=self.axes[0].plot(self.df.close)
        self.marker=self.axes[0].plot(self.df.close[10:100],'o',color='r')
        self.counter=0

        ani=animation.FuncAnimation(self.fig,self.update,1) 
        self.update(0) 
        plt.show()
    def clear_axes(self,nums=[0,1]):
        axes=self.axes
        for i in nums:
            axes[i].lines=axes[i].lines[:1]
            axes[i].collections=[]


    def update(self,frame_number):
        if self.counter<len(self.hsdf.stock):
            self.clear_axes([1])
            df=load_sec_from_ts_date(self.hsdf.stock[self.counter][2:])
            ref=pd.DataFrame(self.df.date)
            df=get_aligned_day_data(ref,df)
            #print(df)
            #df=ts.get_hist_data(self.hsdf[self.counter][2:])
            #df=df.sort_index(ascending=True)
            #df=df.reset_index()
            self.axes[1].plot(df.close)
            #x=self.df.index[:self.counter]
            #y=self.df.close[:self.counter]
            #self.marker[0].set_data(x,y)
            self.counter+=1

def main():
    #plt.ion()
    hs=Hs300()

if __name__ == '__main__':
    main()
