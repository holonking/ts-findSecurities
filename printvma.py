import tushare as ts
import pandas as pd
from ts_util import *
import matplotlib.pyplot as plt


def main():
    connect_db('day_stock.db')
    #for i in range(600000,600120):
    
    printOne('002572')

def printOne(sec_num):    
    #df=ts.get_hist_data('600000')
    #df=load_sec_from_db_date('sec_num','2014-01-01','2016-01-01')
    df=load_sec_from_ts_date(sec_num,'2012-01-01','2016-04-25')
    if df is None: return
    for name in ['ma10','ma20','v_ma10','v_ma20']:
        if name.find('v')>=0:
            color=COLOR_01
        else:
            color=COLOR_03
        uname='u'+name
        max=df[name].max()
        df[uname]=df[name]/max
        plt.plot(df[uname],alpha=1,color=color)
    #end for
    

if __name__ == '__main__':
    main()
    plt.show()
