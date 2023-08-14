__author__ = 'Zhang Juzheng'
import cPickle as pickle
import Definition
import enchant
from numpy import array,zeros,dot,linalg
import re
from textblob import TextBlob, Word
import BasicOperation as opt
from randomFunc import randomFunc
import sys
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")
import socket

import Inputs.LSAService as LSA_Service
from I2P.ttypes import *
import ThriftTools

wordReplace={"work":"job"}

class processInput:
    def __init__(self,attrCoordDict):
        #print "Load wordLSA..."
        #self.wordLSA=pickle.Unpickler(open("LSA.pickle", "rb")).load()
        print "Load NLP..."
        self.stopwords=pickle.load(open("stoplist.pickle", "rb"))
        # self.stopverbs=pickle.load(open("stop_verbs.pickle", "rb"))
        # self.names=pickle.load(open("names.pickle", "rb"))
        #self.stemmer=PorterStemmer()
        #self.dic = enchant.Dict("en_US")
        self.AttrCoord=attrCoordDict
        #self.totalWords=self.wordLSA.keys()
        self.totalWords=pickle.load(open("LSAWords.pickle", "rb"))
        self.totalWords.append(u"work")
        self.initTextBlob()
        self.randomFunc=randomFunc()
        self.getLSAClient()

    def getLSAClient(self):
        ip_address = socket.gethostbyname(socket.gethostname())
        print ip_address
        self.lsa_client = ThriftTools.ThriftClient(ip_address,12018,LSA_Service,'LSA client')
        while not self.lsa_client.connected:
            self.lsa_client.connect()
        print "Successfully connect with LSA Server!!!"


    def getNouns(self,sentence,sentUser=None):
        sent=TextBlob(sentence.lower())
        tags=sent.tags
        #ner_dict=self.getner(sentence)
        res=[]
        for w,_tag in tags:
            if w not in self.stopwords:
                word=self.check(w,_tag)
                if word!=None:
                    res.append(word)
                else:
                    res.append(w)
        if sentUser!=None:
            user=sentUser.lower()
            if user in res:
                res.remove(user)
        if len(res)>0:
            return res
        else:
            return None

    def isContain(self,wordList,candidates):
        common=set(wordList).intersection(set(candidates))
        if len(common)>0: return True
        else: return False


    def isCompleteSentence(self,sentence):
        sentence=self.processSentence(sentence.lower())
        sent=TextBlob(sentence)
        tags=sent.tags
        if len(tags)<=2:
            return False
        subject=False
        verb=False
        sub_idx=-1
        verb_idx=-1
        idx=0
        for tag in tags:
            if subject and verb:
                break
            if tag[1] in ["NN", "NNS", "NNP", "NNPS","PRP"]:
                subject=True
                if sub_idx==-1: sub_idx=idx
            if tag[1] in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                verb=True
                if verb_idx==-1: verb_idx=idx
            idx+=1
        if subject and verb:
            #if sub_idx<verb_idx:
            return True
        return False



    ############################  EM + NLP ######################################
    def initTextBlob(self):
        sent=TextBlob("went")
        tags=sent.tags
        #nltk.word_tokenize("hello")
        #nltk.pos_tag("hello")
        for (w,t) in tags:
            self.lemmatize(w,t)

    def substituteWord(self,word,newWord,str):
        if word in str:
            idx=str.find(word)
            idx2=idx+len(word)
            res=str[:idx]+newWord+str[idx2:]
            #print "res: "+res
            return res
        else:
            return str



    def buildEvent(self,inputs):
        atts=self.buildAttr(inputs)
        if atts==None:
            return None
        (sent,attrs)=atts
        coord=self.getEventCoord(attrs)
        question,quesWord=self.checkQuestion(sent)
        event=Definition.Event(attrs,sent)
        event.coordinate=coord
        event.question=question
        event.quesWord=quesWord
        return event



    # def getEventCoord(self,attrs,dim=400):
    #     res=zeros(dim)
    #     for attr in attrs:
    #         coord=self.getAttrCoord(attr)
    #         if coord!=None:
    #             res+=coord
    #     if linalg.norm(res)<1e-3:
    #         res=None
    #     return res

    def getEventCoord(self,attrs):
        words=[]
        for attr in attrs:
            if attr.type=="knownWord":
                words.append(attr.label.split("=")[1])
        if len(words)==0:
            return None
        res=self.getWordCoord(words)
        if linalg.norm(res)<1e-3:
            res=None
        return res

    def getKnownWordCoord(self,event,dim=400):
        res=zeros(dim)
        knownWordLabels=event.getAttrType("knownWord")
        if knownWordLabels==None:
            return None
        for wordAttr in knownWordLabels:
            coord=self.getAttrCoord(wordAttr)
            if coord!=None:
                res+=coord
        if linalg.norm(res)<1e-3:
            res=None
        return res


    def getAttrCoord(self,attr,ctx_w=0.2):
        if attr.type=="knownWord":
            word=attr.label.split("=")[1]
            return self.getWordCoord(word)
        elif attr.label in self.AttrCoord.keys():
                return ctx_w*self.AttrCoord[attr.label]
        return None

    # should first get event
    def getEventSentCoord(self,event):
        return self.getKnownWordCoord(event)



    # get attribute list
    def buildAttr(self,contents):
        sent=self.processSentence(contents[0])
        sent=self.clearSentence(sent)
        wordLabels,wordTags=self.getKnownWords(sent)
        if len(wordLabels)==0:
            return None
        res=[]
        for i in range(1,len(contents)):
            text=contents[i]
            label,value=self.getAttrLabelIntensity(text)
            type=contents[i].split("=")[0]
            attr=Definition.Attribute(label,type,value)
            res.append(attr)

        for i in range(len(wordLabels)):
            label=wordLabels[i]
            tag=wordTags[i]
            attr=Definition.Attribute(label,"knownWord",1)
            attr.tag=tag
            res.append(attr)
        return (sent,res)

    def processSentence(self,sent_label):
        sentence=sent_label.split("=")[1].lower()
        sentence=re.sub(r"'ve"," have",sentence)
        sentence=re.sub(r"'m"," am",sentence)
        sentence=re.sub(r"'d"," would",sentence)
        sentence=re.sub(r"'s","",sentence)
        sentence=re.sub(r'''[,\.;\:!"\(\)\{\}\+~/\?&\[\]\$\|\\]+''',"",sentence)
        return sentence

    def clearSentence(self,sentence):
        words=sentence.split()
        if len(words)==0:
            return ""
        blockWords=["yes","ok","hello","no","okea","hi","sorry","yeah"]
        while words[0] in blockWords:
            words.pop(0)
            if len(words)==0:
                return ""

        return " ".join(words)



    def getAttrLabelIntensity(self,text):
        name=["emotion","mood"]
        for word in name:
            if text.startswith(word):
                _att=text.split()
                attr=_att[0]
                intensity=float(_att[1])*2
                return (attr,intensity)
        return (text,1)

    def getKnownWords(self,sentence):
        res=[]
        res_tags=[]
        sent=TextBlob(sentence)
        tags=sent.tags
        for (word,tag) in tags:
            word=self.check(word,tag)
            if word!=None:
                res.append("knownWord="+word)
                res_tags.append(tag)

        return res,res_tags


    def getWordCoord(self,words):
        #coord=self.wordLSA[word]
        if isinstance(words,str):
            words=[words]
        for i in range(len(words)):
            word=words[i]
            if word in wordReplace.keys():
                words[i]=wordReplace[word]
        coord=self.lsa_client.client.getCoordinates(words)
        coord=array(coord,"float")
        return coord


    # def checkQuestion(self,sent):
    #     # direct find key word
    #     queWords=["who","whom","when","where","what"]
    #     for word in queWords:
    #         if word in sent:
    #             return True,word
    #     # make analysis of the sentence
    #     sentence=TextBlob(sent)
    #     TaggedSentence=sentence.tags
    #     if len(TaggedSentence)==0:
    #         return False
    #     firstWord=TaggedSentence[0][0]
    #     secondWord=TaggedSentence[0][1]
    #     if len(TaggedSentence)>1:
    #         secondTag=TaggedSentence[1][1]
    #     else:
    #         secondTag=""
    #     questionWord=["did","does","which","who","whom","when","where","is","are","was","were",\
    #                   "had","will","would","shall","should","can","could","may","might"]
    #     if firstWord in questionWord:
    #         return True,firstWord
    #     elif firstWord in ["do","have"] and (secondTag =="PRP" or secondTag.startswith("NN")):  # do you
    #         return True,firstWord
    #     elif firstWord in ["what","how"]: # how nice you are
    #         if secondTag not in ["JJ","DT"] or secondWord in ["much","many"]:
    #             return True,firstWord
    #         else:
    #             return False,None
    #     else:
    #         return False,None

    def checkQuestion(self,sent):
        sentence=TextBlob(sent)
        TaggedSentence=sentence.tags
        if len(TaggedSentence)==0:
            return False,None
        firstWord=TaggedSentence[0][0]
        if len(TaggedSentence)>1:
            secondWord=TaggedSentence[1][0]
            secondTag=TaggedSentence[1][1]
        else:
            secondWord=""
            secondTag=""
        questionWord=["did","does","which","who","whom","when","where","is","are","was","were",\
                      "had","will","would","shall","should","can","could","may","might"]
        if firstWord in questionWord:
            #print "Q: ",sent
            return True,firstWord
        elif firstWord in ["do","have"] and (secondTag =="PRP" or secondTag.startswith("NN")):  # do you
            #print "Q: ",sent
            return True,firstWord
        elif firstWord in ["what"]: # how nice you are
            if secondTag not in ["JJ","DT","PRP"] and secondWord not in ["if"]:
                #print "Q: ",sent
                return True,firstWord
            else:
                return False,None
        elif firstWord in ["how"]: # how nice you are
            if secondTag not in ["JJ","DT","PRP"] or secondWord in ["much","many"]:
                #print "Q: ",sent
                return True,firstWord
            else:
                return False,None
        else:
            return False,None

    def check(self,word,tag):
        try:
            if word not in self.stopwords:
                lemma=self.lemmatize(word,tag)
                if isinstance(word,Word):
                    word=word.string
                if word in self.totalWords:
                    if lemma in self.totalWords:
                        return lemma
                    else:
                        return word
                return None
        except:
            print sys.exc_info()

    # def isStopwords(self,str):
    #     if(str in self.stopwords):
    #         return True
    #     else:
    #         return False
    #
    # def isStopverbs(self,str):
    #     if(str in self.stopverbs):
    #         return True
    #     else:
    #         return False
    #
    # def isName(self,str):
    #     if(str in self.names):
    #         return True
    #     else:
    #         return False

    def lemmatize(self,word,tag):
        w=Word(word,tag)
        lemma=w.lemma
        if isinstance(lemma,Word):
            lemma=lemma.string
        return lemma

    def getSimilarWord(self,attr,event,candidates,dim=400):
        words=[]
        coords=[]
        for absword in candidates:
            res=[]
            sent=TextBlob(absword)
            tags=sent.tags
            coord=zeros(dim)
            for (word,tag) in tags:
                word=self.check(word,tag)
                if word!=None:
                    res.append(word)
                    coord+=self.getWordCoord(word)
            if linalg.norm(coord)>1e-3:
                new_sent=" ".join(res)
                words.append(new_sent)
                coords.append(coord)
        if len(coords)>0:
            sent_coord=self.getEventSentCoord(event)
            cos_array=[opt._cos(sent_coord,coord) for coord in coords]
            (word_idx,n_max)=opt.find_n_max(cos_array,1)
            attr.substitution=self.getIsAExpression(words[word_idx[0]])
        else:
            attr.substitution=False

    def getIsAExpression(self,sent):
        pre=["a kind of","one of","something about"]
        res=self.randomFunc.randomChoose(pre)+" "+sent
        return res






if __name__=="__main__":
    import cPickle as pickle
    file=open("LSAWords.pickle", "rb")
    totalWords=pickle.load(file)
    print len(totalWords)
    words=[]
    for word in totalWords:
        try:
            #print word
            w=str(word)
            words.append(w)
        except:
            print w
    words.append("work")
    print "nationality" in words
    print len(words)
    file.close()

    file1=open("LSA", "wb")
    pickle.dump(words,file1)
    file1.close()

    # proc=processInput({})
    # # event=proc.buildEvent(["sentence=University has many talented researchers","sub=James",\
    # #                       "user=James","emotion=JOY 0.3","mood=EXEUBERANT 0.5"])
    # event=proc.buildEvent(["sentence=job"])
    # print 1
