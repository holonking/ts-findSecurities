import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sqlite3 
import threading
import time
import queue
from sqlalchemy import create_engine


threads=[]
thread_complete=[]
q=queue.Queue()
q_sec_num=queue.Queue()


engine = create_engine('sqlite:///test.db')
def insert_db(df):
    df.to_sql('tick_data', engine, if_exists='append')

def connect_DB():
	global con,cur
	if con==None or cur==None:
		con=sqlite3.connect('stock.db')
		cur=con.cursor()
def read_ticks(sec_num,date):
	#print("read tick %s--------------------"%str(sec_num))
	df=ts.get_tick_data(str(sec_num),str(date))
	if type(df)==type(None): return None
	if len(df.index)<100: return None
	if df.time[0]=='alert("当天没有数据");' : 
		print("%S failed to retrieve"%str(sec_num))
		return None
	#print("<<got df>>")
	df.insert(0,'date',str(date))
	df.insert(0,'sec_num',str(sec_num))
	q.put(df,500)
	#df.to_sql('tick_data',con,if_exists='append')
	#print("%s, %s, %d entries added to database"%(str(sec_num),str(date),len(df.index)))
	return df
def fetcher(thread_id,days=900):
	if days<1 :
		print('must input more than one day')
		return None

	while q_sec_num.qsize()>0 :
		sec_num=q_sec_num.get()
		today=datetime.date.today()
		for i in range(1,days):
			delta=delta=datetime.timedelta(days=i)
			xday=today-delta
			print("T-%-2d fetch %s %s"%(thread_id,str(sec_num),str(xday)) )
			df=read_ticks(sec_num,xday)
			#if type(df)==type(None): break 
			#time.sleep(delay)

	thread_complete[thread_id]=True
	print("thread %d complete"%thread_id)
	#threading.currentThread().exit()

def all_threads_complete():
	for i in thread_complete:
		if i==False: return False
	return True
def get_queue():
	collect_count=0
	con=sqlite3.connect('stock.db')
	cur=con.cursor()
	con1=True

	while con1==True :
		#print("consume")
		if q.qsize()>0:
			df=q.get()
			collect_count+=1
			insert_db(df)
			#print("%s, %s, %d entries added to database"%(str(df.sec_num[0]),str(df.date[0]),len(df.index)))
			print("-> queue size = %d collectd %d"%(q.qsize(),collect_count))

		if all_threads_complete()==False: 
			con1=True
		elif all_threads_complete() and q.qsize()>0:
			con1=True
		else:
			con1=False

	print ("all threads completed and got %d data"%collect_count)


def run1():
	#cur.execute("drop table tick_data")
	first_num=0
	

	#queue all security names
	start=0
	end=3000
	for i in range(start,end+1):
		sec_num=600000+i
		q_sec_num.put(sec_num)


	threadTotal=3 #20
	try:
		#start producer thread
		for i in range(threadTotal):
			thread_complete.append(False)
			t=threading.Thread(target=fetcher,args=(i,900))
			t.deamon=True
			t.start()

		#consumer thread
		t=threading.Thread(target=get_queue)
		t.deamon=False
		t.start()

	except :
		print('unable to start thread')



	#end for
		
def run2():
	sday=datetime.date(2016,3,30)
	read_ticks('600000',sday)


if __name__ == '__main__':

	run1()