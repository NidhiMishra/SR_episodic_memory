__author__ = 'Zhang Juzheng'

from EpisodicMemory import EpisodicMemory
from numpy import array,zeros,dot,mat,linalg,diag
import cPickle as pickle
import k_medoids as k_medoids
import BasicOperation as opt
import Definition

class Train:
    def __init__(self):
        self.EM=EpisodicMemory()
        self.getTotalEvents()
        self._build()
        self.EM.saveMemory()

    def _build(self):
        self.trainAttrCoords()
        self.saveData()
        self.EM.processEvent.AttrCoord=self.attrCoords
        self.EM.AttrCoord=self.attrCoords
        self.getEventCoords()
        self.getEventDistMat()
        self.clusterEvent(100)
        self.getEpisodeEvcMatrix()
        self.getEpEvcCoord()
        self.getEpisodeDistMat()
        self.clusterEpisode(10)
        self.getContextScore()


    def saveData(self):
        file1= open('index.pickle', 'wb')
        pickle.dump(self.attrCoords,file1)
        file1.close()


    def _remove_duplicates(self, List):
        return list(set((item for item in List)))

    # get all attribute labels
    def getAllAttrs(self):
        res=[]
        for episode in self.EM.episodes:
            for event in episode.content:
                for attr in event.content:
                    if attr.type!="knownWord":
                        res.append(attr.label)
        self.attrs=self._remove_duplicates(res)
        self.attr_to_index={}
        offset=0
        for entity in self.attrs:
            self.attr_to_index[entity] = offset #[entity:position]
            offset += 1

    def getAttrMatrix(self):
        self.attrMatrix=[]
        self.knownCoord=[]
        for episode in self.EM.episodes:
            for event in episode.content:
                coord=self.EM.processEvent.getKnownWordCoord(event)
                if coord!=None:
                    index=self.make_event_index(event)
                    self.attrMatrix.append(index)
                    self.knownCoord.append(coord)
        self.attrMatrix=mat(self.attrMatrix)
        self.knownCoord=mat(self.knownCoord)

    def solveAttrMatrix(self):
        [dim_x,dim_y]=self.attrMatrix.shape
        if dim_x<dim_y:
            print "should get more data!!!"
            return None
        A=linalg.pinv(self.attrMatrix)
        b=self.knownCoord
        X=A*b
        self.attrCoords={}
        for i in range(X.shape[0]):
            coord=X[i,:].A1
            self.attrCoords[self.attrs[i]]=coord

    def make_event_index(self,event):
        # for event context
        index = [0] * len(self.attr_to_index)
        for attr in event.content:
            if attr.type!="knownWord" and attr.label in self.attrs:
                index[self.attr_to_index[attr.label]] += attr.value
        return index

    def trainAttrCoords(self):
        self.getAllAttrs()
        self.getAttrMatrix()
        self.solveAttrMatrix()

    def getEventCoords(self):
        self.eventCoords=[]
        for i in range(len(self.EM.episodes)):
            episode=self.EM.episodes[i]
            for j in range(len(episode.content)):
                event=episode.content[j]
                coord=self.EM.processEvent.getEventCoord(event.content)
                event.coordinate=coord
                self.eventCoords.append(coord)

    def getTotalEvents(self):
        num=0
        for episode in self.EM.episodes:
            num+=len(episode.content)
        self.totalEvNum=num

    def getEventDistMat(self):
        res=mat(zeros((self.totalEvNum,self.totalEvNum)))
        for i in range(self.totalEvNum):
            for j in range(i,self.totalEvNum):
                cosVal=opt._cos(self.eventCoords[i],self.eventCoords[j])
                res[i,j]=(1-cosVal)/float(2)
        for i in range(self.totalEvNum):
            for j in range(0,i):
                res[i,j]=res[j,i]
        self.eventDistMat=res


    def clusterEvent(self,k=50):
        Idxs,event_centers=k_medoids.cluster(self.eventDistMat,k)
        eventClusterIdx=Idxs.T.tolist()[0]
        event_centers=event_centers.tolist()
        offset=0
        for center in event_centers:
            cluster=Definition.Cluster()
            cluster.idx=offset
            cluster.coord_1=self.eventCoords[center]
            self.EM.eventClusterDB.append(cluster)
            offset+=1
        for i in range(len(self.EM.episodes)):
            episode=self.EM.episodes[i]
            for j in range(len(episode.content)):
                event=episode.content[j]
                center=eventClusterIdx[event.index]
                event.category=event_centers.index(center)
                self.EM.eventClusterDB[event.category].elementIdxList.append(event.index)

    def getEpisodeEvcMatrix(self):
        res=[]
        for episode in self.EM.episodes:
            res.append(self.makeEpisodeIndex(episode))
        self.EpEvcMatrix=array(res).T

    def makeEpisodeIndex(self,episode):
        index = [0] * len(self.EM.eventClusterDB)
        for event in episode.content:
            index[event.category] += 1
        return index

    def getMinIdx(self,dataArray,prop=0.8):
        total=float(dataArray.sum())
        threshold=prop*total
        sum=0
        for i in range(dataArray.shape[0]):
            sum+=dataArray[i]
            if sum>=threshold:
                return i



    def getEpEvcCoord(self):
        s,v,d=linalg.svd(self.EpEvcMatrix)
        dim=self.getMinIdx(v)+1
        s1=s[:,:dim]
        v1=diag(v[:dim])
        d1=d[:,:dim]
        self.EM.S2=s1
        self.EM.V2=v1
        self.EpCoords=dot(d1,v1)
        EcCoords=dot(s1,v1)
        for i in range(len(self.EM.episodes)):
            episode=self.EM.episodes[i]
            episode.coordinate=self.EpCoords[i,:]
        for i in range(len(self.EM.eventClusterDB)):
            cluster=self.EM.eventClusterDB[i]
            cluster.coord_2=EcCoords[i,:]

    def getEpisodeDistMat(self):
        dim=len(self.EM.episodes)
        res=mat(zeros((dim,dim)))
        for i in range(dim):
            for j in range(i,dim):
                cosVal=opt._cos(self.EM.episodes[i].coordinate,self.EM.episodes[j].coordinate)
                res[i,j]=(1-cosVal)/float(2)
        for i in range(dim):
            for j in range(0,i):
                res[i,j]=res[j,i]
        self.episodeDistMat=res

    def clusterEpisode(self,k=10):
        Idxs,episode_centers=k_medoids.cluster(self.episodeDistMat,k)
        episodeClusterIdx=Idxs.T.tolist()[0]
        episode_centers=episode_centers.tolist()
        offset=0
        for center in episode_centers:
            cluster=Definition.Cluster()
            cluster.idx=offset
            cluster.coord_2=self.EM.episodes[center].coordinate
            self.EM.episodeClusterDB.append(cluster)
            offset+=1
        for i in range(len(self.EM.episodes)):
            episode=self.EM.episodes[i]
            center=episodeClusterIdx[episode.index]
            episode.category=episode_centers.index(center)
            self.EM.episodeClusterDB[episode.category].elementIdxList.append(episode.index)

    def getContextScore(self):
        for i in range(len(self.EM.episodes)):
            episode=self.EM.episodes[i]
            for j in range(len(episode.content)):
                event=episode.content[j]
                ev_coord=self.EM.eventClusterDB[event.category].coord_2
                score=opt._cos(ev_coord,episode.coordinate)
                event.contextScore=(1+score)/float(2)
                event.intensity=event.contextScore
                for k in range(len(event.content)):
                    attr=event.content[k]
                    if attr.type=="knownWord":
                        attr_coord=self.EM.processEvent.getWordCoord(attr.label.split("=")[1])
                    else:
                        attr_coord=self.attrCoords[attr.label]
                    score=opt._cos(attr_coord,event.coordinate)
                    attr.contextScore=(1+score)/float(2)
                    attr.intensity=attr.contextScore














if __name__=="__main__":
    tr=Train()
    print 1


