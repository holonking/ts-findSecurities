import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sqlite3 

con=sqlite3.connect('stock.db')
cur=con.cursor()

def connect_DB():
	global con,cur
	if con==None or cur==None:
		con=sqlite3.connect('stock.db')
		cur=con.cursor()


def read_ticks(sec_num,date):
	df=ts.get_tick_data(str(sec_num),str(date))
	if type(df)==type(None): return None
	if len(df.index)<100: return None
	if df.time[0]=='alert("当天没有数据");' : return None
	df.insert(0,'date',str(date))
	df.insert(0,'sec_num',str(sec_num))
	df.to_sql('tick_data',con,if_exists='append')
	print("%s, %s, %d entries added to database"%(str(sec_num),str(date),len(df.index)))

def run1():
	#cur.execute("drop table tick_data")

	today=datetime.date.today()
	for j in range(8,3000):
		for i in range(1,900):
			delta=delta=datetime.timedelta(days=i)
			xday=today-delta
		
			sec_num=600000+j
			read_ticks(sec_num,xday)

if __name__ == '__main__':
	run1()