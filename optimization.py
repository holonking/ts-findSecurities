import random as rnd
import pandas as pd
import matplotlib.pyplot as plt
from strategy01 import strategy_day_01 as stg
import tushare as ts
from ts_util import *
#params:
#params[0] int      0-5         buy feature range 01 
#params[1] int      0-5         buy feature range 02
#params[2] int      0-5         sell feature range 01
#params[3] int      0-5         sell feature range 02
#params[4] float    0.01-0.5    buy_macd_roc_reverse
#params[5] float    0.01-0.5    sell_macd_roc_reverse
THRESH_01=0
THRESH_02=4
THRESH_03=0.01
THRESH_04=0.3
THRESH_MT=0.3 # dictates mutation

NUM_SUBJECTS=10
NUM_SELECT=2

class Subject:
    def __init__(self,params):
        self.params=params
        self.score=0

def make_randomize_params():
    params=[]
    #params:
    #params[0] int      0-5         buy feature range 01 
    #params[1] int      0-5         buy feature range 02
    #params[2] int      0-5         sell feature range 01
    #params[3] int      0-5         sell feature range 02
    #params[4] float    0.01-0.5    buy_macd_roc_reverse
    #params[5] float    0.01-0.5    sell_macd_roc_reverse
    params.append(rnd.randint(THRESH_01,THRESH_02))
    params.append(rnd.randint(THRESH_01,THRESH_02))
    params.append(rnd.randint(THRESH_01,THRESH_02))
    params.append(rnd.randint(THRESH_01,THRESH_02))
    params.append(rnd.uniform(THRESH_03,THRESH_04))
    params.append(rnd.uniform(THRESH_03,THRESH_04))
    return params

def trade(subject):
    score=0
    for p in subject.params:
        score+=p
    subject.score=score
    return 

def random_gen():
    
    best_score=0
    best_params=[]
    scores=[]
    stg1=stg()

    sec_num='600000'
    df=load_sec_from_ts_date(sec_num,'2015-04-01','2016-04-01')
    df=fill_df_MACD_ratio(df)
    df=fill_df_KDJ(df)


    for i in range(1000):
        s=Subject(make_randomize_params())
        stg1.params=s.params
        s.score=stg1.run(sec_num,draw=False,log=False,df=df)
        print(i,' score:',s.score,s.params)
        if(s.score>best_score):
            best_score=s.score
            scores.append(best_score)
            best_params=s.params
            print(i,' score:',s.score,s.params,'---------------------')

    print('best params are :',best_params)
    plt.plot(scores)
    plt.show()

def main():
    #enironment()
    random_gen()

if __name__ == '__main__':
    main()





