__author__ = 'Zhang Juzheng'



class shortTermMemory:
    def __init__(self,length=5):
        self.index=[]
        self.fixedLen=2
        self.maxLen=length
        self.fixedIndex=[] # it includes the current episode


    def encode(self,ep_idx):
        if ep_idx in self.index:
            self.index.remove(ep_idx)
        self.index.append(ep_idx)
        while len(self.index)>self.maxLen:
            self.pop()

    # def addFixedIndex(self,ep_idx):
    #     if ep_idx not in self.fixedIndex:
    #         self.fixedIndex.append(ep_idx)
    def addFixedIndex(self,ep_idx):
        if ep_idx in self.fixedIndex:
            self.fixedIndex.remove(ep_idx)
        self.fixedIndex.append(ep_idx)
        while len(self.index)>self.fixedLen:
            self.fixedIndex.pop(0)

    def pop(self):
        self.index.pop(0)

    def update(self,Episodes,processInput,cue):
        for i in self.index:
            episode=Episodes[i]
            episode.updateByCue(processInput,cue)
            episode.checkForgetting()

    def getIndex(self):
        res=set(self.index) | set(self.fixedIndex)
        return list(res)



