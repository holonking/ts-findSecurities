
import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from ts_util import *




def get_nearest_vally(s):
    for i in range(len(s)-1):
            d=s[i]-s[i+1]
            if d<0: 
                return i
    return -1
def get_nearest_peak(s):
    for i in range(len(s)-1):
            d=s[i]-s[i+1]
            if d>0: 
                return i
    return -1
def get_df(d):
    if len(d.index)<40: 
        #print("index length=%d <40, return None"%len(index))
        return None
    df=d.sort_index(ascending=True)
    
    close=df.close
    ema12=pd.ewma(close,12)
    ema26=pd.ewma(close,26)

    macd=ema12-ema26
    signal=pd.ewma(macd,9)
    htg=macd-signal

    df['ema12']=ema12
    df['ema26']=ema26
    df['macd']=macd
    df['signal']=signal
    df['htg']=htg

    return df

def get_features(df):
    df=df.sort_index(ascending=False)
    valley=-1
    peak=-1
    upCross=-1
    dnCross=-1
    d=0
    dl=0
    #print(df)
    span=len(df.index)
    #print("span=%d"%span)
    if span>40: span=20
    for i in range(1,span-1):
        d=df.htg[i]-df.htg[i+1]
        dl=df.htg[i-1]-df.htg[i]
    

        #find first valley
        if valley<0:
            if df.htg[i]<0 and dl>0 and d<0: 
                #print ("found valley at %d h[i]=%f, d=%f, dl=%f"%(i,df.htg[i],d,dl))
                valley=i
        #find first peak
        if peak<0:
            if df.htg[i]>0 and dl<0 and d>0: 
                peak=i
        #find upCross
        if upCross<0:
            if df.htg[i-1]>0 and df.htg[i]<=0 and df.htg[i+1]<0 : 
                #print("found upcross at %d h[i-1]=%f, h[i]=%f,h[i+1]%f"%(i,df.htg[i-1],df.htg[i],df.htg[i+1]))
                upCross=i
        #find dnCross
        if dnCross<0:
            if df.htg[i-1]<0 and df.htg[i]>=0 and df.htg[i+1]>0 : 
                dnCross=i
        
    return valley,peak,upCross,dnCross

def plot(df):
    fig=plt.figure()
    ax1=fig.add_subplot(211)
    ax2=fig.add_subplot(212,sharex=ax1)

    ax1.plot(df.close.tolist())
    ax1.plot(df.ema12.tolist())
    ax1.plot(df.ema26.tolist())
    ax2.plot(df.htg.tolist())
    ax2.plot(df.macd.tolist())
    ax2.plot(df.signal.tolist())
    x=np.linspace(0,len(df.htg)-1,len(df.htg))
    ax2.fill_between(x,0,df.htg.tolist(),color="#aaaaaa")

    plt.show()
    
def getSecAndPlot(sec_num,days=90):
    today=datetime.date.today()
    delta=datetime.timedelta(days=days)
    xday=today-delta
    strDs=str(xday)
    strDe=str(today)
    d=ts.get_hist_data(str(sec_num),start=strDs,end=strDe)
    if type(d)==type(None):
        print('nothing retrieved')
        return None
    print("data length=%d"%len(d.index))
    #print(d.close)
    df=get_df(d)
    if type(df)==type(None) : return None
    print(df)
    plot(df)
def getSec(sec_num,days=900):
    today=datetime.date.today()
    delta=datetime.timedelta(days=days)
    xday=today-delta
    strDs=str(xday)
    strDe=str(today)
    d=ts.get_hist_data(str(sec_num),start=strDs,end=strDe)
    if type(d)==type(None):
        print('nothing retrieved')
        return None
    #print("data length=%d"%len(d.index))
    #print(d.close)
    df=get_df(d)
    if type(df)==type(None) : return None
    return df

def run1():
    outData=[]
    outSec=[]
    outV=[]
    outP=[]
    outU=[]
    outD=[]
    outDf=pd.DataFrame()

    ndays=3
    for i in range(0,3000):
        sec_num=600000+i
        arrData=getSec(600000+i)
        if type(arrData)!=type(None): 
            features=get_features(arrData)
            v,p,u,d=features    
            print("fetching"+str(sec_num)+" u="+str(u))
            if u>0 and u<ndays:
                out=sec_num,u
                outData.append(out)
                outV.append(v)
                outP.append(p)
                outU.append(u)
                outD.append(d)
                outSec.append(sec_num)

                print("found %s v:%-3d  ,p:%-3d  ,u:%-3d  ,d:%-3d"%(str(sec_num),v,p,u,d) )

            #end if
        #end if
    #end for

    outDf['sec_num']=outSec
    outDf['v']=outV
    outDf['p']=outP
    outDf['u']=outU
    outDf['d']=outD
    print(outDf)
    outDf.to_csv('daily.csv')

    #end for i

    for d in outData:
        sec_num,u=d
        print("%s - %3ddays"%(str(sec_num),u))
def run2():

    select=[]
    

    for sec_num in range(600000,600001):

        sec_num='600898'
        df=load_sec_from_ts_days(sec_num,300)
        df=fill_df_MACD(df)
        df=fill_df_KDJ(df)
        if type(df)==type(None): continue

        
        ax1,ax2,ax3=plot_day_default(df)

        #ftr=get_list_interpolated_indice(df.htg.tolist())
        htg_up,htg_dn=find_reverse(df.htg)



        
        ax2.scatter(htg_up.index,htg_up,color='r')
        ax2.scatter(htg_dn.index,htg_dn,color='g')

        kdj_uc,kdj_dc=find_KDJ_cross(df)
        ax3.scatter(kdj_uc.index,kdj_uc,color='r')
        ax3.scatter(kdj_dc.index,kdj_dc,color='g')


        plt.show()

        #pc_max=df.p_change.max();
        #pc_min=df.p_change.min();

    print(select)
    ##print(df)
    #print("max price up={}, price drop={}".format(pc_max,pc_min))
    #print("htg[{}]={}".format(gth_mk_x,min_htg))

if __name__ == '__main__':
    run2()
    #run1()
    






