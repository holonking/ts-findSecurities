import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
from traders import *

BUY='constant buy'
SELL='constant sell'

class StrategistBase:
    def __init__(self,df=None):
        
        if df is not None:self.set_data(df)
        self.axes=None
        self.plotter=None
        self.reset_evaluation()
    def reset_evaluation(self):
        self.nearest_index=None
        self.buy_signals=pd.Series()
        self.sell_signals=pd.Series()
        self.buys=pd.Series()
        self.sells=pd.Series()
        self.trades=[]
        self.text_trade=[]
        self.trade=None
        self.remove_data_text()
    def set_data(self,df):
        self.df=df
        self.fill_data()
        self.update()
    def set_plotter(self,p):
        print('@ set_plotter p=',p)
        self.plotter=p
        

    def add_trade_point(self,i,type=BUY):
        df=self.df
        if type==BUY:
            self.buys.set_value(i,df.close[i])
            self.plotter.buys[0].set_data(self.buys.index,self.buys)

        elif type==SELL:
            self.sells.set_value(i,df.close[i])
            self.plotter.sells[0].set_data(self.sells.index,self.sells)

    def add_signal(self,i,type=BUY):
        df=self.df
        if type==BUY:
            self.buy_signals.set_value(i,df.close[i])
            self.plotter.buy_signals[0].set_data(self.buy_signals.index,self.buy_signals)
        elif type==SELL:
            self.sell_signals.set_value(i,df.close[i])
            self.plotter.sell_signals[0].set_data(self.sell_signals.index,self.sell_signals)
    def add_datatext(self,i,s,color=COLOR_01):
        y=self.df.close[i]
        s='          '+s
        t=self.plotter.axes[0].text(i,y,s,color=color,rotation='90',size='x-small')
        self.text_trade.append(t)
    def remove(self):
        self.remove_data_text()
    def remove_data_text(self):
        if self.plotter is None: return
        self.plotter.axes[0].texts=[]

    def key_press(self,event):
        return

    def plot(self,axes):
        return

    def update(self):
        self.reset_evaluation()
        return
    def fill_data(self):
        #fill data frame
        df=self.df
        df=fill_df_MACD_ratio(df,params=[6,8,4],names=['macds','signals','htgs'])
        df=fill_df_MACD_ratio(df,params=[24,32,18],names=['macdl','signall','htgl'])
        df=fill_df_MACD_normalratio(df,params=[24,32,18],names=['macdln','signalln','htgln'])
        df=fill_df_KDJ(df,param=[9,2])
        df=fill_df_KDJ(df,param=[9,9],names=['kl','dl','jl'])

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
  
        kduc,kddc=find_se_cross(df.k,df.d)
        df['kduc']=kduc
        df['kddc']=kddc
        self.df=df


        #print('flag 1')
    def get_nearest_index(self,i):
        df=self.df
        #n=pd.DataFrame()
        n={}
        #names=['mu','md','msu','msd','mlu','mld','su','sd','ssu','ssd','slu','sld','hu','hd','hsu','hsd','hlu','hld','huc','hdc','hsuc','hsdc','hluc','hldc']
        names=['mlu','mld','kduc','kddc','hu','hd','hdc','huc','hsu','hsd','hsuc','hsdc','hsd','hlu','hld','ssu','ssd']
        for name in names:
            if df[name] is None: continue
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
        macdlf=pd.Series()
        macdf=pd.Series()
        for m in range(10,len (df.index)):
            fit,lows,highs=find_extrema(df.macdl[:m], window=5, span_points=30)
            macdlf.set_value(m,fit[len(fit)-1]*2)

            fit,lows,highs=find_extrema(df.macd[:m], window=5, span_points=30)
            macdf.set_value(m,fit[len(fit)-1]*2)
        self.df['macdlf']=macdlf
        self.df['macdf']=macdlf

        macdlfrc=df.macdlf-df.macdlf.shift()
        macdlfrcc=macdlfrc-macdlfrc.shift()
        self.df['macdlfrc']=macdlfrc
        self.df['macdlfrcc']=macdlfrcc
        self.df['macdlfrccEma']=pd.ewma(macdlfrcc,span=5)
    def plot(self,axes):
        df=self.df
        up,dn=find_reverse(df.macdlf)
        df.macdlf.plot(ax=axes[2],color='r')
        df.macdlfrc.plot(ax=axes[4],color=COLOR_01)
        df.macdlfrcc.plot(ax=axes[4],color=COLOR_02)
        df.macdlfrccEma.plot(ax=axes[4],color=COLOR_04)
        axes[4].axhline(y=0)
    def evaluate(self,i):
        super().evaluate(i)
        df=self.df
        n=self.nearest_index
        #print("kduc=",n['kduc'],"i=",i," hu=",n['hu'])

        #print('n.hu=',n.hu)
        kdj_thr_u=35
        if df.macd[i]>1.5: kdj_thr_u=65

        #///////////////////////////
        #/////// BUY ///////////////
        #///////////////////////////
        form=get_curve_form(df.macdlf,i,test_length=5)

        con1=True
        con1&=(i-n['hu'])<1
        #con1&=(i-n['ssu'])<1
        #con1&=df.macdlfrc[i]<0
        #con1&=df.macdlfrcc[i]<0
        con1&=df.macdlfrccEma[i]<0
        #con1&=form=='concave'
        #con1&=df.macd[i]<0
        con1&=(df.d[i]<50)
  
        if con1:
            #print(i-n['kduc'])
            self.buy_signals.set_value(i,df.close[i])

        #///////////////////////////
        #/////// SELL //////////////
        #///////////////////////////

        con1=True
        con1&=(i-n['hd'])<2
        con1&=(i-n['ssd'])<1
        #con1&=df.macdlfrc[i]<0.15
        #con1&=df.macdlfrcc[i]>0
        con1&=df.macdlfrccEma[i]>0
        con1&=form=='convex'
        con1&=(df.d[i]>50)
        #con1&=df.macd[i]>0
        #con1&=(i-n['hsd'])<1
        # con1=(i-n['hsdc'])<1
        # con1&=((i-n['kddc'])<3) #& (df.kduc[i]>50)

        # con2=(i-n['hsd'])<1
        # con2&=df.d[i]>68
        
        # con_dip=((i-n['kddc'])<1) & ((i-n['kduc'])<3)
        # #con1&=df.hu[i]>-0.2

        # con3=(i-n['hsd'])<1
        # con3&=(i-n['huc'])>4
        # con3&=(df.d[i]<70)# & (df.kc[i]<0) & (df.jc[i]<df.kc[i])


        if con1:#or con2:
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
        downslope=df.slc[i]<0 
        downslope&=(df.signall[i]-df.macdl[i])>0.08

        if downslope: subcon1=df.htgl[i]<-0.5
        else: subcon1=df.macdl[i]<0.25


        prevent=(i-n['hd'])>1
        prevent&=(i-n['hsd'])>1
        prevent&=(i-n['hld'])>1



        con1=(i-n['hsu'])<1
        con1&=df.htgs[i]<0

        #con1&=df.htg[i]<0
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
        con1&=subcon1


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
        else: subcon1=df.macdl[i]>1

        con1=True
        con1&=(i-n['hsd'])<1
        con1&=(i-n['hsu'])>1
        con1&=(i-n['hu'])>1
        con1&=(i-n['hlu'])>1
        con1&=subcon1
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

class Stg_normal_macdl(StrategistBase):
    def __init__(self,df,domain1=[-0.75,0.75],risk_buy=-0.3):
        super().__init__(df)
        self.domain=domain1
        self.risk_buy=risk_buy
        self.mlu=0
        self.take_risk=False
    def evaluate(self,i):
        super().evaluate(i)
        df=self.df
        n=self.nearest_index
        dm=self.domain

        #///////////////////////////////////////////
        #////////// LOOK FOR BUY SIGNALS ///////////
        #///////////////////////////////////////////
        #con1 proven worked
        con1=(i-n['hsu'])<1
        con1&=df.macdln[i]<dm[0]

        #con2
        con2=False
        if self.take_risk:
            con2=(i-n['hsu'])<1
            con2=(df.macdln[i]-df.macdln[i-2])>0
            con2=(df.signalln[i]-df.signalln[i-2])>0
            con2&=df.macdln[i]<self.risk_buy

        if con1 or con2:
            self.buy_signals.set_value(i,df.close[i])
            if self.trade is None:
                self.trade=Trade()
                self.trade.buy(df.close[i],i)
                self.buys.set_value(i,df.close[i])
                #print("B i=%d, close=%4.2f"%(i,df.close[i]))
            
        #///////////////////////////////////////////
        #////////// LOOK FOR SELL SIGNALS //////////
        #///////////////////////////////////////////
        con1=(i-n['hsd'])<1
        con1&=df.macdln[i]>dm[1]
        if con1 :
            self.sell_signals.set_value(i,df.close[i])
            if self.trade is not None:
                self.trade.sell(df.close[i],i)
                self.sells.set_value(i,df.close[i])
                self.trades.append(self.trade)
                #self.trade.log()
                self.trade=None
                #print("S i=%d, close=%4.2f"%(i,df.close[i]))
class Stg_macd_slope(StrategistBase):
    def __init__(self,df):
        super().__init__(df)
        df=self.df
        hlrc=df.htgl-df.htgl.shift()
        hrc=df.htg-df.htg.shift()
        mask_up=(hrc>hlrc) & (hrc.shift()<hlrc.shift())
        hrc_uc_hlrc=hrc[mask_up]
        mask_dn=(hrc<hlrc) & (hrc.shift()>hlrc.shift())
        hrc_dc_hlrc=hrc[mask_dn]

        df['hrc']=hrc
        df['hlrc']=hlrc
        df['hrc_uc_hlrc']=hrc_uc_hlrc
        df['hrc_dc_hlrc']=hrc_dc_hlrc
        self.df=df

        
    def evaluate(self,i):
        super().evaluate(i)
        #self.fill_data()
        df=self.df
        n=self.nearest_index

        con1=(i-n['hsu'])<1
        con1&=(i-n['hu'])<1
        con1&=(i-n['kddc'])>4
        con1&=df.dl[i]>df.k[i]
        #con1&=(df.dl[i]<50) or (df.jl[i]<20)
        close=df.close
        if self.trade is not None:
            if close[i]> self.trade.max:
                self.trade.max=close[i]
            if (close[i]<self.trade.max) & (close[i]<(self.trade.bought+(self.trade.max-self.trade.bought)*0.4)):
                safe_sell=True


        if con1:
            self.buy_signals.set_value(i,df.close[i])
            if self.trade is None:
                self.trade=Trade()
                self.trade.buy(df.close[i],i)
                self.buys.set_value(i,df.close[i])


        safe_sell=False
        con1=(i-n['hd'])<1
        con1&=df.dl[i]<df.kl[i]
        con1&=df.jl[i]>75
        if con1:
            self.sell_signals.set_value(i,df.close[i])

        if con1 or safe_sell:
            if self.trade is not None:
                #safe

                #sell condition
                self.trade.sell(df.close[i],i)
                self.sells.set_value(i,df.close[i])
                self.trades.append(self.trade)
                #self.trade.log()
                self.trade=None
class Stg_macdlfc_reverse(StrategistBase):
    def __init__(self,df):
        super().__init__(df)
        macdlf=pd.Series()
        macdf=pd.Series()
        macdsf=pd.Series()
        for m in range(10,len (df.index)):
            fit,lows,highs=find_extrema(df.macdl[:m], window=5, span_points=30)
            macdlf.set_value(m,fit[len(fit)-1]*2)

            fit,lows,highs=find_extrema(df.macd[:m], window=5, span_points=12)
            macdf.set_value(m,fit[len(fit)-1]*2)

            fit,lows,highs=find_extrema(df.macd[:m], window=5, span_points=5)
            macdsf.set_value(m,fit[len(fit)-1]*2)

        self.df['macdlf']=macdlf
        self.df['macdf']=macdf
        self.df['macdsf']=macdsf

        macdlfrc=df.macdlf-df.macdlf.shift()
        macdlfrcc=macdlfrc-macdlfrc.shift()
        self.df['macdlfrc']=macdlfrc
        self.df['macdlfrcc']=macdlfrcc
        self.df['macdlfrccEma']=pd.ewma(macdlfrcc,span=5)
        mlfcu,mlfcd=find_reverse(macdlfrc)
        self.df['mlfcu']=mlfcu
        self.df['mlfcd']=mlfcd
    def plot(self,axes):
        df=self.df
        
        #check how the fitted curve different from macd
        df.macdlf.plot(ax=axes[2],color='orange')
        df.macdf.plot(ax=axes[2],color='blue')
        df.macdsf.plot(ax=axes[1],color='blue')


        df.macdlfrc.plot(ax=axes[4],color=COLOR_01)
        df.macdlfrcc.plot(ax=axes[4],color=COLOR_02)
        df.macdlfrccEma.plot(ax=axes[4],color=COLOR_04)
        axes[4].axhline(y=0)

    def evaluate(self,i):
        super().evaluate(i)
        df=self.df
        n=self.nearest_index
        mlfcu=df.mlfcu.dropna()
        mlfcd=df.mlfcd.dropna()
        i_mlfcu,temp=get_adjacent_index(i,mlfcu.index)
        i_mlfcd,temp=get_adjacent_index(i,mlfcd.index)


        #///////////////////////////
        #/////// BUY ///////////////
        #///////////////////////////
        form=get_curve_form(df.macdlf,i,test_length=5)

        con1=True
        con1&=(i-i_mlfcu)<1
        #con1&=df.macdlfrccEma[i]<0
        con1&=(df.d[i]<60)
  
        if con1:
            #print(i-n['kduc'])
            self.buy_signals.set_value(i,df.close[i])

        #///////////////////////////
        #/////// SELL //////////////
        #///////////////////////////

        con1=True
        con1&=(i-i_mlfcd)<1
        con1&=(df.d[i]>50)
 


        if con1:#or con2:
            self.sell_signals.set_value(i,df.close[i])

class Stg_ma(StrategistBase):
    def __init__(self):
        super().__init__()
        self.ws=4
        self.wl=20
        self.bot=0
        self.top=100

    #update will be called first time generating data
    #can also be called manually during execution  
    def key_press(self,event):
        super().key_press(event)
        print('%s key presed'%event.key)
    

        if event.key=='1': self.ws+=1
        elif event.key=='q': self.ws-=1
        elif event.key=='2': self.wl+=1
        elif event.key=='w': self.wl-=1
        elif event.key=='3': self.top+=0.5
        elif event.key=='e': self.top-=0.5
        elif event.key=='4': self.bot+=0.5
        elif event.key=='r': self.bot-=0.5

        self.update()


    def update(self,ws=None,wl=None,top=None,bot=None):
        super().update()
        if self.df is None: return
        print('Strg_ma.update()')
        if ws is not None:self.ws=ws
        if wl is not None:self.wl=wl

        if bot is not None:self.bot=bot
        if top is not None:self.top=top

        sma=pd.rolling_mean(self.df.close,self.ws)
        smaa=pd.ewma(sma,com=5)
        lma=pd.rolling_mean(self.df.close,self.wl)
        self.df['sma']=sma
        self.df['smaa']=smaa
        self.df['lma']=lma
        self.df['smaa_lma_dif']=smaa-lma

        up,dn=find_se_cross(sma,lma)
        self.df['sma_uc_lma']=up
        self.df['sma_dc_lma']=dn
        self.plot()
        self.plotter.run()


    def plot(self):
        if self.plotter is None: 
            print('StrategistBase.plotter is None')
            return
        self.plotter.clear_axes([3])
        self.df['sma'].plot(ax=self.plotter.axes[3],color=COLOR_03)
        self.df['smaa'].plot(ax=self.plotter.axes[3],color=COLOR_01)
        self.df['lma'].plot(ax=self.plotter.axes[3],color=COLOR_02)
        self.df['sma_uc_lma'].plot(ax=self.plotter.axes[3],marker='o',color='r')
        self.df['sma_dc_lma'].plot(ax=self.plotter.axes[3],marker='o',color='g')

    def evaluate(self,i):
        super().evaluate(i)
        df=self.df
        n=self.nearest_index

        #get adjacent index for the crosses
        sma_uc_lma=df.sma_uc_lma.dropna()
        sma_dc_lma=df.sma_dc_lma.dropna()
        i_sma_uc_lma,temp=get_adjacent_index(i,sma_uc_lma.index)
        i_sma_dc_lma,temp=get_adjacent_index(i,sma_dc_lma.index)

        #///////////////////////////
        #/////// BUY ///////////////
        #///////////////////////////
        
        con1=True
        con1&=i-i_sma_uc_lma<1
        con1&=self.df.d[i]<self.top
  
        if con1:
            self.add_signal(i,BUY) #updates signals on plot
            if self.trade is None:
                self.trade=Trade()
                self.trade.buy(df.close[i],i)
                self.add_trade_point(i,BUY) #updates trade points on plot
                
        #///////////////////////////
        #/////// SELL //////////////
        #///////////////////////////

        con1=True
        con1&=i-i_sma_dc_lma<1
        con1&=self.df.d[i]>self.bot
        
        if con1:#or con2:
            self.add_signal(i,SELL) #updates signals on plot
            if self.trade is not None:
                self.trade.sell(df.close[i],i)
                self.add_trade_point(i,SELL) #updates trade points on plot
                color=COLOR_01 if self.trade.profit_rate <0 else 'r'
                s="%-3.1f%%"%(self.trade.profit_rate*100)
                self.add_datatext(i,s,color=color)
                self.trades.append(self.trade)
                self.trade=None
 
class Stg_reverse_short(StrategistBase):
    def __init__(self):
        super().__init__()
        self.ws=4
        self.wl=20
        self.bot=0
        self.top=100
        self.vparam=[12,26,9]
        self.vmaparam=[12,26]
    
    def fill_data(self):
        super().fill_data()
        v=self.vparam
        va=self.vmaparam
        vm1=pd.ewma(self.df.volume,span=v[0])
        vm2=pd.ewma(self.df.volume,span=v[1])
        vmacd=vm1-vm2
        vsignal=pd.ewma(vmacd,span=v[2])
        vdiv=vmacd-vsignal
        self.df['vmacd']=vmacd
        self.df['vsignal']=vsignal
        self.df['vhtg']=vdiv

        #self.df['vma1']=pd.ewma(self.df.volume,span=va[0])
        self.df['vma1']=pd.rolling_mean(self.df.volume,va[0])
        #self.df['vma2']=pd.ewma(self.df.volume,span=va[1])
        self.df['vma2']=pd.rolling_mean(self.df.volume,va[1])
        self.df['vmadif']=self.df.vma1-self.df.vma2



    #update will be called first time generating data
    #can also be called manually during execution  
    def key_press(self,event):
        super().key_press(event)
        print('%s key presed'%event.key)
    

        if event.key=='1': self.ws+=1
        elif event.key=='q': self.ws-=1
        elif event.key=='2': self.wl+=1
        elif event.key=='w': self.wl-=1
        elif event.key=='3': self.top+=0.5
        elif event.key=='e': self.top-=0.5
        elif event.key=='4': self.bot+=0.5
        elif event.key=='r': self.bot-=0.5

        self.update()


    def update(self,ws=None,wl=None,top=None,bot=None):
        super().update()
        if self.df is None: return
        print('Strg_ma.update()')
        if ws is not None:self.ws=ws
        if wl is not None:self.wl=wl

        if bot is not None:self.bot=bot
        if top is not None:self.top=top

        sma=pd.rolling_mean(self.df.close,self.ws)
        smaa=pd.ewma(sma,com=5)
        lma=pd.rolling_mean(self.df.close,self.wl)
        self.df['sma']=sma
        self.df['smaa']=smaa
        self.df['lma']=lma
        self.df['smaa_lma_dif']=smaa-lma

        up,dn=find_se_cross(sma,lma)
        self.df['sma_uc_lma']=up
        self.df['sma_dc_lma']=dn
        self.plot()
        self.plotter.run()


    def plot(self):
        nameS=['macds','signals','htgs']
        nameL=['macdl','signall','htgl']
        nameV=['vmacd','vsignal','vhtg']
        nameVa=['vma1','vma2','vmadif']
        if self.plotter is None: 
            print('StrategistBase.plotter is None')
            return
        self.plotter.clear_axes([2])
        self.plotter.clear_axes([3])
        self.plotter.clear_axes([4])

        print(self.df)
        plot_MACD(self.plotter.axes[3],self.df,nameVa)  
        plot_KDJ(self.plotter.axes[2],self.df)
        #self.df.k.plot(ax=self.plotter.axes[2],color=COLOR_01)
        #self.df.d.plot(ax=self.plotter.axes[2],color=COLOR_02)
        #self.df.j.plot(ax=self.plotter.axes[2],color=COLOR_03)
                
        nmacd=get_normalized_series(self.df.macd)
        nmacds=get_normalized_series(self.df.macds)
        nmacdl=get_normalized_series(self.df.macdl)
        nvma10=get_normalized_series(self.df.v_ma10)
        nvma20=get_normalized_series(self.df.v_ma20)

        span=3
        manm=pd.ewma(nmacd,span=span)
        manms=pd.ewma(nmacds,span=span)
        manml=pd.ewma(nmacdl,span=span)


        #plot_curve_with_reverse(self.plotter.axes[4],manm,COLOR_R01)
        #plot_curve_with_reverse(self.plotter.axes[4],manms,COLOR_R02)
        #plot_curve_with_reverse(self.plotter.axes[4],manml,COLOR_R03)

        #plot_curve_with_reverse(self.plotter.axes[4],nmacd,COLOR_B01)
        #plot_curve_with_reverse(self.plotter.axes[4],nmacds,COLOR_B02)
        #plot_curve_with_reverse(self.plotter.axes[4],nmacdl,COLOR_B03)
        plot_curve_with_reverse(self.plotter.axes[4],nvma10,COLOR_Y01)
        plot_curve_with_reverse(self.plotter.axes[4],nvma20,COLOR_Y03)
        
        uc,dc=find_se_cross(nvma10,nvma20)
        plot_dot_pairs(self.plotter.axes[4],uc,dc)
        
        #self.df['sma'].plot(ax=self.plotter.axes[3],color=COLOR_03)
        #self.df['smaa'].plot(ax=self.plotter.axes[3],color=COLOR_01)
        #self.df['lma'].plot(ax=self.plotter.axes[3],color=COLOR_02)
        #self.df['sma_uc_lma'].plot(ax=self.plotter.axes[3],marker='o',color='r')
        #self.df['sma_dc_lma'].plot(ax=self.plotter.axes[3],marker='o',color='g')

    def evaluate(self,i):
        super().evaluate(i)
        df=self.df
        n=self.nearest_index

        #///////////////////////////////////////////
        #////////// LOOK FOR BUY SIGNALS ///////////
        #///////////////////////////////////////////
        #prevent=(i-n['hld'])>4
        downslope=df.slc[i]<0 
        downslope&=(df.signall[i]-df.macdl[i])>0.08

        if downslope: subcon1=df.htgl[i]<-0.5
        else: subcon1=df.macdl[i]<0.25


        prevent=(i-n['hd'])>1
        prevent&=(i-n['hsd'])>1
        prevent&=(i-n['hld'])>1



        con1=(i-n['hsu'])<1
        con1&=df.htgs[i]<0

        #con1&=df.htg[i]<0
        con1&=df.macds[i]<0
        con1&=df.macd[i]<0

        #con1&=abs(df.jc[i]-df.jc[i-1])<26 #prevent suddent change 
        con1&=df.d[i]<60
        #-----prevent too close to dn
        con1&=prevent


        #macds dip
        con2=(i-n['hsu'])<1
        con2&=df.close[i-2]>df.close[i]
        con2&=(i-n['hsd'])>5
        #con2&=abs(df.jc[i]-df.jc[i-1])<26 #prevent suddent change 
        con2&=prevent
        con1&=subcon1


        #if con3:
        if con1 or con2:
            #print(i-n['kduc'])
            self.buy_signals.set_value(i,df.close[i])
            #print('mc:%3.2f'%df.mc[i],'mlc:%3.2f'%df.mlc[i], ' dif%3.2f'%abs(df.jc[i]-df.jc[i-1]))


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
        else: subcon1=df.macdl[i]>1

        con1=True
        con1&=(i-n['hsd'])<1
        con1&=(i-n['hsu'])>1
        con1&=(i-n['hu'])>1
        con1&=(i-n['hlu'])>1
        con1&=subcon1
        #con1&=prevent

        #debuf message
        if i==157:
        #if con1 :
            print('macdl=%4.2f'%(df.macdl[i]),'subcon1=',subcon1,' downslope=',downslope, 'macd dif=',df.signall[i]-df.macdl[i])
            print('n[hsu]=',n['hsu'],' df.hsu=%4.2f'%df.hsu[n['hsu']])
            print('n[hsd]=',n['hsd'],' df.hsd[xxx]=%4.2f'%df.hsd[n['hsd']])
            print('n[hsd]=',n['hsd'],' df.htgs[i]=%4.2f'%df.htgs[i])
            #print(df.hsu)

 
