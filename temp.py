import numpy as np
import pandas as pd
import tushare as ts
import random as rnd

class C:
    def __init__(self,s):
        self.num=100
        self.score=s
    def run(self):
        print('my score is ',self.score)

def main():        
    subjects=pd.Series()
    for i in range(0,10):
        score=rnd.randint(0,20)
        c=C(score)
        subjects.set_value(score,c)
    print(subjects)

    os=subjects.sort_index(ascending=False)
    os=os.reset_index()
    print(os)
    print(os[0][0].run())




if __name__ == '__main__':
    main()