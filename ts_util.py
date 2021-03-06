

import tushare as ts
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.finance import candlestick_ohlc, candlestick2_ohlc
import matplotlib as mpl

import math

from sqlalchemy import create_engine

from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri, r, Environment

base = importr('base')
stats = importr('stats')
pandas2ri.activate()

#global constance
COLOR_01='#4682b4'
COLOR_02='#cc33cc'
COLOR_03='#FFcc00'
COLOR_04='#339933'
COLOR_05='#FFcccc'

COLOR_B01='#4682b4'
COLOR_B02='#81B2DB'
COLOR_B03='#A8C9E6'

COLOR_R01='#cf3636'
COLOR_R02='#D96868'
COLOR_R03='#E8A2A2'

COLOR_Y01='#FCBB23'
COLOR_Y02='#FAD173'
COLOR_Y03='#FFEE2E'

COLOR_LR='#ffdddd'
COLOR_LB='#ddddff'
COLOR_LGY='#dddddd'

COLOR_DN=COLOR_01
COLOR_UP='#FF3333'

MACD_STD_PARAMS=[12,26,9]
#MACD_STD_PARAMS=[26,32,18]
EWMA_TIME_SCALE=[2,6,12]

mouse_vlines=[]
mouse_message=[]

engine=None

def connect_db(filename):
    DB_FILE=filename
    global engine
    engine = create_engine('sqlite:///' + DB_FILE)


#loads security from tushare api returns a df
def load_sec_from_ts_days(sec_num,days):
    today=datetime.date.today()
    delta=datetime.timedelta(days=days)
    xday=today-delta
    return load_sec_from_ts_date(sec_num,xday,today)

def load_sec_from_ts_tick(sec_num,date):
    df=ts.get_tick_data(sec_num,date)
    if df is None: return None
    df=df.sort_index(ascending=False)
    df=df.reset_index()
    return df

#loads security from tushare api returns a df
def load_sec_from_ts_date(sec_num,start='2013-01-01',end='2016-01-01',min_days=10):
    #print("fetching %s"%str(sec_num))
    strDs=str(start)
    strDe=str(end)

    #get 30 days(requres >9 days) of data
    df=ts.get_hist_data(str(sec_num),start=strDs,end=strDe)
    if type(df)==type(None) :return None
    if len(df)<min_days : return None
    df=df.sort_index(ascending=True)
    df=df.reset_index()
    df.insert(0,'sec_num',sec_num)
    return df
def load_sec_from_db_date(sec_num,start,end):
    #print("fetching %s"%str(sec_num))
    if engine is None:
        print('no engine, please run connect_db(db_filename) first')
        return
    strDs=str(start)
    strDe=str(end)
    strNum=str(sec_num)

    query="select * from day_data where stock='%s' and date>='%s' and date<='%s' "%(strNum,strDs,strDe) 
    df=pd.read_sql_query(query,engine)
    df=df.sort_index(ascending=True)
    df=df.reset_index()
    return df

def x_formatter(x,pos=None):
        i=int(x)
        if i<len(df.date): return df.date[i]
        
        return 0
def get_candle_array(df,i):
    o=np.round(df.open[i],2)
    c=np.round(df.close[i],2)
    h=np.round(df.high[i],2)
    l=np.round(df.low[i],2)
    return np.round([o,c,h,l],2)

#default plotter for day data
def plot_day_default(df):
    fig=plt.figure()
    ax1=fig.add_subplot(311)
    ax2=fig.add_subplot(312,sharex=ax1)
    ax3=fig.add_subplot(313,sharex=ax1)

    #print (df.date)
    ax3.xaxis.set_major_formatter(ticker.FuncFormatter(x_formatter))
    
    df.ema26.plot(ax=ax1,color=COLOR_03)
    df.ema12.plot(ax=ax1,color=COLOR_02)
    df.close.plot(ax=ax1,color=COLOR_01)

    df.signal.plot(ax=ax2,color=COLOR_03)
    df.macd.plot(ax=ax2,color=COLOR_02)
    df.htg.plot(ax=ax2,color=COLOR_01)

    #df.KDJ_RSV.plot(ax=ax3,color='r')
    df.KDJ_J.plot(ax=ax3,color=COLOR_03)
    df.KDJ_D.plot(ax=ax3,color=COLOR_02)
    df.KDJ_K.plot(ax=ax3,color=COLOR_01)

    x=np.linspace(0,len(df.htg)-1,len(df.htg))
    ax2.fill_between(x,0,df.htg.tolist(),color=COLOR_LB)
    ax3.fill_between(x,50,80,color=COLOR_LB)
    ax3.fill_between(x,20,50,color=COLOR_LR)

    return ax1,ax2,ax3
    #plt.show()
def on_mousemove(event):
    #print (event.x,',',event.y)
    if not event.inaxes:return
    for l in mouse_vlines:
        l.set_xdata(round(event.xdata))
        plt.draw()

#remove everything but the first line2D in an axes
#because it is a mouse cursor associated w/ mouse event


def make_axes(num,host=None):
    axes=[]
    fig=plt.figure()
    cid=fig.canvas.mpl_connect('motion_notify_event',on_mousemove)
    if host is not None:
        try:
            fig.canvas.mpl_connect('motion_notify_event',host.on_mouse_move)
        except: pass 

    for i in range(1,num+1):
        layout=(num*100)+10+i
        if i==1: ax=fig.add_subplot(layout)
        else: ax=fig.add_subplot(layout,sharex=axes[0])
        axes.append(ax)
        vline=ax.axvline(50,color='#aaaaaa')
        mouse_vlines.append(vline)
    plt.subplots_adjust(wspace=None, hspace=None)
    return axes,fig

def plot_curve_with_reverse(ax,se,color=None):
    l=ax.plot(se,color=color)
    color=l[0].get_color()
    up,dn=find_reverse(se)
    ax.scatter(up.index,up,color=color,marker='+')
    ax.scatter(dn.index,dn,color=color,marker='x')

def plot_dots(ax,se,color):
    ax.scatter(se.index,se,color=color)
def plot_dot_pairs(ax,se1,se2,colors=['r','g']):
    plot_dots(ax,se1,colors[0])
    plot_dots(ax,se2,colors[1])



def plot_price(ax,df):
    print('plot_price called')
    df.close.plot(ax=ax,color=COLOR_01)
    #df.ema12.plot(ax=ax,color=COLOR_02)
    #df.ema26.plot(ax=ax,color=COLOR_03)
def plot_MACD(ax,df,names=['macd','signal','htg'],color=None):
    if color is not None:
        c1=color[0]
        c2=color[1]
        c3=color[2]
    else:
        c1=COLOR_01
        c2=COLOR_02
        c3=COLOR_03

    macd=df[names[0]]
    signal=df[names[1]]
    htg=df[names[2]]

    signal.plot(ax=ax,color=c3)
    macd.plot(ax=ax,color=c2)
    htg.plot(ax=ax,color=c1)

    ax.fill_between(df.index,0,df[names[2]].tolist(),color=COLOR_LB)
def plot_KDJ(ax,df,names=['k','d','j']):
    k=df[names[0]]
    d=df[names[1]]
    j=df[names[2]]

    j.plot(ax=ax,color=COLOR_03)
    d.plot(ax=ax,color=COLOR_02)
    k.plot(ax=ax,color=COLOR_01)

    ax.fill_between(k.index,50,80,color=COLOR_LB)
    ax.fill_between(k.index,20,50,color=COLOR_LR)

def plot_day_with_macdroc(df):
    fig=plt.figure()
    ax1=fig.add_subplot(411)
    ax2=fig.add_subplot(412,sharex=ax1)
    ax3=fig.add_subplot(413,sharex=ax1)
    ax4=fig.add_subplot(414,sharex=ax1)
    #ax4=fig.add_subplot(414,sharex=ax1)

    #plot candle stick
    #candlestick2_ohlc(ax1,df.open,df.high,df.low,df.close,width=0.6,colorup=COLOR_UP,colordown=COLOR_DN,alpha=1.0)

    #print (df.date)
    def formatter(x,pos=None):
        i=int(x)
        if i<len(df.date): return df.date[i]
        
        return 0

    ax3.xaxis.set_major_formatter(ticker.FuncFormatter(formatter))

    
    df.ema26.plot(ax=ax1,color=COLOR_03)
    df.ema12.plot(ax=ax1,color=COLOR_02)
    df.close.plot(ax=ax1,color=COLOR_01)

    df.signal.plot(ax=ax2,color=COLOR_03)
    df.macd.plot(ax=ax2,color=COLOR_02)
    df.htg.plot(ax=ax2,color=COLOR_01)

    #macd_roc=get_moving_roc(df.macd,1)
    #htg_roc=get_moving_roc(df.htg,1)
    macd_roc=df.macd-df.macd.shift()
    htg_roc=df.htg-df.htg.shift()


    macd_roc.plot(ax=ax3,color=COLOR_02)
    htg_roc.plot(ax=ax3,color=COLOR_01)

    #df.KDJ_RSV.plot(ax=ax3,color='r')
    df.j.plot(ax=ax4,color=COLOR_03)
    df.d.plot(ax=ax4,color=COLOR_02)
    df.k.plot(ax=ax4,color=COLOR_01)


    x=np.linspace(0,len(df.htg)-1,len(df.htg))
    #ax4.bar(df.volume.index,df.volume,color=COLOR_01)
    ax2.fill_between(x,0,df.htg.tolist(),color=COLOR_LB)
    ax3.fill_between(x,0,htg_roc.tolist(),color=COLOR_LB)
    ax4.fill_between(x,50,80,color=COLOR_LB)
    ax4.fill_between(x,20,50,color=COLOR_LR)

    return ax1,ax2,ax3,ax4
    #plt.show()

def plot_day_macd_schemes(df):
    fig=plt.figure()
    ax1=fig.add_subplot(411)
    ax2=fig.add_subplot(412,sharex=ax1)
    ax3=fig.add_subplot(413,sharex=ax1)
    ax4=fig.add_subplot(414,sharex=ax1)

    df.close.plot(ax=ax1,color=COLOR_01)
    
    df.ema26.plot(ax=ax1,color=COLOR_03)
    df.ema12.plot(ax=ax1,color=COLOR_02)

    df.signal.plot(ax=ax2,color=COLOR_03)
    df.macd.plot(ax=ax2,color=COLOR_02)
    df.htg.plot(ax=ax2,color=COLOR_01)

    #MACD for 5-10
    macd_5,signal_5,htg_5=get_MACD(df.close,[5,10,9])
    ax3.plot(signal_5,color=COLOR_03)
    ax3.plot(macd_5,color=COLOR_02)
    ax3.plot(htg_5,color=COLOR_01)



    #ratio version of MACD
    macd_r,signal_r,htg_r=get_MACD_ratio(df.close)
    ax4.plot(signal_r,color=COLOR_03)
    ax4.plot(macd_r,color=COLOR_02)
    ax4.plot(htg_r,color=COLOR_01)

    x=np.linspace(0,len(df.htg)-1,len(df.htg))
    ax2.fill_between(x,0,df.htg.tolist(),color=COLOR_LB)
    ax3.fill_between(x,0,htg_5.tolist(),color=COLOR_LB)
    ax4.fill_between(x,0,htg_r.tolist(),color=COLOR_LB)



def fill_df_MACD(df=None,params=None,names=['macd','signal','htg']):
    if df is None: return None
    if len(df.index)<40: 
        #print("index length=%d <40, return None"%len(index))
        return None
    #df=df.sort_index(ascending=True)
    
    if params is None: params=MACD_STD_PARAMS

    close=df.close
    ema1=pd.ewma(close,span=params[0])
    ema2=pd.ewma(close,span=params[1])

    macd=ema1-ema2
    signal=pd.ewma(macd,span=params[2])
    htg=macd-signal

    df['ema'+str(params[0])]=ema1
    df['ema'+str(params[1])]=ema2
    df[names[0]]=macd
    df[names[1]]=signal
    df[names[2]]=htg

    return df
def fill_df_MACD_ratio_com(df=None,params=None,names=['macd','signal','htg']):
    if df is None: return None
    if len(df.index)<40: 
        #print("index length=%d <40, return None"%len(index))
        return None
    #df=df.sort_index(ascending=True)
    
    if params is None: params=MACD_STD_PARAMS
    
    close=df.close
    ema1=pd.ewma(close,params[0])
    ema2=pd.ewma(close,params[1])

    macd=(ema1-ema2)/ema2*100
    signal=pd.ewma(macd,params[2])
    htg=macd-signal

    df['ema'+str(params[0])]=ema1
    df['ema'+str(params[1])]=ema2
    df[names[0]]=macd
    df[names[1]]=signal
    df[names[2]]=htg
    return df

def fill_df_MACD_ratio(df=None,params=None,names=['macd','signal','htg'],base_value='close'):
    if df is None: return None
    if len(df.index)<40: 
        #print("index length=%d <40, return None"%len(index))
        return None
    #df=df.sort_index(ascending=True)
    
    if params is None: params=MACD_STD_PARAMS
    
    close=df[base_value]
    ema1=pd.ewma(close,span=params[0])
    ema2=pd.ewma(close,span=params[1])

    macd=(ema1-ema2)/ema2*100
    signal=pd.ewma(macd,span=params[2])
    htg=macd-signal

    df['ema'+str(params[0])]=ema1
    df['ema'+str(params[1])]=ema2
    df[names[0]]=macd
    df[names[1]]=signal
    df[names[2]]=htg
    return df
def fill_df_MACD_normalratio(df=None,params=None,names=['macd','signal','htg']):
    if df is None: return None
    if len(df.index)<40: 
        #print("index length=%d <40, return None"%len(index))
        return None
    #df=df.sort_index(ascending=True)
    if params is None: params=MACD_STD_PARAMS
    pos_scale=1
    neg_scale=1
    
    close=df.close
    ema1=pd.ewma(close,span=params[0])
    ema2=pd.ewma(close,span=params[1])

    macd=(ema1-ema2)/ema2*100
    signal=pd.ewma(macd,span=params[2])
    htg=macd-signal

    macd_max=macd.max()
    macd_min=macd.min()

    pos_scale=abs(1/macd_max)
    neg_scale=abs(1/macd_min)

    macd=macd.map(lambda x :x*neg_scale if x<0 else x*pos_scale)
    signal=signal.map(lambda x :x*neg_scale if x<0 else x*pos_scale)
    htg=htg.map(lambda x :x*neg_scale if x<0 else x*pos_scale)


    #df['ema'+str(params[0])]=ema1
    #df['ema'+str(params[1])]=ema2
    df[names[0]]=macd
    df[names[1]]=signal
    df[names[2]]=htg
    return df
def fill_df_reverse(df,se,nameup,namedown):
    up,dn=find_reverse(se)
    df[nameup]=up
    df[namedown]=dn
    return df
def fill_df_cross_zero(df,se,nameup,namedown):
    up,dn=find_cross_zero(se)
    df[nameup]=up
    df[namedown]=dn
    return df
      
def fill_df_KDJ(df,param=[9,2],names=['k','d','j']):
    if type(df)==type(None): return None
    if len(df.index)<10: 
        #print("index length=%d <40, return None"%len(index))
        return None
    roll_low=pd.rolling_min(df.low,param[0])
    #roll_low.fillna(value=pd.expanding_min(df.low),inplace=True) #ask chiu
    roll_high=pd.rolling_max(df.high,param[0])
    #roll_high.fillna(value=pd.expanding_min(df.high),inplace=True) #ask chiu
    roll_dif=roll_high-roll_low
    rsv=(df.close-roll_low)/(roll_dif)*100
    #print(rsv)
    #df['KDJ_RSV']=rsv
    k=pd.ewma(rsv,com=param[1]) #look up 'com'
    d=pd.ewma(k, com=param[1])
    j=3*k-2*d
    df[names[0]]=k
    df[names[1]]=d
    df[names[2]]=j
    return df

def find_se_cross(se1,se2):
    mask=se1>se2
    upcon=(mask==True)& (mask.shift()==False)
    dncon=(mask==False)& (mask.shift()==True)

    upcross=se1[upcon]
    dncross=se1[dncon]

    return upcross,dncross

def find_J_cross_zone(df,bot=20,top=80):
    #j_below=df.KDJ_J<bot
    #j_above=df.KDJ_J>top

    con1=(df.KDJ_J>=bot) & (df.KDJ_J.shift()<bot)
    con2=(df.KDJ_J<=top) & (df.KDJ_J.shift()>top)
    
    upcross=df.KDJ_J[con1]
    dncross=df.KDJ_J[con2]

    return upcross,dncross


def find_MACD_reverse(df):
    
    con1=df.htg.shift()-df.htg.shift(2)<0
    con2=df.htg-df.htg.shift()<0

    upcon=(con1==True)&(con2==False)
    dncon=(con1==False)&(con2==True)

    upreverse=df.htg[upcon]
    dnreverse=df.htg[dncon]

    return upreverse,dnreverse

def find_reverse(se):
    con1=se.shift()-se.shift(2)<0
    con2=se-se.shift()<0
    upcon=(con1==True)&(con2==False)
    dncon=(con1==False)&(con2==True)

    upreverse=se[upcon]
    dnreverse=se[dncon]

    return upreverse,dnreverse

def find_reverse_fit(se,length=12):
    up=pd.Series()
    dn=pd.Series()
    
    con1=se.shift()-se.shift(2)<0
    con2=se-se.shift()<0
    upcon=(con1==True)&(con2==False)
    dncon=(con1==False)&(con2==True)

    upreverse=se[upcon]
    dnreverse=se[dncon]

    return upreverse,dnreverse

def find_cross_zero(se):
    mask_d=(se<0)&(se.shift()>0)
    mask_u=(se>0)&(se.shift()<0)
    uc=se[mask_u]
    dc=se[mask_d]
    return uc,dc

def find_possible_cross_zero(se,length=2):
    roc_p=se.shift(length)-se.shift(length+1)
    roc=se-se.shift()

    mask_u=(roc_p>0)&(roc>0)&(se<0)&((se+roc)>0)
    mask_d=(roc_p<0)&(roc<0)&(se>0)&((se+roc)<0)

    uc=se[mask_u]
    dc=se[mask_d]
    return uc,dc

def get_MACD(se,params=[12,26,9]):
    ema1=pd.ewma(se,span=params[0])
    ema2=pd.ewma(se,span=params[1])
    macd=ema1-ema2
    signal=pd.ewma(macd,span=params[2])
    htg=macd-signal
    return macd,signal,htg
def get_MACD_ratio(se,params=[12,26,9]):
    ema1=pd.ewma(se,span=params[0])
    ema2=pd.ewma(se,span=params[1])
    macd=(ema1-ema2)/ema2*100
    signal=pd.ewma(macd,span=params[2])
    htg=macd-signal
    return macd,signal,htg

def get_up_stops(df):

    #up_stops=[i for i in df.p_change if i >=10]
    x=[]
    y=[]
    price=[]
    for i in range(len(df.p_change)):
        pc=df.p_change[i]
        if pc>=10 : 
            x.append(i)
            y.append(pc)
            price.append(df.close[i])
        #end if
    #end for

    return x,y,price

#find the adjacent index from a given index
#i.e: get_adjacent_index(45,df.close.index)
def get_adjacent_index(index,se):
    iprev=-1
    inext=-1
    for i in range(len(se)):

        if se[i]>index:
            inext=i
            return iprev,inext
        iprev=se[i]
    return iprev,inext


def get_list_interpolated_indice(set1,minDistFactor=0.01,iteration=5,offsetX=0):
    #recomend minDistFactor=0.01m iteration=10
    #print("set1.length=%d"%len(set1))
    outData=[]
    outX=[]
    outY=[]
    ix1=0
    ix2=len(set1)-1
    outData.append(ix1)
    outData.append(ix2)
    itr=0
    def getPts(srcPts,x1,x2,count):
        #print("count%d"%count)
        minDist=srcPts[x1]*minDistFactor
        if count<=0: return outData
        if(x2-x1<2): return outData
        maxDist=0
        x3=-1
        for i in range(x1+1,x2-1):              
            y1=srcPts[x1]
            y2=srcPts[x2]
            y0=srcPts[i]
            dist=getDistPtToLine(i,y0,x1,y1,x2,y2)
            #print('-cout:'+str(count),'x1:',x1,' y1:',y1,' x2:',x2,' y2:',y2,' x3:',i,' y3:',y3)
            if dist>maxDist and dist>minDist:
                maxDist=dist
                x3=i
        if x3>0 : 
            outData.append(x3)
            getPts(srcPts,x1,x3,count-1)
            getPts(srcPts,x3,x2,count-1)
        return

    getPts(set1,ix1,ix2,iteration)
    #print(outData)
    outNp=np.array(outData)
    outNp=np.sort(outNp)
    outData=outNp.tolist()

    for d in outData:
        outX.append(d+offsetX)
        outY.append(set1[d])

    return pd.Series(outY,index=outX)
def get_aligned_day_data(ref,subject):
    d=pd.DataFrame(ref.date)
    outdata=pd.merge(d,subject,how='left')
    return outdata

def get_list_valley(set1):
    outData=[];
    x=[]
    y=[]
    offset=2
    for i in range(offset , len(set1)-offset-1):
        u0=set1[i-offset]
        u1=set1[i]
        u2=set1[i+offset]
        if u0>u1 and u1<u2: 
            outData.append({'x':i,'y':u1})
            x.append(set1.index[i])
            y.append(u1)
    return pd.Series(y,index=x)
def get_list_peak(set1):
    outData=[];
    x=[]
    y=[]
    for  i in range(1 , len(set1)-1):
        u0=set1[i-1]
        u1=set1[i]
        u2=set1[i+1]
        if u0<u1 and u1>u2: 
            x.append(set1.index[i])
            y.append(u1)
    return pd.Series(y,index=x)
def getDistPtToLine(x0,y0,x1,y1,x2,y2):
    a=abs((y2-y1)*x0-(x2-x1)*y0+(x2*y1)-(y2*x1))
    b=math.sqrt( math.pow((y2-y1),2) + math.pow((x2-x1),2))
    return a/b

#returns concave or convex
def get_curve_form(se,i,test_length=3):
    if i<test_length: return 'unkown'
    if len(se)<i:return 'index out of range'
    p1=se[i]
    p2=se[i-5]
    imid=math.floor(i/2)
    p_middle=se[imid]
    p_compare=(p1-p2)*(imid/test_length)+p2

    if p_middle<p_compare : return 'convex'
    if p_middle>p_compare : return 'concave'

    return 'unkown'

def get_moving_roc(se,length=9):
    roc=se-se.shift()
    mroc=pd.ewma(roc,9)
    return mroc
def get_normalized_series(se):
    smax=se.max()
    smin=se.min()
    scalep=abs(1/smax)
    scalen=abs(1/smin)
    normalized=se.map(lambda x: x*scalep if x>0 else x*scalen)
    return normalized
def get_normalized_series_by_series(se,base):
    smax=se.max()
    smin=se.min()
    scalep=base/smax
    scalen=abs(base/smin)

    outData=pd.Series()
    for i in range(len(se)):
        if se[i]>0: d=se[i]*scalep[i]
        else: d=se[i]*scalen[i]
        outData.set_value(i,d)
    return outData
        


def get_boll(se,length=20,std_scale=2):
    series=se
    ave=pd.stats.moments.rolling_mean(series,length)
    std=pd.stats.moments.rolling_std(series,length)

    scaledStd=std*std_scale
    upBand=ave+scaledStd
    dnBand=ave-scaledStd

    ave=ave.fillna(-1)
    upBand=upBand.fillna(-1)
    dnBand=dnBand.fillna(-1)

    ave=np.round(ave,3).tolist()
    return ave,upBand,dnBand,std
def find_extrema(se, window=5, span_points=25):
        #df = pd.DataFrame({'x': mpl.dates.date2num(x), 'y': y})
        x=se.index
        y=se
        df = pd.DataFrame({'x': x, 'y': y})

        span = span_points/len(df)
        lo = stats.loess('y~x', df, span=span, na_action=stats.na_exclude)
        # we have to use predict(lo) instead of lo.rx2('fitted') here, the latter 
        # doesn't not include NAs
        fitted = pd.Series(pandas2ri.ri2py(stats.predict(lo)), index=df.index)
        max_ = pd.rolling_max(fitted, window, center=True)
        min_ = pd.rolling_min(fitted, window, center=True)

        df['fitted'] = fitted
        df['max'] = max_
        df['min'] = min_

        delta = max_ - fitted
        highs = df[delta<=0]
        delta = min_ - fitted
        lows = df[delta>=0]

        #globals()['fe_df'] = df
        #globals()['x'] = x
        #globals()['y'] = y
        #globals()['lows'] = lows
        #globals()['highs'] = highs

        return fitted, lows, highs

def count_weekdays(since, until):
    since_isoweekday = since.isoweekday() + 1
    return len([x for x in range(since_isoweekday,since_isoweekday + (until - since).days) if x % 7 not in [0, 6]])


def str2date(str):
    sap=str.split('-')
    y=int(sap[0])
    m=int(sap[1])
    d=int(sap[2])
    date=datetime.date(y,m,d)
    return date

class Trade():
    def __init__(self,bought=None,sold=None,feed_b=0.002,feed_s=0.002,id=0):
        if bought is not None:self.bought=bought 
        else: self.bought=-1
        if sold is not None:self.sold=sold 
        else: self.sold=-1

        self.feed_b=feed_b
        self.feed_s=feed_s
        self.profit=0
        self.profit_rate=0
        self.id=id
        self.max=0
        self.min=0

        self.buy_time=0
        self.sell_time=0

        if (bought is not None)&(sold is not None):
            self.bought=bought*(1+self.feed_b)
            self.sold=sold*(1-self.feed_s)
            self.profit=self.sold-seld.bought
            self.profit_rate=self.profit/self.bought

        
    def set_feed(feed_b=0.002,feed_s=0.002):
        self.feed_b=feed_b
        self.feed_s=feed_s
        return self

    def buy(self,price,time):
        bought=price*(1+self.feed_b)
        self.bought=bought
        self.buy_time=time
        self.max=price
        self.min=price
        return self

    def sell(self,price,time):
        self.sold=price*(1-self.feed_s)
        self.profit=self.sold-self.bought
        self.profit_rate=self.profit/self.bought
        self.sell_time=time
        return self

    def log(self):
        print('Trade %3d b%-5.2f|s%-5.2f p%-8.2f|r%5.2f%%(%5.2f%%)'%(self.id,self.bought,self.sold,self.profit,self.profit_rate*100,self.profit_rate*100/360*(self.sell_time-self.buy_time)))
        return self

    def plot(self,ax):
        if (self.bought is not None )&(self.sold is not None):
            ax.scatter([self.buy_time],[self.bought],color='r',s=250,alpha=0.3)
            ax.scatter([self.sell_time],[self.sold], color='g',s=250,alpha=0.3)


