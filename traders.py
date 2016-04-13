import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
class Trader():
    def __init__(self,df):
        self.df=df
        self.htg_up,self.htg_dn=find_reverse(df.htg)
        self.htgl_up,self.htgl_dn=find_reverse(df.htg_l)

        #find valley and peaks for macd
        self.macd_up,self.macd_dn=find_reverse(df.macd)
        self.macds_up,self.macds_dn=find_reverse(df.macd_s)
        self.macdl_up,self.macdl_dn=find_reverse(df.macd_l)
        self.macdc_up,self.macdc_dn=find_reverse(df.macdc)
        self.htgc_up,self.htgc_dn=find_reverse(df.htgc)
        self.htgs_up,self.htgs_dn=find_reverse(df.htg_s)


        #find cross zero values
        self.htg_p_uc,self.htg_p_dc=find_possible_cross_zero(df.htg)
        self.htg_uc,self.htg_dc=find_cross_zero(df.htg)
        self.htgs_uc,self.htgs_dc=find_cross_zero(df.htg_s)
        self.htgl_uc,self.htgl_dc=find_cross_zero(df.htg_l)
        self.htgs_p_uc,self.htgs_p_dc=find_possible_cross_zero(df.htg_s)
        self.htgc_uc,self.htgc_dc=find_reverse(df.htgc)

        self.macd_roc=df.macd-df.macd.shift()
        self.macds_roc=df.macd_s-df.macd_s.shift()
        self.macdl_roc=df.macd_l-df.macd_l.shift()
        self.htg_roc=df.htg-df.htg.shift()

        #find K up corss and down crossD
        self.kdj_uc,self.kdj_dc=find_KD_cross(df)
    def get_feature_index(self,i):
        self.i_htg_up,temp=get_adjacent_index(i,self.htg_up.index)
        self.i_htgl_up,temp=get_adjacent_index(i,self.htgl_up.index)
        self.i_htgs_up,temp=get_adjacent_index(i,self.htgs_up.index)
        self.i_htgs_uc,temp=get_adjacent_index(i,self.htgs_uc.index)
        self.i_htgc_uc,temp=get_adjacent_index(i,self.htgc_uc.index)

        self.i_macd_up,temp=get_adjacent_index(i,self.macd_up.index)
        self.i_macds_up,temp=get_adjacent_index(i,self.macds_up.index)
        self.i_macdl_up,temp=get_adjacent_index(i,self.macdl_up.index)
        self.i_macdc_up,temp=get_adjacent_index(i,self.macdc_up.index)
        self.i_htgc_up,temp=get_adjacent_index(i,self.htgc_up.index)

        self.i_htg_uc,temp=get_adjacent_index(i,self.htg_uc.index)
        self.i_htgs_uc,temp=get_adjacent_index(i,self.htgs_uc.index)
        self.i_htgs_p_uc,temp=get_adjacent_index(i,self.htgs_p_uc.index)
        self.i_kdj_uc,temp=get_adjacent_index(i,self.kdj_uc.index)
   
        self.i_htg_dn,temp=get_adjacent_index(i,self.htg_dn.index)
        self.i_htgs_dn,temp=get_adjacent_index(i,self.htgs_dn.index)
        self.i_macd_dn,temp=get_adjacent_index(i,self.macd_dn.index)
        self.i_macds_dn,temp=get_adjacent_index(i,self.macds_dn.index)
        self.i_macdl_dn,temp=get_adjacent_index(i,self.macdl_dn.index)
        self.i_macdc_dn,temp=get_adjacent_index(i,self.macdc_dn.index)
        self.i_htgc_dn,temp=get_adjacent_index(i,self.htgc_dn.index)
        
        self.i_htgc_dc,temp=get_adjacent_index(i,self.htgc_dc.index)
        self.i_htg_dc,temp=get_adjacent_index(i,self.htg_dc.index)
        self.i_htgs_dc,temp=get_adjacent_index(i,self.htgs_dc.index)
        self.i_htgs_p_dc,temp=get_adjacent_index(i,self.htgs_p_dc.index)
        self.i_kdj_dc,temp=get_adjacent_index(i,self.kdj_dc.index)


class Trader_testing01(Trader):
    def __init__(self,df):
        super().__init__(df)
        self.j_range_b=[25,75]
        self.j_range_s=[20,80]

    def is_buy_signal(self,i):
        signal=False;
        super().get_feature_index(i)
        con1= ((i-self.i_htgs_up)<1)
        con1&=((i-self.i_macds_up)<2)
        con1&=self.macds_roc[i]>0#0.3
        con1&=self.df.KDJ_J[i]<self.j_range_b[0]

        #this is the quick dip reverse
        con2 =((i-self.i_htgs_uc)<1)&((i-self.i_htgs_dc)<3)
        con2&=self.df.KDJ_J[i]<self.j_range_b[0]


        signal=con1 #or con2
        return signal

    def is_sell_signal(self,i):
        signal=False;
        super().get_feature_index(i)

        con1= ((i-self.i_htgs_dn)<2)
        con1&=((i-self.i_macdl_dn)<2)
        #con1&=((i-self.i_macds_dn)<2)
        #con1&=self.df.KDJ_K[i]>self.j_range_s[1]
        signal=con1
        return signal

class Trader_BearMarket01(Trader):
    def __init__(self,df):
        super().__init__(df)

    def is_buy_signal(self,i):
        signal=False;
        i_htg_up,temp=get_adjacent_index(i,self.htg_up.index)
        i_htgl_up,temp=get_adjacent_index(i,self.htgl_up.index)
        i_htgs_uc,temp=get_adjacent_index(i,self.htgs_uc.index)
        i_htgc_uc,temp=get_adjacent_index(i,self.htgc_uc.index)

        i_macd_up,temp=get_adjacent_index(i,self.macd_up.index)
        i_macds_up,temp=get_adjacent_index(i,self.macds_up.index)
        i_macdl_up,temp=get_adjacent_index(i,self.macdl_up.index)
        i_macdc_up,temp=get_adjacent_index(i,self.macdc_up.index)
        i_htgc_up,temp=get_adjacent_index(i,self.htgc_up.index)

        i_htg_uc,temp=get_adjacent_index(i,self.htg_uc.index)
        i_htgs_uc,temp=get_adjacent_index(i,self.htgs_uc.index)
        i_htgs_p_uc,temp=get_adjacent_index(i,self.htgs_p_uc.index)
        i_kdj_uc,temp=get_adjacent_index(i,self.kdj_uc.index)
        
        con= (i-i_htgs_uc)<1
        con&=(i-i_macdl_up)<1

        signal=con

        return signal

    def is_sell_signal(self,i):
        signal=False;
        i_htg_dn,temp=get_adjacent_index(i,self.htg_dn.index)
        i_macd_dn,temp=get_adjacent_index(i,self.macd_dn.index)
        i_macds_dn,temp=get_adjacent_index(i,self.macds_dn.index)
        i_macdl_dn,temp=get_adjacent_index(i,self.macdl_dn.index)
        i_macdc_dn,temp=get_adjacent_index(i,self.macdc_dn.index)
        i_htgc_dn,temp=get_adjacent_index(i,self.htgc_dn.index)
        
        i_htgc_dc,temp=get_adjacent_index(i,self.htgc_dc.index)
        i_htg_dc,temp=get_adjacent_index(i,self.htg_dc.index)
        i_htgs_dc,temp=get_adjacent_index(i,self.htgs_dc.index)
        i_htgs_p_dc,temp=get_adjacent_index(i,self.htgs_p_dc.index)
        i_kdj_dc,temp=get_adjacent_index(i,self.kdj_dc.index)

        con= (i-i_htgs_dc)<1
        con&=(i-i_macdl_dn)<1
        signal=con

        return signal


