#上涨行情双连阴异动信号
import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import math
from ts_util import *
from traders import *
from strategist import *

sec_num='600549'#厦门钨业
start1=600000
end1=600549


def list_conditions():
    counter=0
    counter1=0
    counter2=0
    

    for stock in range(start1,end1):
        sec_num=str(stock)
        df=load_sec_from_db_date(sec_num)
        if df is None: continue
        p1_pc=pd.Series()
        p2_pc=pd.Series()
        for m in range(5,len(df.index)):

            i=len(df.index)-m

            con1=df.p_change[i]>=10
            con1&=df.p_change[i+1]<=0
            con1&=df.p_change[i+2]<=0
            con1&=df.p_change[i+3]<=0



            if con1:
                counter+=1
                cdl0=get_candle_array(df,i)
                cdl1=get_candle_array(df,i+1)
                cdl2=get_candle_array(df,i+2)
                cdl3=get_candle_array(df,i+3)
                print(sec_num,'  con1:',counter)
                print(df.date[i],'  ',cdl0,' ',df.p_change[i])
                print(df.date[i+1],'  ',cdl1)
                print(df.date[i+2],'  ',cdl2)
                print(df.date[i+3],'  ',cdl3)

                # vc1=(df.volume[i+1]-df.volume[i+2])/df.v_ma10[i+1]
                # vc2=(df.volume[i+2]-df.volume[i+3])/df.v_ma10[i+1]
                # vc3=(df.volume[i+2]-df.volume[i+4])/df.v_ma10[i+1]

                vc1=df.volume[i+1]/df.v_ma20[i+1]
                vc2=df.volume[i+2]/df.v_ma20[i+2]
                vc3=df.volume[i+3]/df.v_ma20[i+3]
                vcs=np.round([vc1,vc2,vc3],2)
                print(df.date[i],'  ',vcs)
  
    print('TOTAL: con1:',counter)
    #print ("Total ------   >10:",counter,'pc1:%16s'%str(strp1pc),'pc2:%16s'%str(strp2pc))

def test_condition():
    rate=0
    rates=[]
    count_zt=0

    for stock in range(start1,end1):
        sec_num=str(stock)
        df=load_sec_from_db_date(sec_num)
        #df.sort_index(ascending=False)
        #print(df.date[0])
        #df=load_sec_from_ts_date(sec_num,start='2014-01-01',end='2016-01-01')

        if df is None: continue
        for m in range(5,len(df.index)):

            i=len(df.index)-m
            #con1=df.p_change[i]>=10
            con1=df.p_change[i+1]<0
            con1&=df.p_change[i+2]<0
            con1&=df.p_change[i+3]<0

            con1&=df.high[i+1]==df.low[i+1]
            #con1&=df.high[i+2]==df.low[i+1]

            #vc1=df.volume[i-1]/df.v_ma20[i-1]
            #con1&=vc1>2

            if con1 :#& lbshadow:
                rate+=df.p_change[i]
                rates.append(df.p_change[i])
                avr=np.average(rates)
                dayrate=100*(df.close[i]-df.open[i])/df.open[i]
                if(df.p_change[i]>=10): 
                    print('------------------')
                    count_zt+=1
                print("date:%s p_change: %3.2f"%(df.date[i+1],df.p_change[i+1]))
                print("date:%s p_change: %3.2f"%(df.date[i+2],df.p_change[i+2]))
                print("date:%s p_change: %3.2f"%(df.date[i+3],df.p_change[i+3]))
                print("%s %-3.2f %-3.2f i:%s| average %-3.2f tz:%d/%d acurracy=%3.2f"%(sec_num,df.p_change[i],dayrate,df.date[i],avr,count_zt,len(rates),count_zt/len(rates)))
    print('zt count:',count_zt)
    #print('total rate:',rate)
    print('average rate:',np.average(rates))


def main():
    connect_db('day_stock.db')
    #list_conditions()
    test_condition()

if __name__ == '__main__':
    main()

