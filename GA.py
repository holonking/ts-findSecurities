import random as rnd
import pandas as pd
import matplotlib.pyplot as plt

#params:
#params[0] int      0-5         buy feature range 01 
#params[1] int      0-5         buy feature range 02
#params[2] int      0-5         sell feature range 01
#params[3] int      0-5         sell feature range 02
#params[4] float    0.01-0.5    buy_macd_roc_reverse
#params[5] float    0.01-0.5    sell_macd_roc_reverse
THRESH_01=0
THRESH_02=5
THRESH_03=0.01
THRESH_04=0.5
THRESH_MT=0.3 # dictates mutation

NUM_SUBJECTS=10
NUM_SELECT=2

class Subject:
    def __init__(self,params):
        self.params=params
        self.score=0

    def cross1(self,subject):
        params1=self.params
        params2=subject.params
        op1=params1
        op2=params2
        skip=rnd.randint(2,3)
        for i in range(0,len(params1),skip):
            op1[i]=params2[i]
            op2[i]=params1[i]
        offspring1=Subject(op1)
        offspring2=Subject(op2)

        #offspring1.mutate()
        #offspring2.mutate()

        return offspring1,offspring2

    def cross2(self,subject):
        params1=self.params
        params2=subject.params
        op1=params1
        op2=params2
        split=rnd.randint(2,3)
        for i in range(split):
            op1[i]=params2[i]
            op2[i]=params1[i]
        offspring1=Subject(op1)
        offspring2=Subject(op2)

        offspring1.mutate()
        offspring2.mutate()

        return offspring1,offspring2

    def mutate(self):
        trigger=rnd.random()
        if trigger<THRESH_MT: return self
        params=make_randomize_params()
        i=rnd.randint(0,len(self.params)-1)
        self.params[i]=params[i]




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

def generation(count,subjects):
        
        #perform cross
        offsprings=[]
        for i in range(NUM_SELECT):
            if (i+1)<len(subjects):
                parent1=subjects[i]
                parent2=subjects[i+1]
                offspring1,offspring2=parent1.cross2(parent2)
                trade(offspring1)
                trade(offspring2)
                if offspring1.score>parent1.score:
                    offsprings.append(offspring1)
                else: offsprings.append(parent1)
                if offspring2.score>parent2.score:
                    offsprings.append(offspring2)
                else: offsprings.append(parent2)
                

        #make new subject pool
        new_subjects=[]
        for i in range(len(subjects)+1):
            if i<len(offsprings):
                new_subjects.append(offsprings[i])
            else: 
                new_subjects.append(Subject(make_randomize_params()))

        subjects=new_subjects

        #trade all subjects
        average_score=0
        subject_se=pd.Series()
        for s in subjects:
            trade(s)
            average_score+=s.score
            #print('traded score=',s.score)
            index=int(s.score*1000)
            subject_se.set_value(index,s)
        average_score/=len(subjects)

        #rank all subjects by score
        subject_se.sort_index(ascending=False,inplace=True)
        subject_se=subject_se.reset_index()
        best_subject=subject_se[0][0]
        subjects=subject_se[0].tolist()
        print("%3d : %3d/%3d offsprings | score:%3.3f"%(count,len(offsprings),len(subjects),best_subject.score))
        #print(count,':',len(offsprings),'/'' | best score:',best_subject.score)
        return subjects

def enironment():
        #generate a pool of samples
        subjects=[]
        for i in range (NUM_SUBJECTS):
            params=make_randomize_params()
            subjects.append(Subject(params))

        #print(subjects)
        #iterate generations
        scores=[]
        for i in range(50):
            subjects=generation(i,subjects)
            scores.append(subjects[0].score)

        plt.plot(scores)
        plt.show()


def main():
    enironment()

if __name__ == '__main__':
    main()





