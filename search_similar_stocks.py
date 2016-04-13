import threading
import queue
import re
import multiprocessing as mp
import numpy as np
import pandas as pd
import arrow
from sqlalchemy import create_engine
import tushare as ts
from ts_util import *

N_THREADS = 20
start_date = '2013-03-29'
end_date = '2016-03-29'
sec_start=600000
sec_end=600100
df_list=[]
DB_FILE='day_stock.db'
engine = create_engine('sqlite:///' + DB_FILE)

def _make_jobs(q_job):
    # generate stocks codes
    stocks = list(map('{:06d}'.format, range(sec_start,sec_end)))
    #stocks = [s for s in stocks if symbol_is_stock(s)]
    print (stocks)
    for stock in stocks:
            q_job.put(stock)

def _mp_read(i,q_job,q_res,e_end):
    print('start process'+str(i))
    while not e_end.is_set():
        try:
            sec_num=q_job.get(timeout=0.1)
            print('reading %s'%str(sec_num))
            df=ts.get_hist_data(sec_num,start_date,end_date)
            df=fill_df_MACD_ratio(df)
            df=fill_df_KDJ(df)
            if type(df)==type(None): continue
            q_res.put(df)
        except queue.Empty:continue
        q_job.task_done()
    return

def _mp_write(q_res,e_end):
    while not e_end.is_set():
        try:
            df=q_res.get()
            df_list.append(df)
            print("got %d data"%len(df_list))
        except queue.Empty:continue
        q_res.task_done()
    return


def main():
    q_job=mp.JoinableQueue()
    q_res=mp.JoinableQueue()

    e_end=mp.Event()
    arr_process_read=[]
    _make_jobs(q_job)

    for i in range(N_THREADS):
        print(' flag 4'+str(i))
        process_read = mp.Process(target=_mp_read, args=(i, q_job,q_res,e_end))
        process_read.start()
        arr_process_read.append(process_read)

    process_write=mp.Process(target=_mp_write,args=(q_res,e_end))
    process_write.start()

    q_job.join()
    q_res.join()
    e_end.set()

    process_write.join()
    [p.join for p in arr_process_read]
    print('all processes completed')

    out_df=pd.concat(df_list)
    out_df.to_csv('')







if __name__ == '__main__':
    main()