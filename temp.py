import matplotlib.pyplot as plt
import numpy as np
import tushare as ts
from ts_util import *

#df=ts.get_hist_data('600000','2015-01-01','2016-01-01')
connect_db('day_stock.db')
df=load_sec_from_db_date('600000','2015-01-01','2016-01-01')
close=df.close


T = 2
mu = 0.1
sigma = 0.01
S0 = 20
dt = 0.01
N = round(T/dt)
#t = np.linspace(0, T, N)
t=df.index
w=np.array(close.tolist())
print (w)
#w = np.random.standard_normal(size = N) 
W = np.cumsum(w)*np.sqrt(dt) ### standard brownian motion ###
X = (mu-0.5*sigma**2)*t + sigma*W 
S = S0*np.exp(X) ### geometric brownian motion ###
plt.plot(t,w)
#plt.plot(t,S)
plt.show()