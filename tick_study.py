import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import tushare as ts
from ts_util import *

df=ts.get_tick_data('002730','2016-05-05')
df=df.sort_index(ascending=False)
df=df.reset_index()
df=fill_df_MACD_ratio(df,base_value='price')

def accum(se,window=20):
    s=pd.Series()
    for i in range(window,len(df.volume)):
        x=i
        sub=0 if i-window<0 else i-window 
        sum=se[sub:i].sum()
        s.set_value(x,sum)
    return s
sv60=pd.rolling_sum(df.volume,window=20)
sv90=pd.rolling_sum(df.volume,window=30)
sv120=pd.rolling_sum(df.volume,window=40)

print(df)
axes,fig=make_axes(3)

axes[0].plot(df.price,color=COLOR_01)
plot_MACD(axes[1],df)

axes[2].plot(df.volume)
axes[2].plot(sv60,color=COLOR_01)
axes[2].plot(sv90)
axes[2].plot(sv120)
axes[2].plot(pd.ewma(sv60,span=5),color=COLOR_01)

#print(df)

plt.show()
