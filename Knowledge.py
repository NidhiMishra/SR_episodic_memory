__author__ = 'Zhang Juzheng'
import cPickle as pickle
import os
from textblob import TextBlob, Word
from PriorityQueue import PriorityQueue

class Relation:
    def __init__(self,arg1=None,rel=None,arg2=None,conf=None):
        self.arg1=arg1
        self.rel=rel
        self.arg2=arg2
        self.conf=conf

    def equal(self,rel):
        x1=self.arg1==rel.arg1
        x2=self.rel==rel.rel
        x3=self.arg2==rel.arg2
        if x1 and x2 and x3:
            return True
        else:
            return False

class Knowledge:
    def __init__(self,relation_client):
        self.relation_client=relation_client
        self.stopwords=pickle.load(open("stop_words.pickle", "rb"))
        self.loadKnowledge()

    def loadKnowledge(self):
        path=os.getcwd()+"\\"+"knowledge.pickle"
        if os.path.isfile(path):
            file=open('knowledge.pickle','rb')
            self.knowledge=pickle.load(file)
            file.close()
        else:
            self.knowledge={}

    def saveKnowledge(self):
        file=open('knowledge.pickle','wb')
        pickle.dump(self.knowledge,file)
        file.close()

    def reformRel(self,rel):
        sent=TextBlob(rel)
        tags=sent.tags
        words=[]
        be=["am","is","are","was","were"]
        for (word,tag) in tags:
            if word in be:
                words.append("is")
            elif tag not in ["DT","JJ", "JJR", "JJS","RB", "RBR", "RBS"]:
                words.append(word)
        if len(words)>0:
            res=" ".join(words)
            return res
        else:
            return None


    def lemmatize(self,word,tag):
        w=Word(word,tag)
        return w.lemma

    def reformArg(self,arg):
        if arg=="x":
            return arg
        sent=TextBlob(arg)
        tags=sent.tags
        words=[]
        hasnoun=self.hasTag(tags,("PRP","PRP$","NN", "NNS", "NNP", "NNPS","VBG","JJ"))
        if not hasnoun:
            return None
        for (word,tag) in tags:
            w=self.lemmatize(word,tag)
            if w not in self.stopwords or tag.startswith("PRP"):
                words.append(w)
        if len(words)>0:
            res=" ".join(words)
            return res
        else:
            return None


    def getRelation(self,sentence,flag=False,th=0.75):
        sentence=sentence.lower()
        res=self.relation_client.client.getRelation(sentence)
        if len(res)>0:
            conf=float(res["conf"])
            if conf>th or flag:
                arg1=self.reformArg(res["arg1"])
                rel=self.reformRel(res["rel"])
                arg2=self.reformArg(res["arg2"])
                if (arg1!=None) and (rel!=None) and (arg2!=None):
                    relation=Relation(arg1,rel,arg2,conf)
                    return relation
        return None

    def formQuery(self,query):
        query=[w.lower() for w in query]
        if len(query)==1:
            return query
        elif len(query)==2:
            res=[self.lemmatize(word,"NN") for word in query]
            return res
        else:
            res=[]
            for word in query:
                if word in ["who","what"]:
                    res.append("x")
                else:
                    res.append(word)
            sent=" ".join(res)
            queryRel=self.getRelation(sent)
            if queryRel==None:
                return None
            res=[queryRel.arg1,queryRel.rel,queryRel.arg2]
            return res

    def getQuery(self,sentence,user=None):
        query=[]
        if len(sentence)!=0:
            query=self.formQuery(sentence)
        res={}
        backup={}
        if query==None:
            return None
        if user!=None and user not in self.knowledge.keys():
            return None
        knowledgeList=[]
        if user==None:
            for user in self.knowledge.keys():
               knowledgeList.extend(self.knowledge[user])
        else:
            knowledgeList=self.knowledge[user]
        if len(query)==0:
            for Rel in knowledgeList:
                answer=Rel.arg1+" "+Rel.rel+" "+Rel.arg2
                res[answer]=Rel.conf
            if len(res)>0:
                return res
            else:
                return None
        if len(query)==1:
            for Rel in knowledgeList:
                if query[0]==Rel.arg1:
                    answer=Rel.arg1+" "+Rel.rel+" "+Rel.arg2
                    res[answer]=Rel.conf
                    backup[answer]=Rel.conf
                elif query[0] in Rel.arg1:
                    answer=Rel.arg1+" "+Rel.rel+" "+Rel.arg2
                    backup[answer]=Rel.conf
            if len(res)>0:
                return res
            elif len(backup)>0:
                return backup
            else:
                return None
        elif len(query)==2:
            for Rel in knowledgeList:
                x1=(query[0] == Rel.arg1) and (query[1] == Rel.arg2)
                x2=(query[1] == Rel.arg1) and (query[0] == Rel.arg2)
                _x1=(query[0] in Rel.arg1) and (query[1] in Rel.arg2)
                _x2=(query[1] in Rel.arg1) and (query[0] in Rel.arg2)
                if x1 or x2:
                    answer=Rel.arg1+" "+Rel.rel+" "+Rel.arg2
                    res[answer]=Rel.conf
                    backup[answer]=Rel.conf
                elif _x1 or _x2:
                    answer=Rel.arg1+" "+Rel.rel+" "+Rel.arg2
                    res[answer]=Rel.conf

            if len(res)>0:
                return res
            elif len(backup)>0:
                return backup
            else:
                return None

        else:
            if "x" not in query:
                return None
            x_idx=query.index("x")
            idx=[0,1,2]
            idx.remove(x_idx)
            for Rel in knowledgeList:
                candidate=[Rel.arg1,Rel.rel,Rel.arg2]
                x1=query[idx[0]] == candidate[idx[0]]
                x2=query[idx[1]] == candidate[idx[1]]
                _x1=query[idx[0]] in candidate[idx[0]]
                _x2=query[idx[1]] in candidate[idx[1]]
                if x1 and x2:
                    res[candidate[x_idx]]=Rel.conf
                    backup[candidate[x_idx]]=Rel.conf
                elif _x1 and _x2:
                    backup[candidate[x_idx]]=Rel.conf
            if len(res)>0:
                return res
            elif len(backup)>0:
                return backup
            else:
                return None

    def getBeVerb(self,tokens):
        be=["am","is","are","was","were"]
        for word in tokens:
            if word in be:
                idx=tokens.index(word)
                return idx
        return None

    def hasTag(self,tags,tagList):
        for tag in tags:
            if tag[1] in tagList:
                return True
        return False


    def isStandardInput(self,tokens,tags):
        idx=self.getBeVerb(tokens)
        if idx:
            tg1=tags[:idx]
            tg2=tags[idx+1:]
            flag1=self.hasTag(tg1,("NN", "NNS", "NNP", "NNPS","VBG"))
            flag2=self.hasTag(tg2,("NN", "NNS", "NNP", "NNPS"))
            if flag1 and flag2:
                return True
            if tags[0][1].startswith("PRP") and idx==1 and tags[2][1]!="VBG" and flag2:
                return True
        return False




    def getSentence(self,event):
        sentence=event.sentence
        sentence=sentence.lower()
        sent=TextBlob(sentence)
        words=sent.words
        tags=sent.tags
        Flag=self.isStandardInput(words,tags)
        sub=event.getAttrLabelType("subject")
        user=event.getAttrLabelType("user")
        if sub=="Robot":
            return (None,None,False)
        if sub!=None and user!=None:
            res=[]
            for word in words:
                if word.isalpha():
                    res.append(word)
            res=" ".join(res)
            return (res,sub,Flag)
        else:
            return (sentence,sub,Flag)


    def isDuplication(self,rel,user):
        if user not in self.knowledge.keys():
            self.knowledge[user]=[]
            return False
        for r in self.knowledge[user]:
            if rel.equal(r):
                return True
        return False

    def addKnowledge(self,event):
        (sentence,sub,flag)=self.getSentence(event)
        if sentence:
            rel=self.getRelation(sentence,flag)
            if rel!=None:
                if not self.isDuplication(rel,sub):
                    if sub not in self.knowledge.keys():
                        self.knowledge[sub]=[]
                    self.knowledge[sub].append(rel)
                    print "Add relation: "+rel.arg1+", "+rel.rel+", "+rel.arg2+", ",rel.conf
        # else:
        #     print "No relation extracted"


if __name__=="__main__":
    import Inputs.RelationExtractionService as Relation_Service
    import Inputs.constants
    import ThriftTools
    from Definition import *
    import socket

    ip_address = socket.gethostbyname(socket.gethostname())
    print ip_address
    relation_client = ThriftTools.ThriftClient(ip_address,Inputs.constants.DEFAULT_RELATON_EXTRACTION_PORT,Relation_Service,'RelationExtraction')
    while not relation_client.connected:
        relation_client.connect()
    print "Successfully connect with Relation Extraction"
    kn=Knowledge(relation_client)
    while True:
        sentence=raw_input("Input: ")
        event=Event(["sentence="+sentence,"subject=James","user=James"])
        kn.addKnowledge(event)
