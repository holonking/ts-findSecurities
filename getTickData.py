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


threads=[]
thread_complete=[]
q=queue.Queue()


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
def fetcher(thread_id,start_num=0,end_num=3000,days=900,delay=10):
	print("fetching...from %d to %d"%(start_num,end_num))
	if days<1 :
		print('must input more than one day')
		return None

	today=datetime.date.today()
	for j in range(start_num,end_num+1):
		sec_num=600000+j
		for i in range(1,days):
			delta=delta=datetime.timedelta(days=i)
			xday=today-delta
			#print("T-%-2d reading %s %s"%(thread_id, str(sec_num),str(xday)))
			df=read_ticks(sec_num,xday)
			if type(df)==type(None): break 
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
		if q.qsize()>0:
			df=q.get()
			collect_count+=1
			df.to_sql('tick_data',con,if_exists='replace')
			print("%s, %s, %d entries added to database"%(str(df.sec_num[0]),str(df.date[0]),len(df.index)))
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
	threadTotal=5 #20
	sec_num_each_thread=2#150
	try:
		#start producer thread
		for i in range(threadTotal):
			thread_complete.append(False

			start=i*sec_num_each_thread+first_num
			end=start+sec_num_each_thread

			t=threading.Thread(target=fetcher,args=(i,start,end,900))
			t.deamon=True
			t.start()

		#consumer thread
		t=threading.Thread(target=get_queue)
		t.deamon=False
		t.start()

	except :
		print('unable to start thread')

	while 1:
		pass

	#end for
		
def run2():
	sday=datetime.date(2016,3,30)
	read_ticks('600000',sday)


if __name__ == '__main__':

	run1()