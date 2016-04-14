import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
from traders import *

class StrategistBase:
    def __init__(self,df):
        self.df=df
        self.nearest_index=None
        self.fill_data()
        self.buy_signals=pd.Series()
        self.sell_signals=pd.Series()
        return
    def fill_data(self):
        #fill data frame
        df=self.df
        df=fill_df_MACD_ratio(df)
        df=fill_df_MACD_ratio(df,params=[6,8,4],names=['macds','signals','htgs'])
        df=fill_df_MACD_ratio(df,params=[24,32,18],names=['macdl','signall','htgl'])
        df=fill_df_KDJ(df)

        df=fill_df_reverse(df,df.macd,'mu','md')
        df=fill_df_reverse(df,df.macds,'msu','msd')
        df=fill_df_reverse(df,df.macdl,'mlu','mld')
        df['mc']=df.macd-df.macd.shift()
        df['msc']=df.macds-df.macds.shift()
        df['mlc']=df.macdl-df.macdl.shift()

        df=fill_df_reverse(df,df.signal,'su','sd')
        df=fill_df_reverse(df,df.signals,'ssu','ssd')
        df=fill_df_reverse(df,df.signall,'slu','sld')

        df=fill_df_reverse(df,df.htg,'hu','hd')
        df=fill_df_reverse(df,df.htgs,'hsu','hsd')
        df=fill_df_reverse(df,df.htgl,'hlu','hld')
        df['hc']=df.htg-df.htg.shift()
        df['hsc']=df.htgs-df.htgs.shift()
        df['hlc']=df.htgl-df.htgl.shift()

        df['sc']=df.signal-df.signal.shift()
        df['ssc']=df.signals-df.signals.shift()
        df['slc']=df.signall-df.signall.shift()

        df=fill_df_cross_zero(df,df.htg,'huc','hdc')
        df=fill_df_cross_zero(df,df.htgs,'hsuc','hsdc')
        df=fill_df_cross_zero(df,df.htgl,'hluc','hldc')


        df=fill_df_reverse(df,df.KDJ_J,'ju','jd')
        df['kc']=df.KDJ_K-df.KDJ_K.shift()
        df['dc']=df.KDJ_D-df.KDJ_D.shift()
        df['jc']=df.KDJ_J-df.KDJ_J.shift()
        kduc,kddc=find_KD_cross(df)
        df['kduc']=kduc
        df['kddc']=kddc
        self.df=df
        print('flag 1')
    def get_nearest_index(self,i):
        df=self.df
        #n=pd.DataFrame()
        n={}
        #names=['mu','md','msu','msd','mlu','mld','su','sd','ssu','ssd','slu','sld','hu','hd','hsu','hsd','hlu','hld','huc','hdc','hsuc','hsdc','hluc','hldc']
        names=['mlu','mld','kduc','kddc','hu','hd','hdc','huc','hsu','hsd','hsuc','hsdc','hsd','hlu','hld','jd']
        for name in names:
            se=df[name]
            se=se.dropna()
            adji,trash=get_adjacent_index(i,se.index)
            n[name]=adji


        self.nearest_index=n
        return n

    def evaluate(self,i):
        if self.df is None: return
        self.get_nearest_index(i)

class Stg_testing(StrategistBase):
    def __init__(self,df):
        super().__init__(df)
    def evaluate(self,i):
        super().evaluate(i)
        df=self.df
        n=self.nearest_index
        #print("kduc=",n['kduc'],"i=",i," hu=",n['hu'])

        #print('n.hu=',n.hu)
        kdj_thr_u=35
        if df.macd[i]>1.5: kdj_thr_u=65

        con1=(i-n['hsuc'])<1
        con1&=((i-n['kduc'])<1) & (df.KDJ_D[i]<kdj_thr_u)
        con1&=df.htgs[i]<0.2


        if con1:
            #print(i-n['kduc'])
            self.buy_signals.set_value(i,df.close[i])


        con1=(i-n['hsdc'])<1
        con1&=((i-n['kddc'])<3) #& (df.kduc[i]>50)

        con2=(i-n['hsd'])<1
        con2&=df.KDJ_D[i]>68
        
        con_dip=((i-n['kddc'])<1) & ((i-n['kduc'])<3)
        #con1&=df.hu[i]>-0.2

        con3=(i-n['hsd'])<1
        con3&=(i-n['huc'])>4
        con3&=(df.KDJ_D[i]<70) & (df.kc[i]<0) & (df.jc[i]<df.kc[i])


        if con3 or con_dip:#or con2:
            self.sell_signals.set_value(i,df.close[i])
class Stg_tight(StrategistBase):
    def __init__(self,df):
        super().__init__(df)
        self.mlu=0
    def evaluate(self,i):
        super().evaluate(i)
        df=self.df
        n=self.nearest_index

        #///////////////////////////////////////////
        #////////// LOOK FOR BUY SIGNALS ///////////
        #///////////////////////////////////////////
        #prevent=(i-n['hld'])>4
        prevent=(i-n['hd'])>3
        prevent&=(i-n['hsd'])>1



        con1=(i-n['hsu'])<1
        con1&=df.htgs[i]<0
        con1&=df.macds[i]<0
        con1&=df.macd[i]<0
        con1&=abs(df.jc[i]-df.jc[i-1])<26 #prevent suddent change 
        con1&=df.KDJ_D[i]<60
        #-----prevent too close to dn
        con1&=prevent


        #macds dip
        con2=(i-n['hsu'])<1
        con2&=df.close[i-2]>df.close[i]
        con2&=(i-n['hsd'])>5
        con2&=abs(df.jc[i]-df.jc[i-1])<26 #prevent suddent change 
        con2&=prevent

        #historical low for macd long
        con3=((i-n['hlu'])<1)
        con3&=df.htgl[i]<self.mlu
        con3&=df.htgl[i]<0
        con3&=((i-n['hld'])>10)
        con3&=df.KDJ_J[i]<60

        if ((i-n['hlu'])<1):self.mlu=df.htgl[i]

        #if con3:
        if con1 or con2:
            #print(i-n['kduc'])
            self.buy_signals.set_value(i,df.close[i])
            print('mc:%3.2f'%df.mc[i],'mlc:%3.2f'%df.mlc[i], ' dif%3.2f'%abs(df.jc[i]-df.jc[i-1]))


        #///////////////////////////////////////////
        #////////// LOOK FOR sell SIGNALS //////////
        #///////////////////////////////////////////
        curve=df.htg
        form=get_curve_form(curve,i,test_length=5)
        if curve[i]<curve[i-1]: correct_form=(form=='convex')
        elif curve[i]>curve[i-1]: correct_form=(form=='concave')

        subcon1=True
        downslope=df.slc[i]<0 
        downslope&=(df.signall[i]-df.macdl[i])>0.08
        #ml_sl_almost_cross=
        #if df.htgl[i]-df.htgl[i-1]>=0: downslope=False

        if downslope: subcon1=df.htgl[i]>-0.28
        else: subcon1=df.macdl[i]>1.6

        con1=True
        con1&=(i-n['hsd'])<1
        con1&=subcon1
        #con1&=(i-n['hd'])<1
        #con1&=(i-n['hld'])<1
        #con1&=prevent

        #debuf message
        if i==157:
        #if con1 :
            print('macdl=%4.2f'%(df.macdl[i]),'subcon1=',subcon1,' downslope=',downslope, 'macd dif=',df.signall[i]-df.macdl[i])
            print('n[hsu]=',n['hsu'],' df.hsu=%4.2f'%df.hsu[n['hsu']])
            print('n[hsd]=',n['hsd'],' df.hsd[xxx]=%4.2f'%df.hsd[n['hsd']])
            print('n[hsd]=',n['hsd'],' df.htgs[i]=%4.2f'%df.htgs[i])
            #print(df.hsu)

        if con1 :
            self.sell_signals.set_value(i,df.close[i])
            print('macd dif=',df.signall[i]-df.macdl[i])

