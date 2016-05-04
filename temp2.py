import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
import pandas as pd
from ts_util import *

def format(f):
    return '%3.2f'%f

#pd.set_option('float_format',format)
#pd.set_option('display.max_rows',101)
#pd.set_option('display.width',1000)

#df=ts.get_hist_data('600000','2015-01-01','2016-01-01')
connect_db('day_stock.db')
df=load_sec_from_db_date('600000','2015-01-01','2016-01-01')
print(df.loc[0:5])
df=df.set_index('date',drop=True)
df=df.sort_index(ascending=True)
df=df.reset_index()
print(df.loc[0:5])
close=df.close

#print(df)

