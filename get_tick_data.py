import threading
import queue
import re
import multiprocessing as mp
import numpy as np
import pandas as pd
import arrow
from sqlalchemy import create_engine
import tushare as ts


DB_FILE = 'test.db'
N_THREADS = 2

queue_count=0
collected_count=0
engine = create_engine('sqlite:///' + DB_FILE)



def _is_no_data(df):
   return df.time[0] == 'alert("当天没有数据");'

def _download_data(stock, date):
    df = ts.get_tick_data(stock, date)
    return df

def _make_jobs(q_job,istart,iend):
    # generate date range
    start_date = '2015-01-29'
    end_date = '2015-01-30'
    date_range = arrow.Arrow.range('day',
            arrow.get(start_date), arrow.get(end_date))
    date_range = [date.format('YYYY-MM-DD') for date in date_range]

    # generate stocks codes
    stocks = list(map('{:06d}'.format, range(istart,iend)))
    stocks = [s for s in stocks if symbol_is_stock(s)]

    for stock in stocks:
        for date in date_range:
            q_job.put((stock, date))

def insert_db(df):
    df.to_sql('tick_data', engine, if_exists='append')

def symbol_is_stock(symbol):
    if not re.match('\d{6}', symbol):
        return False
    else:
        start = symbol[:3]
        if start in ['000', '001', '002', '300',
                '600', '601', '603']:
            return True
        else:
            return False

def get_stocks(istart,iend):
    def fetcher_thread(id_, q_job, q_res, e_end):
        print("starting fetcher {}".format(id_))
        while not e_end.is_set() :
            try:
                stock, date = q_job.get(timeout=0.1)
            except queue.Empty:
                continue
            print("fetching {}, {}".format(stock, date))
            df = _download_data(stock, date)
            # TODO: handle other errors, retry if necessary
            if not _is_no_data(df):
                q_res.put((stock, date, df))
            q_job.task_done()
        print("fetcher {} exited".format(id_))

    def writer_thread(q_res):
        print("starting writer")
        while not e_end.is_set() :
            try:
                stock, date, df = q_res.get(timeout=0.2)
                global collected_count
                collected_count+=1
                print("-------queue size={} collected {}".format(queue_count,collected_count))
            except queue.Empty:
                continue
            df.insert(0, 'stock', stock)
            df.insert(0, 'date', date)
            #insert_db(df)
            q_res.task_done()            
            print("writing {}, {}".format(stock, date))
        print("writer exited")

    #q_job = queue.Queue()
    #q_res = queue.Queue(maxsize=100)
    q_job=mp.JoinableQueue()
    q_res=mp.JoinableQueue()

    #e_end = threading.Event()
    e_end=mp.Event()

    fetchers = []
    for i in range(N_THREADS):
        #t = threading.Thread(target=fetcher_thread, args=(i, q_job, q_res, e_end))
        t = mp.Process(target=fetcher_thread, args=(i, q_job, q_res, e_end))
        t.start()
        fetchers.append(t)

    #writer = threading.Thread(target=writer_thread, args=(q_res,))
    writer = mp.Process(target=writer_thread, args=(q_res,))
    writer.start()

    _make_jobs(q_job,istart,iend)

    q_job.join()
    q_res.join()

    e_end.set()
    writer.join()
    [t.join() for t in fetchers]


def main():
    get_stocks(600000,600020)
    #get_stocks(0,4000)

if __name__ == '__main__':
    main()



















