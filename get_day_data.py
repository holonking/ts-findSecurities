import threading
import queue
import re
import multiprocessing as mp
import numpy as np
import pandas as pd
import arrow
from sqlalchemy import create_engine
import tushare as ts
import traceback


N_THREADS = 10
start_date = '2013-03-29'
end_date = '2016-03-29'
sec_start=600000
sec_end=604000
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
def _insert_db(df):
    df.to_sql('day_data', engine, if_exists='append')
def _mp_read(i,q_job,q_res,e_end):
    print('+----start process'+str(i))
    while not e_end.is_set():
    #while not q_job.empty():
        #print('- - -')
        try:
            sec_num=q_job.get(timeout=0.1)
        except queue.Empty:
            continue

        print('reading %s'%str(sec_num))
        df=ts.get_hist_data(sec_num,start_date,end_date)
        if df is None:
            q_job.task_done()
        else:
            df.insert(0, 'stock', sec_num)
            q_res.put(df)
            q_job.task_done()
    print('process '+str(i)+' completed')

    

def _mp_write(q_job,q_res,e_end):
    while not e_end.is_set():
    #while not q_job.empty()&q_res.empty():
        #print('+ + +')
        try:
            df=q_res.get(timeout=0.1)
            print("got %d data"%len(df_list))
        except queue.Empty:
            continue
        except Exception:
            traceback.print_exc()
        q_res.task_done()
        _insert_db(df)
        #df_list.append(df)
    print('writer complete')

def get_stocks():
    df_list=[]
    q_job=mp.JoinableQueue()
    q_res=mp.JoinableQueue()

    e_end=mp.Event()
    arr_process_read=[]

    _make_jobs(q_job)

    for i in range(N_THREADS):
        print(' flag 4 '+str(i))
        process_read = mp.Process(target=_mp_read, args=(i, q_job,q_res,e_end))
        process_read.start()
        arr_process_read.append(process_read)

    process_write=mp.Process(target=_mp_write,args=(q_job,q_res,e_end))
    process_write.start()




    q_job.join()
    print('q_job done')
    q_res.join()
    print('q_res done')
    e_end.set()

    [p.join() for p in arr_process_read]
    print("total df read=%d"%len(df_list))
    process_write.join()

    #out_df=pd.concat(df_list)
    #_insert_db(out_df)
    #print("concatinated df length%d="%len(out_df.index))
    #print(out_df)

    print('all processes completed')

    #print(out_df)


def main():
    get_stocks()






if __name__ == '__main__':
    main()