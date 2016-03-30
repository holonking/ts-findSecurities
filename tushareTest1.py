
import tushare as ts
import pandas as pd
import numpy as np
import datetime,calendar
import matplotlib.pyplot as plt
import matplotlib.animation as animation



def loadSec(secNum,days):
	print("fetching %s"%str(secNum))
	today=datetime.date.today()
	delta=datetime.timedelta(days=days)
	xday=today-delta
	strDs=str(xday)
	strDe=str(today)

	#get 30 days(requres >9 days) of data
	d=ts.get_hist_data(str(secNum),start=strDs,end=strDe)
	if type(d)==type(None) :return None
	if len(d)<days : return None
	#calculate MACD histogram
	macd=d.ma10-d.ma20
	Rmacd=macd.sort_index(ascending=True)
	Rsignal=pd.ewma(Rmacd,9)
	signal=Rsignal.sort_index(ascending=False)
	htg=macd-signal

	#add macd to te dataframe
	d['macd']=macd
	d['signal']=signal
	d['htg']=htg

	#print(d)

	#get the nearest valley
	if htg[0]-htg[1] >0: 
		nearestValley=getNearestValley(htg)
		if nearestValley>0: 
			print("last valley at %s"%d.index[nearestValley])
			return secNum,nearestValley,d.index[nearestValley],"valley"
	elif htg[0]-htg[1] <0: 
		nearestPeak=getNearestPeak(htg)
		if nearestPeak>0: 
			print("last peak at %s"%d.index[nearestPeak])
			return secNum,nearestPeak,d.index[nearestPeak],"peak"
	return None

#end def loadSec

def getNearestValley(s):
	for i in range(len(s)-1):
			d=s[i]-s[i+1]
			if d<0: 
				return i
	return -1
def getNearestPeak(s):
	for i in range(len(s)-1):
			d=s[i]-s[i+1]
			if d>0: 
				return i
	return -1
def getdf(d):
	if len(d.index)<40: 
		#print("index length=%d <40, return None"%len(index))
		return None
	df=d.sort_index(ascending=True)
	
	close=df.close
	ema12=pd.ewma(close,12)
	ema26=pd.ewma(close,26)

	macd=ema12-ema26
	signal=pd.ewma(macd,9)
	htg=macd-signal

	df['ema12']=ema12
	df['ema26']=ema26
	df['macd']=macd
	df['signal']=signal
	df['htg']=htg

	return df

def getFeatures(df):
	df=df.sort_index(ascending=False)
	valley=-1
	peak=-1
	upCross=-1
	dnCross=-1
	d=0
	dl=0
	#print(df)
	span=len(df.index)
	#print("span=%d"%span)
	if span>40: span=20
	for i in range(1,span-1):
		d=df.htg[i]-df.htg[i+1]
		dl=df.htg[i-1]-df.htg[i]
	

		#find first valley
		if valley<0:
			if df.htg[i]<0 and dl>0 and d<0: 
				#print ("found valley at %d h[i]=%f, d=%f, dl=%f"%(i,df.htg[i],d,dl))
				valley=i
		#find first peak
		if peak<0:
			if df.htg[i]>0 and dl<0 and d>0: 
				peak=i
		#find upCross
		if upCross<0:
			if df.htg[i-1]>0 and df.htg[i]<=0 and df.htg[i+1]<0 : 
				#print("found upcross at %d h[i-1]=%f, h[i]=%f,h[i+1]%f"%(i,df.htg[i-1],df.htg[i],df.htg[i+1]))
				upCross=i
		#find dnCross
		if dnCross<0:
			if df.htg[i-1]<0 and df.htg[i]>=0 and df.htg[i+1]>0 : 
				dnCross=i
		
	return valley,peak,upCross,dnCross

def plot(df):
	fig=plt.figure()
	ax1=fig.add_subplot(211)
	ax2=fig.add_subplot(212,sharex=ax1)

	ax1.plot(df.close.tolist())
	ax1.plot(df.ema12.tolist())
	ax1.plot(df.ema26.tolist())
	ax2.plot(df.htg.tolist())
	ax2.plot(df.macd.tolist())
	ax2.plot(df.signal.tolist())
	x=np.linspace(0,len(df.htg)-1,len(df.htg))
	ax2.fill_between(x,0,df.htg.tolist(),color="#aaaaaa")

	plt.show()
	
def getSecAndPlot(secNum,days=90):
	today=datetime.date.today()
	delta=datetime.timedelta(days=days)
	xday=today-delta
	strDs=str(xday)
	strDe=str(today)
	d=ts.get_hist_data(str(secNum),start=strDs,end=strDe)
	if type(d)==type(None):
		print('nothing retrieved')
		return None
	print("data length=%d"%len(d.index))
	#print(d.close)
	df=getdf(d)
	if type(df)==type(None) : return None
	print(df)
	plot(df)
def getSec(secNum,days=90):
	today=datetime.date.today()
	delta=datetime.timedelta(days=days)
	xday=today-delta
	strDs=str(xday)
	strDe=str(today)
	d=ts.get_hist_data(str(secNum),start=strDs,end=strDe)
	if type(d)==type(None):
		print('nothing retrieved')
		return None
	#print("data length=%d"%len(d.index))
	#print(d.close)
	df=getdf(d)
	if type(df)==type(None) : return None
	return df

def run1():
	outData=[]
	outSec=[]
	outV=[]
	outP=[]
	outU=[]
	outD=[]
	outDf=pd.DataFrame()

	ndays=3
	for i in range(0,3000):
		secNum=600000+i
		arrData=getSec(600000+i)
		if type(arrData)!=type(None): 
			features=getFeatures(arrData)
			v,p,u,d=features	
			print("fetching"+str(secNum)+" u="+str(u))
			if u>0 and u<ndays:
				out=secNum,u
				outData.append(out)
				outV.append(v)
				outP.append(p)
				outU.append(u)
				outD.append(d)
				outSec.append(secNum)

				print("found %s v:%-3d  ,p:%-3d  ,u:%-3d  ,d:%-3d"%(str(secNum),v,p,u,d) )

			#end if
		#end if
	#end for

	outDf['secNum']=outSec
	outDf['v']=outV
	outDf['p']=outP
	outDf['u']=outU
	outDf['d']=outD
	print(outDf)
	outDf.to_csv('daily.csv')

	#end for i

	for d in outData:
		secNum,u=d
		print("%s - %3ddays"%(str(secNum),u))

def run2(secNum,days=90):
	df=getSec(secNum,days)
	dfR=df.sort_index(ascending=False)
	features=getFeatures(df)
	v,p,u,d=features


	print(df.htg)
	print("v:%-3d(%s)  ,p:%-3d(%s)  ,u:%-3d(%s)  ,d:%-3d(%s)"%(v,dfR.index[v],p,dfR.index[p],u,dfR.index[u],d,dfR.index[d]) )
	#plot(df)

if __name__ == '__main__':
	#run2(600711)
	run1()
	






