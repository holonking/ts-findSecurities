import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
from traders import *

ttl_trade_count=0
ttl_profit=0
ttl_profit_rate=0
ttl_gain=0
ttl_lose=0
ttl_totalcost=0

ttl_wincount=0
ttl_lostcount=0
ttl_accuracy=0

class Features:
    def log():
        return

class strategy_day_01:
    def __init__(self):
        #params:
        #params[0] int      0-5         buy feature range 01 
        #params[1] int      0-5         buy feature range 02
        #params[2] int      0-5         sell feature range 01
        #params[3] int      0-5         sell feature range 02
        #params[4] float    0.01-0.5    buy_macd_roc_reverse
        #params[5] float    0.01-0.5    sell_macd_roc_reverse
        self.params=[2,2,2,4,0.3,0.3]
        self.mouse_move_data=[]
        self.features=Features()

    def old_method_backup(self,sec_num,draw=True,log=True,df=None):
        #sec_num='600898'
        global trade_count, profit,lose,gain,totalcost,returnrate,wincount,lostcount,accuracy
        trade_state='empty'
        buy_price=-1
        sale_price=-1
        feed=0.002
        returnrate=0

        #df=load_sec_from_ts_days(sec_num,300)
        if df is None:
            df=load_sec_from_ts_date(sec_num,'2015-04-01','2016-04-01')

            macd_name_l=['macd_l','signal_l','htg_l']
            macd_name_s=['macd_s','signal_s','htg_s']

            df=fill_df_MACD_ratio(df)
            df=fill_df_MACD_ratio(df,[6,8,4],macd_name_s)
            df=fill_df_MACD_ratio(df,[24,32,18],macd_name_l)
            df=fill_df_KDJ(df)
            if type(df)==type(None): return 0
            if len(df.close)<50: return 0


        #find valleys and peaks for macd historam
        htg_up,htg_dn=find_reverse(df.htg)

        #find valley and peaks for macd
        macd_up,macd_dn=find_reverse(df.macd)
        macd_up,macd_dn=find_reverse(df.macd)
        macd_up,macd_dn=find_reverse(df.macd)

        macd_roc=df.macd-df.macd.shift()
        htg_roc=df.htg-df.htg.shift()

        #find K up corss and down crossD
        kdj_uc,kdj_dc=find_KD_cross(df)

        buy=pd.Series()
        sell=pd.Series()

        b_range1=self.params[0]#2
        b_range2=self.params[1]#3
        s_range1=self.params[2]#2
        s_range2=self.params[3]#4
        macd_roc_reverse_b=self.params[4] #0.1 #both possitive and negative to evaluate macd reverse
        macd_roc_reverse_s=self.params[5] #0.3

        for i in range(40,len(df.close)):
            close=df.close[i]
            

            #find buy signals
            i_htg_up,temp=get_adjacent_index(i,htg_up.index)
            i_macd_up,temp=get_adjacent_index(i,macd_up.index)
            i_kdj_uc,temp=get_adjacent_index(i,kdj_uc.index)

            con=(i-i_htg_up)<=b_range1
            #con=con&(i-i_macd_up<=b_range1)
            con=con&(i-i_kdj_uc<=b_range2)
            con=con&(macd_roc[i]<macd_roc_reverse_b)&(macd_roc[i]>-macd_roc_reverse_b)
            con=con&(get_curve_form(df.signal,i_macd_up)=='concave')
            if con :
                buy.set_value(df.index[i],df.close[i])
                if trade_state=='empty':
                    trade_state='holding'
                    buy_price=df.close[i]*(1+feed)*100
                    totalcost+=buy_price


            #find sell signal
            i_htg_dn,temp=get_adjacent_index(i,htg_dn.index)
            i_macd_dn,temp=get_adjacent_index(i,macd_dn.index)
            i_kdj_dc,temp=get_adjacent_index(i,kdj_dc.index)

            con=(i-i_htg_dn)<=s_range1
            #con=con&(i-i_macd_dn<=s_range1)
            con=con&(macd_roc[i]<macd_roc_reverse_s)&(macd_roc[i]>-macd_roc_reverse_s)
            con=con&(i-i_kdj_dc<=s_range2)
            con=con&(get_curve_form(df.signal,i_macd_dn)=='convex')
            if con:
                sell.set_value(df.index[i],df.close[i])
                if trade_state=='holding':
                    trade_state='empty'
                    trade_count+=1
                    sell_price=df.close[i]*(1-feed)*100
                    profit_t=sell_price-buy_price
                    profit+=profit_t
                    returnrate=profit/totalcost*100
                    if profit_t<0: 
                        lose+=profit_t
                        lostcount+=1
                    if profit_t>0: 
                        gain+=profit_t
                        wincount+=1
                    accuracy=wincount/trade_count*100
                    if log:
                        print("%s traded, profit: %8.2f | total %3d trades, won:%8.2f  lost :%8.2f  accuracy:%3.1f%% | total profit:%10.2f  %3.1f%% "%(sec_num,profit_t,trade_count,gain,lose,accuracy,profit,returnrate) )
    def on_mouse_move(self,event):
        #print (event.x,',',event.y)
        if not event.inaxes:return
        lh=12
        title=''
        value=''
        mi=int(event.xdata)
        for i in range(len(self.mouse_move_data)):
            se,name=self.mouse_move_data[i]
            x=10
            y=lh*i
            if name.find('rc')>-1:
                title+="|%-5s"%name
                value+="|%-2.2f"%se[mi]
            else:
                index,temp=get_adjacent_index(mi,se.index)
                dif=int(mi-index)
                title+="|%-4s"%name
                value+="|%-4s"%dif
                #event.inaxes.text(x,y,name+str(index))
                #plt.draw()        
        print(title)
        print(value)

    def run(self,sec_num,draw=True,log=True,df=None,start='2015-04-01',end='2016-04-01'):
        #sec_num='600898'
        print('flag 1')
        global trade_count, profit,lose,gain,totalcost,returnrate,wincount,lostcount,accuracy
        trade_state='empty'
        buy_price=-1
        sale_price=-1
        feed=0.002
        returnrate=0

        #df=load_sec_from_ts_days(sec_num,300)
        print('flag 2')
        if df is None:
            df=load_sec_from_ts_date(sec_num,start,end)

            macd_name_l=['macd_l','signal_l','htg_l']
            macd_name_s=['macd_s','signal_s','htg_s']
            #macd_name_c=['macdc','signalc','htgc']
            df=fill_df_MACD_ratio(df)
            df=fill_df_MACD_ratio(df,[6,8,4],macd_name_s)
            df=fill_df_MACD_ratio(df,[24,32,18],macd_name_l)
            #df=fill_df_MACD_ratio_com(df,[12,26,9],macd_name_c)
            df=fill_df_KDJ(df)

            if type(df)==type(None): return 0
            if len(df.close)<50: return 0


        #tdr=Trader_BearMarket01(df)
        tdr=Trader_testing01(df)
        

        #add data to display when mouse move
        self.mouse_move_data.append((tdr.htg_up,'hup'))
        self.mouse_move_data.append((tdr.macd_up,'mup'))
        self.mouse_move_data.append((tdr.macds_up,'mupS'))
        self.mouse_move_data.append((tdr.macdl_up,'mupL'))

        self.mouse_move_data.append((tdr.htg_uc,'huc'))
        self.mouse_move_data.append((tdr.htgs_uc,'hucS'))
        self.mouse_move_data.append((tdr.htgl_uc,'hucL'))

        self.mouse_move_data.append((tdr.htg_dn,'hdn'))
        self.mouse_move_data.append((tdr.macd_dn,'mdn'))
        self.mouse_move_data.append((tdr.macds_dn,'mdnS'))
        self.mouse_move_data.append((tdr.macdl_dn,'mdnL'))

        self.mouse_move_data.append((tdr.htg_dc,'hdc'))
        self.mouse_move_data.append((tdr.htgs_dc,'hdcS'))
        self.mouse_move_data.append((tdr.htgl_dc,'hdcL'))

        self.mouse_move_data.append((tdr.macd_roc,'mrc'))
        self.mouse_move_data.append((tdr.macds_roc,'mrcS'))
        self.mouse_move_data.append((tdr.macdl_roc,'mrcL'))
        
        self.mouse_move_data.append((tdr.htg_roc,'hrc'))
        self.mouse_move_data.append((tdr.htgs_roc,'hrcS'))
        self.mouse_move_data.append((tdr.htgl_roc,'hrcL'))




        print('flag 3')

        #plot the chart---------------------------------------        
        if draw:
            print('flag 3-1')
            axes=make_axes(5,host=self)
            plot_price(axes[0],df)
            plot_MACD(axes[1],df,macd_name_s)
            plot_MACD(axes[2],df)
            plot_MACD(axes[3],df,macd_name_l)
            #plot_MACD(axes[3],df,macd_name_c,color=['#00ff00','#77ff77','#ddffdd'])
            plot_KDJ(axes[4],df)

            axes[3].scatter(tdr.htgl_up.index,tdr.htgl_up,color='r')
            axes[3].scatter(tdr.htgl_dn.index,tdr.htgl_dn,color='g')
            axes[3].scatter(tdr.macdl_up.index,tdr.macdl_up,color='r')
            axes[3].scatter(tdr.macdl_dn.index,tdr.macdl_dn,color='g')

            #axes[1].scatter(tdr.htgs_uc.index,tdr.htgs_uc,color='r')
            #axes[1].scatter(tdr.htgs_dc.index,tdr.htgs_dc,color='g')
            axes[1].scatter(tdr.htgs_up.index,tdr.htgs_up,color='r')
            axes[1].scatter(tdr.htgs_dn.index,tdr.htgs_dn,color='g')

            #axes[2].scatter(tdr.htg_uc.index,tdr.htg_uc,color='r')
            #axes[2].scatter(tdr.htg_dc.index,tdr.htg_dc,color='g')
            axes[2].scatter(tdr.htg_up.index,tdr.htg_up,color='r')
            axes[2].scatter(tdr.htg_dn.index,tdr.htg_dn,color='g')
            #axes[1].scatter(tdr.htgs_p_uc.index,tdr.htgs_p_uc,color='r')
            #axes[1].scatter(tdr.htgs_p_dc.index,tdr.htgs_p_dc,color='g')

            #axes[2].scatter(tdr.htg_p_uc.index,tdr.htg_p_uc,color='r')
            #axes[2].scatter(tdr.htg_p_dc.index,tdr.htg_p_dc,color='g')

        print('flag 3')
            
        #/////////////////////////////////////////////////////
        #/////////////////////////////////////////////////////
        #//////////////////   TRADING   //////////////////////
        #/////////////////////////////////////////////////////
        #/////////////////////////////////////////////////////
        b_range1=self.params[0]#2
        b_range2=self.params[1]#3
        s_range1=self.params[2]#2
        s_range2=self.params[3]#4
        macd_roc_reverse_b=self.params[4] #0.1 #both possitive and negative to evaluate macd reverse
        macd_roc_reverse_s=self.params[5] #0.3

        buy_signals=pd.Series()
        sell_signals=pd.Series()

        trades=[]
        trade=None
        for i in range(40,len(df.close)):
            close=df.close[i]
            
            # search buy condtions-----------------------------------
            can_buy=tdr.is_buy_signal(i)
            can_sell=tdr.is_sell_signal(i)
            tdr.get_feature_index(i)
            if can_buy:
                buy_signals.set_value(i,close)
                if(trade is None):
                    trade=Trade(id=len(trades))
                    trade.buy(close,i)
                    trades.append(trade)

            # search sell condtions-----------------------------------  
            if can_sell:
                sell_signals.set_value(i,close)
                if(trade is not None):
                    trade.sell(close,i)
                    if log: trade.log()
                    if draw:trade.plot(axes[0])
                    trade=None

            #safe sell
            if(trade is not None):
                safe_exit=((close-trade.bought)/trade.bought)<-0.05
                if safe_exit:
                    trade.sell(close,i)
                    if log: trade.log()
                    if draw:trade.plot(axes[0])
                    trade=None
        
        #calculate total performace
        cost=0
        profit=0
        profit_rate=0
        wins=0
        lost=0
        accuracy=0
        for t in trades:
            profit+=t.profit
            cost+=t.bought
            if profit>0: wins+=1
            else: lost+=1
        if cost>0:
            profit_rate=profit/cost*100
            accuracy=wins/len(trades)*100
            if log:
                print("Total %d trades on %s, a:%3.2f%%, p%8.2f|r%3.2f%%  "%(len(trades),sec_num,accuracy,profit,profit_rate))
        else:
            print("Total %d trades on %s"%(len(trades),sec_num))


        print('flag 4')


        if draw:
            if len(buy_signals.index)>0 :axes[0].scatter(buy_signals.index,buy_signals,color='r')
            if len(sell_signals.index)>0 :axes[0].scatter(sell_signals.index,sell_signals,color='g')
            plt.show()
        return returnrate


def run_comapre_macd(self,sec_num):
        df=load_sec_from_ts_days(sec_num,300)
        df=fill_df_MACD(df)
        df=fill_df_KDJ(df)
        if type(df)==type(None): return
        plot_day_macd_schemes(df)
        plt.show()

if __name__ == '__main__':
    #global trade_count,profit

    stg=strategy_day_01()
    #stg.params=[2, 1, 4, 3, 0.038024200802617, 0.046248246566009434]
    stg.params=[1, 3, 1, 3, 0.030204634013867124, 0.02961919658863036]
    #stg.params=[2, 3, 2, 4, 0.1, 0.3]
    loop=False
    loop=True
    if loop:
        #for i in range(102020,1002200):
        for i in range(1600020,1602200):
            try:
                stg.run(str(i)[1:7],draw=False,log=True)
            except:
                continue

    stg.run('600000',start='2015-04-01',end='2016-04-01')

    #索非亚 std 比较低 @ 2015-2016
    #stg.run('002572',start='2015-04-01',end='2016-04-01')

    #熊市，有升跌 2015-2016
    #tested work with htgs_cross + macdl_reverse
    #stg.run('600549',start='2015-04-01',end='2016-04-01')
    

