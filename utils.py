__author__ = 'Zhang Juzheng'
import findTime
import time
from datetime import datetime
import re
import nltk
from textblob import TextBlob,Word
import enchant
import cPickle as pickle
import random


def processSentence(sentence):
    sentence=re.sub(r"'ve"," have",sentence)
    sentence=re.sub(r"'m"," am",sentence)
    sentence=re.sub(r"'d"," would",sentence)
    sentence=re.sub(r"'s"," is",sentence)
    sentence=re.sub(r"'t"," not",sentence)
    sentence=re.sub(r'''[,\.;\:!"\(\)\{\}\+~/\?&\[\]\$\|\\]+''',"",sentence)
    return sentence

class randomFunc:
    def __init__(self):
        pass

    def randomChoose(self,List):
        '''randomly choose an element in a list'''
        length=len(List)
        rand=random.randint(0,length-1)
        return List[rand]

    def randProb(self,prob):
        '''prob should be larger than 0 and smaller than 1'''
        rand=random.random()
        if rand<=prob:
            return True
        return False


class timeUtils:
    def __init__(self):
        self.timeAnalyser=findTime.findTime()
        self.updateCurrentTime()

    def updateCurrentTime(self):
        now=datetime.today()
        now=time.asctime(now.timetuple())
        tags=now.split()
        self.date="-".join([tags[2],tags[1],tags[4]])
        self.weekday=tags[0]
        self.socialTime=self.getSocialTime(tags[3].split(":")[0])

    def getStringDate(self,datestr):
        now=self.timeAnalyser.getQueryDayTime(datestr)
        if now==None:
            return None
        tags=now.split()
        date="-".join([tags[2],tags[1],tags[4]])
        return date



    def getSocialTime(self,hour):
        hour=int(hour)
        if hour>0 and hour<=12:
            return "Morning"
        elif hour>12 and hour<=18:
            return "Afternoon"
        else:
            return "Night"

    def getSentenceTime(self,sentence):
        if sentence=="":
            return "None"
        sentence=sentence.lower()
        sentence=processSentence(sentence)
        gottime=self.timeAnalyser.getQueryDayTime(sentence)
        tags=gottime.split()
        weekday=tags[0]
        socialTime="None"
        return (weekday,socialTime)

class sentenceUtils:
    def __init__(self):
        self.stopverbs=pickle.load(open('stop_verbs.pickle','rb'))
        self.stopwords=pickle.load(open('stop_words.pickle','rb'))
        #self.initTextBlob()
        self.dic = enchant.Dict("en_US")
        self.changeDict={"second":{"i":"you",
                                     "am":"are",
                                     "was":"were",
                                     "my":"your"},
                         "third":{"i":"he",
                                   "am":"is",
                                   "my":"his"},
                         "second_to_first":{"you":"i",
                                            "are":"am",
                                            "were":"was",
                                            "your":"my"}}



    def getNouns(self,sentence,sentUser=None):
        sent=TextBlob(sentence)
        tags=sent.tags
        #ner_dict=self.getner(sentence)
        res=[]
        for w,_tag in tags:
            if w not in self.stopwords:
                if _tag in ("NN", "NNS", "NNP", "NNPS"):
                    res.append(w)
                elif _tag in ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ"):
                    verb=self.lemmatize(w,_tag)
                    if verb not in self.stopverbs:
                        res.append(w)
                # else:
                #     res.append(w)
        if sentUser!=None:
            user=sentUser.lower()
            if user in res:
                res.remove(user)
        if len(res)>0:
            result=" ".join(res)
            print "search cue is: "+result
            return result
        else:
            return None

    def lemmatize(self,word,tag):
        w=Word(word,tag)
        return w.lemma

    # def getner(self,userInput):
    #     ner=None
    #     if self.ner_client.connected:
    #         ner=self.ner_client.client.getNER(userInput)
    #     if len(ner)>0:
    #         return ner
    #     else:
    #         return None

    def substituteWord(self,word,newWord,str):
        if word in str:
            idx=str.find(word)
            idx2=idx+len(word)
            res=str[:idx]+newWord+str[idx2:]
            #print "res: "+res
            return res
        else:
            return str

    def removeWord(self,sentence):
        sents=nltk.word_tokenize(sentence)
        remove_words=["yes","no"]
        for word in remove_words:
            if word==sents[0]:
                sentence=self.substitute(sentence,word,"")
        return sentence

    def checkInput(self,attrs):
        # do spell correction
        # userInput=userInput.lower()
        userInput=attrs[0].split("=")[1]
        subwords=["jams","ngu","an tu"]
        userInput=self.substituteWord("jams","james",userInput)
        userInput=self.substituteWord("ngu","ntu",userInput)
        userInput=self.substituteWord("an tu","ntu",userInput)
        userInput=processSentence(userInput)
        userInput=userInput.lower()
        self.blob_text=TextBlob(userInput)
        #ner_dict=self.getner(userInput)
        tags=self.blob_text.tags
        res=[]
        for (w,_tag) in tags:
            w_res=w.string
            if _tag not in ("NN", "NNS", "NNP", "NNPS","PRP","PRP$"):
                if not self.dic.check(w_res):
                    w_res=w.correct()
            res.append(w_res)

        res=" ".join(res)
        attrs[0]="sentence="+res
        return res


    def getSentenceState(self,sentence):
        if sentence=="":
            return "None"
        sentence=sentence.lower()
        sentence=processSentence(sentence)
        tokens=nltk.word_tokenize(sentence)
        tags=nltk.pos_tag(tokens)
        if "going to" in sentence:
            pos1=tokens.index("going")-1
            pos2=tokens.index("to")+1
            former=tags[pos1][0]
            latter=tags[pos2][1]
            if former in ["be","am","is","was","are","were","been"] and latter=="VB":
                return "Future"
        for tag in tags:
            if tag == ('will', 'MD'):
                return "Future"
            elif tag[1] in ["VBD","VBN"]:
                return "Past"
            else:
                return "Present"


    def checkQuestion(self,TaggedSentence):
        #firstTag=TaggedSentence[0][1]
        if len(TaggedSentence)==0:
            return False
        firstWord=TaggedSentence[0][0]
        secondWord=TaggedSentence[0][1]
        if len(TaggedSentence)>1:
            secondTag=TaggedSentence[1][1]
        else:
            secondTag=""
        questionWord=["did","does","which","who","whom","when","where","is","are","was","were",\
                      "had","will","would","shall","should","can","could","may","might"]
        if firstWord in questionWord:
            return True
        elif firstWord in ["do","have"] and (secondTag =="PRP" or secondTag.startswith("NN")):  # do you
            return True
        elif firstWord in ["what","how"]: # how nice you are
            if secondTag not in ["JJ","DT"] or secondWord in ["much","many"]:
                return True
            else:
                return False
        else:
            return False

    def isContain(self,wordList,candidates):
        idx=-1
        for word in candidates:
            if word in wordList:
                if idx==-1: idx=wordList.index(word)
                return (True,idx)
        return (False,-1)

    def isCompleteSentence(self,sentence):
        sentence=processSentence(sentence)
        sent=TextBlob(sentence)
        tags=sent.tags
        subject=False
        verb=False
        sub_idx=-1
        verb_idx=-1
        idx=0
        for tag in tags:
            if tag[1] in ["NN", "NNS", "NNP", "NNPS","PRP"]:
                subject=True
                if sub_idx==-1: sub_idx=idx
            if tag[1] in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                verb=True
                if verb_idx==-1: verb_idx=idx
            idx+=1
        if subject and verb:
            if sub_idx<verb_idx:
                return True
        return False

    def getCompleteAnswer(self,question,answer):
        beVerb=["be","am","is","was","are","were"]
        question=processSentence(question.lower())
        answer=processSentence(answer.lower())
        quesWord=nltk.word_tokenize(question)
        if len(quesWord)<2:
            return answer
        x1=quesWord[0] in ["what","who"]
        x2=quesWord[1] in beVerb
        if x1 and x2:
            flag=self.isCompleteSentence(answer)
            if not flag:
                resWord=quesWord[2:]
                resWord.append(quesWord[1])
                resWord.append(answer)
                resSent=" ".join(resWord)
                res=self.changeSecondToFirstPerson(resSent)
                return res

        x3=quesWord[0] in ["do","did","is","was","are","were","will","would","shall","should","can","could"]
        x4=quesWord[1] in ["you","your"]
        if x3 and x4:
            answerFlag=self.getSentOpinion(answer)
            if answerFlag!=None:
                resWord=[]
                resWord.append(quesWord[1])
                if (quesWord[0] not in ["do","did"]) or (not answerFlag):
                    resWord.append(quesWord[0])
                    if not answerFlag:
                        resWord.append("not")
                resWord.extend(quesWord[2:])
                resSent=" ".join(resWord)
                res=self.changeSecondToFirstPerson(resSent)
                return res

        return answer



    def changeToSecondPerson(self,sentence):
        sentence=sentence.lower()
        tokens=nltk.word_tokenize(sentence)
        res=[]
        for word in tokens:
            if word in self.changeDict["second"].keys():
                res.append(self.changeDict["second"][word])
            else:
                res.append(word)
        str=" ".join(res)
        return str

    def changeSecondToFirstPerson(self,sentence):
        sentence=sentence.lower()
        tokens=nltk.word_tokenize(sentence)
        res=[]
        for word in tokens:
            if word in self.changeDict["second_to_first"].keys():
                res.append(self.changeDict["second_to_first"][word])
            else:
                res.append(word)
        str=" ".join(res)
        return str

    def changeToThirdPerson(self,sentence):
        sentence=sentence.lower()
        tokens=nltk.word_tokenize(sentence)
        res=[]
        for word in tokens:
            if word in self.changeDict["third"].keys():
                res.append(self.changeDict["third"][word])
            else:
                res.append(word)
        str=" ".join(res)
        return str

    def transferThirdtoSecondPerson(self,sentence,userName):
        words=nltk.word_tokenize(sentence.lower())
        user=userName.lower()
        print "sentence: "+sentence
        print "user: " +user
        idx=0
        while user in words[idx:]:
            if idx==0:
                idx=words.index(user)
            else:
                idx=words.index(user,idx+1)
            words[idx]="you"
            if idx<len(words)-1 and words[idx+1] in ["is","was"]:
                words[idx+1]="are"

        res=" ".join(words)
        print "res :"+res
        return res

    # def transferFirstPerson(self,tokens,userName):
    #     first=["i","me","my"]
    #     user=userName.lower()
    #     for word in first:
    #         if word in tokens:
    #             idx=tokens.index(word)
    #             tokens[idx]=user

    def getSentOpinion(self,sentence):
        sent=nltk.word_tokenize(sentence.lower())
        agree=["yes","ok","okea","nice","sure","of course","go ahead"]
        disagree=["no","not"]
        for word in disagree:
            if word in sent:
                return False
        for word in agree:
            if word in sent:
                return True
        return None


    def getOpinion(self,sentence,pleasure):
        opn=self.getSentOpinion(sentence)
        if opn==True:
            return True
        elif opn==False:
            return False
        if pleasure>=0:
            return True
        else:
            return False

    def replaceName(self,sentence,name,order=3):
        sentWords=nltk.word_tokenize(sentence.lower())
        if order==3:
            if "he" in sentWords:
                idx=sentWords.index("he")
                sentWords[idx]=name
                res=" ".join(sentWords)
                return res
        return None

    def substitute(self,sentence,from_word,to_word):
        if from_word in sentence:
            idx=sentence.find(from_word)
            length=len(from_word)
            res=sentence[:idx]+to_word+sentence[idx+length:]
            return res
        return sentence

if __name__=="__main__":

    sent_proc=sentenceUtils()
    print sent_proc.substitute("I am ntu student","ntu","n t u")


    question="Can you play basketball"
    answer1="Yes, I can"
    answer2="I like it very much"
    sent="It's a private question"
    sent_proc=sentenceUtils()
    print sent_proc.isCompleteSentence(sent)
    print sent_proc.getCompleteAnswer(question,answer1)
    print sent_proc.getCompleteAnswer(question,answer2)


