__author__ = 'Zhang Juzheng'
import BasicOperation as opt
from copy import copy

class activationSpreading:
    def __init__(self,attr_ev_Mat,ev_ep_Mat,th):
        self.attr_ev_Mat=attr_ev_Mat
        self.ev_ep_Mat=ev_ep_Mat
        self.threshold=th
        self._build()

    def _build(self):
        (self.numAttr,self.numEv)=self.attr_ev_Mat.shape
        self.numEp=self.ev_ep_Mat.shape[1]
        self.activationAttr=[0]*self.numAttr
        self.activationEv=[0]*self.numEv
        self.activationEp=[0]*self.numEp
        self.updatedAttrIdx=[]
        self.updatedEvIdx=[]
        self.updatedEpIdx=[]

    def stimuliAttr(self,attr_index):
        # update attr_activation first
        for idx in attr_index:
            self.activationAttr[idx]+=1
        self.updatedAttrIdx+=attr_index

        boolVal=True
        self.lastAttrIdx=attr_index
        self.lastEvIdx=None
        self.lastEpIdx=None

        while boolVal:
            boolVal=False
            # spreading from attr and episode to event
            if self.lastAttrIdx!=None:
                for idx in self.lastAttrIdx:
                    if(self.attr_to_ev_spreading(idx)):
                        boolVal=True
            if self.lastEpIdx!=None:
                for idx in self.lastEpIdx:
                    if(self.ep_to_ev_spreading(idx)):
                        boolVal=True

            # spread from event to attr and episode
            if boolVal:
                boolVal=False
                if self.lastEvIdx!=None:
                    for idx in self.lastEvIdx:
                        if(self.ev_to_attr_spreading(idx)):
                            boolVal=True
                        if(self.ev_to_ep_spreading(idx)):
                            boolVal=True





    def verifyIndex(self,updatedIndex,index):
        for idx in updatedIndex:
            if idx in index:
                index.remove(idx)

    def attr_to_ev_spreading(self,idx):
        row=opt.matrix_row(idx,self.attr_ev_Mat).tolist()[0]
        LargerIndex=opt.findlarger(row,self.threshold)
        self.verifyIndex(self.updatedEvIdx,LargerIndex)
        num=len(LargerIndex)
        if num>0:
            sum=opt.sum_list_slice(LargerIndex,row)
            act=self.activationAttr[idx]
            for i in LargerIndex:
                self.activationEv[i]+=(row[LargerIndex[i]]/sum)*act
            self.updatedEvIdx+=LargerIndex
            self.lastEvIdx=LargerIndex
            return True
        else:
            self.lastEvIdx=None
            return False

    def ep_to_ev_spreading(self,idx):
        col=opt.matrix_col(idx,self.ev_ep_Mat).tolist()[0]
        LargerIndex=opt.findlarger(col,self.threshold)
        self.verifyIndex(self.updatedEvIdx,LargerIndex)
        num=len(LargerIndex)
        if num>0:
            sum=opt.sum_list_slice(LargerIndex,col)
            act=self.activationEp[idx]
            for i in LargerIndex:
                self.activationEv[i]+=(col[LargerIndex[i]]/sum)*act
            self.updatedEvIdx+=LargerIndex
            self.lastEvIdx=LargerIndex
            return True
        else:
            self.lastEvIdx=None
            return False

    def ev_to_attr_spreading(self,idx):
        col=opt.matrix_col(idx,self.attr_ev_Mat).tolist()[0]
        LargerIndex=opt.findlarger(col,self.threshold)
        self.verifyIndex(self.updatedAttrIdx,LargerIndex)
        num=len(LargerIndex)
        if num>0:
            sum=opt.sum_list_slice(LargerIndex,col)
            act=self.activationEv[idx]
            for i in LargerIndex:
                self.activationAttr[i]+=(col[LargerIndex[i]]/sum)*act
            self.updatedAttrIdx+=LargerIndex
            self.lastAttrIdx=LargerIndex
            return True
        else:
            self.lastAttrIdx=None
            return False

    def ev_to_ep_spreading(self,idx):
        row=opt.matrix_row(idx,self.ev_ep_Mat).tolist()[0]
        LargerIndex=opt.findlarger(row,self.threshold)
        self.verifyIndex(self.updatedEpIdx,LargerIndex)
        num=len(LargerIndex)
        if num>0:
            sum=opt.sum_list_slice(LargerIndex,row)
            act=self.activationEv[idx]
            for i in LargerIndex:
                self.activationEp[i]+=(row[LargerIndex[i]]/sum)*act
            self.updatedEpIdx+=LargerIndex
            self.lastEpIdx=LargerIndex
            return True
        else:
            self.lastEpIdx=None
            return False






