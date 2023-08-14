__author__ = 'Zhang Juzheng'
import random

class randomFunc:
    def __init__(self):
        pass

    def randomChoose(self,List):
        '''randomly choose an element in a list'''
        length=len(List)
        rand=random.randint(0,length-1)
        return List[rand]

    def randomBool(self,trueProb=0.7):
        '''randomly choose an element in a list'''
        if trueProb>1 or trueProb<0:
            print "Value error in randomBool!!!"
            return True
        List=[True,False]
        prob=[trueProb,1-trueProb]
        return self.randomChoose_w_prob(List,prob)[0]

    def randomChoose_w_prob(self,List,probList):
        prob=[]
        total=0
        for p in probList:
            x=round(p,2)*100
            total+=x
            prob.append(total)
        rand=random.randint(1,int(total))
        for i in range(len(prob)):
            if rand<=prob[i]:
                return (List[i],probList[i])


    def randProb(self,prob):
        '''prob should be larger than 0 and smaller than 1'''
        rand=random.random()
        if rand<=prob:
            return True
        return False


if __name__=="__main__":
    rdm=randomFunc()
    List=["a","b","c","d"]
    prob=[0.4,0.34,0.21,0.54]
    for i in range(10):
        print rdm.randomChoose_w_prob(List,prob)