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
	if type(con)==type(None) or type(cur)==type(None):
		con=sqlite3.connect('stock.db')
		cur=con.cursor()

def read_ticks_sql(sec_num='600000',date='2016-03-29'):
	connect_DB()
	command="select * from tick_data where sec_num=%s and date='%s' "%(str(sec_num),str(date))
	df=pd.read_sql(command,con)
	if len(df.index)<=0: return None
	return df

def cal_tick_df(df):
	if len(df.index)<40: 
		#print("index length=%d <40, return None"%len(index))
		return None

	df=df.sort_index(ascending=True)
	df.loc[ df.type=='卖盘','volume']*=-1

	price=df.price
	ema12=[]
	ema26=[]
	macd=[]
	signal=[]
	htg=[]

	for i in range(3):
		ema12.append(pd.ewma(price,12*EWMA_TIME_SCALE[i]))
		ema26.append(pd.ewma(price,26*EWMA_TIME_SCALE[i]))
		macd.append(ema12[i]-ema26[i])
		signal.append(pd.ewma(macd[i],9*EWMA_TIME_SCALE[i]))
		htg.append(macd[i]-signal[i])
		
		df['ema12_%d'%i]=ema12[i]	
		df['ema26_%d'%i]=ema26[i]	
		df['macd_%d'%i]=macd[i]	
		df['signal_%d'%i]=signal[i]	
		df['htg_%d'%i]=htg[i]	

	return df


def cal_recent_df(df):
	if len(d.index)<40: 
		#print("index length=%d <40, return None"%len(index))
		return None
	df=df.sort_index(ascending=True)
	
	price=df.price
	ema12=pd.ewma(price,12)
	ema26=pd.ewma(price,26)

	macd=ema12-ema26
	signal=pd.ewma(macd,9)
	htg=macd-signal

	df['ema12']=ema12
	df['ema26']=ema26
	df['macd']=macd
	df['signal']=signal
	df['htg']=htg

	return df

def plot(df):
	fig=plt.figure()
	ax1=fig.add_subplot(311)
	ax2=fig.add_subplot(312,sharex=ax1)
	ax3=fig.add_subplot(313,sharex=ax1)

	ax1.plot(df.price.tolist(),color=COLOR_STEELBLUE)
	ax1.plot(df.ema12_1.tolist(),color=COLOR_EMA12)
	ax1.plot(df.ema26_1.tolist(),color=COLOR_EMA26)

	ax2.plot(df.htg_1.tolist())
	ax2.plot(df.macd_1.tolist())
	ax2.plot(df.signal_1.tolist())


	x=np.linspace(0,len(df.htg_1)-1,len(df.htg_1))
	ax2.fill_between(x,0,df.htg_1.tolist(),color="#aaaaaa")

	plt.show()

def run1():
	df=read_ticks_sql()
	df=cal_tick_df(df)
	plot(df)

if __name__ == '__main__':
	run1()