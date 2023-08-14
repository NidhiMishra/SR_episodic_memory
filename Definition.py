__author__ = 'Zhang Juzheng'

tagTypes={"noun":("NN", "NNS", "NNP", "NNPS"),
        "adj":("JJ", "JJR", "JJS"),
        "verb": ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ"),
        "adv":("RB", "RBR", "RBS")}

import BasicOperation as opt
import os
import cPickle as pickle
import copy
import numpy as np
import time
import re



class Attribute:
    def __init__(self,label,type,value):
        self.label=label
        self.type=type
        self.value=value  # the value count for the attribute-event matrix
        self.intensity=None
        self.contextScore=None
        self.isForgotten=False
        self.tag=None
        self.substitution=None # the general concept can substitute the word. Asian Country-->Singapore

    def __del__(self):
        return

    def update(self):
        self.intensity=self.intensity+(1-self.intensity)*self.contextScore

    def checkForgetting(self,th=0.4):
        #lastForgotten=self.isForgotten
        if self.intensity<th:
            self.isForgotten=True
        else:
            self.isForgotten=False
        # # check whether the vh remember something or not
        # if lastForgotten==True and self.isForgotten==False:
        #     return True
        # return None

    def decay(self,delta=0.9):
        self.intensity*=delta
        if self.intensity<1e-2:
            self.intensity=0

    def updateByCue(self,processInput,word_coords,th=0.3):
        # check for all attr in the cue
        if self.type=="knownWord":
            coord=np.array(processInput.getWordCoord(self.label.split("=")[1]))
            sims=[opt._cos(w_coord,coord) for w_coord in word_coords]
            idx,_=opt.find_n_max(sims,1)
            sim=sims[idx[0]]
        else:
            sims=[opt._cos(w_coord,processInput.AttrCoord[self.label]) for w_coord in word_coords]
            idx,_=opt.find_n_max(sims,1)
            sim=sims[idx[0]]
        if sim>th:
            self.intensity=self.intensity+(1-self.intensity)*self.contextScore
            remFlag=self.checkForgetting()
            if remFlag:
                return sim
        return None

    # def _copy(self,element):
    #     eleDict=copy.deepcopy(element.__dict__)
    #     myDict=copy.deepcopy(self.__dict__)
    #     deleteSet=set(eleDict.keys())-set(myDict.keys())
    #     addSet=set(myDict.keys())-set(eleDict.keys())
    #     for attr in deleteSet:
    #         del eleDict[attr]
    #     for attr in addSet:
    #         eleDict[attr]=copy.deepcopy(myDict[attr])
    #     self.__dict__=eleDict





class Event:
    def __init__(self,attrs,sent):
        self.content=attrs
        self.sentence=sent
        self.coordinate=None
        self.category=None
        self.index=None
        self.question=None
        self.quesWord=None
        self.intensity=None
        self.contextScore=None
        self.isForgotten=False

    def __del__(self):
        return

    def getFlatAttr(self):
        res=[attr.label for attr in self.content]
        res.insert(0,self.sentence)
        return res

    def getWordType(self,wordType):
        if wordType not in tagTypes.keys():
            return None
        types=tagTypes[wordType]
        wordAttr=self.getAttrType("knownWord")
        if wordAttr==None:
            return None
        else:
            res=[]
            for attr in wordAttr:
                if attr.tag in types:
                    res.append(attr.label.split("=")[1])
            return res





    def getAttrType(self,type):
        res=[]
        for attr in self.content:
            if attr.type==type:
                res.append(attr)
        if len(res)==0:
            return None
        elif len(res)==1 and type!="knownWord":
            return res[0]
        else:
            return res

    def getAttrLabelType(self,type):
        res=[]
        for attr in self.content:
            if attr.type==type:
                res.append(attr.label)
        if len(res)==0:
            return None
        elif len(res)==1 and type!="knownWord":
            return res[0]
        else:
            return res

    def initAttrCtxScore(self,processInput):
        for i in range(len(self.content)):
            attr=self.content[i]
            attr.contextScore=opt._cos(processInput.getAttrCoord(attr),self.coordinate)
            attr.intensity=attr.contextScore

    def update(self):
        self.intensity=self.intensity+(1-self.intensity)*self.contextScore

    def updateByCue(self,processInput,cue_coord,word_coords,th=0.3):
        sim=opt._cos(cue_coord,self.coordinate)
        if sim>th:
            self.intensity=self.intensity+(1-self.intensity)*self.contextScore*sim
        for attr in self.content:
           attr.updateByCue(processInput,word_coords)



    def checkForgetting(self,th=0.1):
        if self.intensity<th:
            self.isForgotten=True
        else:
            self.isForgotten=False
        for attr in self.content:
            attr.checkForgetting()

    def decay(self,delta=0.9):
        self.intensity*=delta
        if self.intensity<1e-2:
            self.intensity=0
        for i in range(len(self.content)):
            attr=self.content[i]
            attr.decay()

    def getCategory(self,eventClusterDB):
        cos_array=[opt._cos(self.coordinate,cluster.coord_1) for cluster in eventClusterDB]
        (cluster_idx,sim)=opt.find_n_max(cos_array,1)
        self.category=cluster_idx
        eventClusterDB[cluster_idx].elementIdxList.append(self.index)


class Cluster:
    def __init__(self):
        self.idx=None
        self.elementIdxList=[]
        self.coord_1=None # coord in event space
        self.coord_2=None # coord in episode space




class Episode:
    def __init__(self):
        self.content=[]
        self.coordinate=None
        self.category=None
        self.maxEvIdx=None
        self.date=None
        self.latestDate=None
        self.index=None
        self.user=None
        self.intensity=1
        self.isForgotten=False
        self.path=None  # path for storage

    def __del__(self):
        return

    def delete(self):
        if self.path!=None:
            os.remove(self.path)

    def save(self):
        if self.path!=None:
            file=open(self.path, "wb")
            pickle.dump(self,file)
            file.close()

    def getEventIndex(self):
        res=[self.content[i].index for i in range(len(self.content))]
        return res

    def initEventCtxScore(self,eventClusters):
        for i in range(len(self.content)):
            event=self.content[i]
            event.contextScore=opt._cos(eventClusters[event.category].coord_2,self.coordinate)
            event.intensity=event.contextScore

    def start(self,day):
        for i in range(0,day):
            self.decay()
        self.checkForgetting()

    def dealForgetting(self):
        self.checkForgetting()
        if self.isForgotten:
            self.delete()
            return True
        else:
            for event in self.content:
                if event.isForgotten:
                    self.content.remove(event)
            if len(self.content)==0:
                self.delete()
                return True
        return False


    def update(self,gama=0.5):
        self.intensity=self.intensity+(1-self.intensity)*gama

    def updateByCue(self,processInput,cue):
        self.update()
        cue_words=cue.getAttrLabelType("knownWord")
        words=[word.split("=")[1] for word in cue_words]
        word_coords=[processInput.getWordCoord(word) for word in words]
        cue_coord=cue.coordinate
        for i in range(len(self.content)):
            event=self.content[i]
            event.updateByCue(processInput,cue_coord,word_coords)




    def checkForgetting(self,th=0.1):
        if self.intensity<th:
            self.isForgotten=True
        else:
            self.isForgotten=False
        for event in self.content:
            event.checkForgetting()

    def decay(self,delta=0.9):
        self.intensity*=delta
        if self.intensity<1e-2:
            self.intensity=0
        for i in range(len(self.content)):
            event=self.content[i]
            event.decay()

    def getCoord(self,eventClusterDB):
        dim=eventClusterDB[0].coord_2.shape[0]
        res=np.zeros(dim)
        for event in self.content:
            ev_coord=eventClusterDB[event.category].coord_2
            res+=ev_coord
        self.coordinate=res

    def getCategory(self,episodeClusterDB,th=0.5):
        cos_array=[opt._cos(self.coordinate,cluster.coord_2) for cluster in episodeClusterDB]
        (cluster_idx,sim)=opt.find_n_max(cos_array,1)
        if sim>=th:
            self.category=cluster_idx
            episodeClusterDB[cluster_idx].elementIdxList.append(self.index)
        else: # create new category
            self.category=len(episodeClusterDB)+1
            newCluster=Cluster()
            newCluster.coord_2=self.coordinate
            newCluster.idx=self.category
            newCluster.elementIdxList.append(self.index)

    def getTimeStr(self):
        if self.path!=None:
            timeStr=self.path.split("\\")[-1].split(".")[0]
        else:
            timeStr=time.strftime("%c")
            timeStr=re.sub(r'''[\:/]''',"-",timeStr)
        return timeStr


if __name__=="__main__":
    ep=Episode()
    ep.path=os.getcwd()+"\\"+"Test.pickle"
    ep.save()







