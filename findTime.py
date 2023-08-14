import time
import calendar
from datetime import datetime,timedelta
from BasicOperation import PriorityQueue
import sys

class socialTime:
    def __init__(self,year,month,day,time,tag):
        self.year=year
        self.month=month
        self.day=day
        self.time=time # morning,afternoon,night
        self.tag=tag # done, doing, to-do

class findTime:
    def __init__(self):
        self.currentTime=None
        self.queryTime=None
        self._build()
        self.updateCurrentTime()


    def _build(self):
        self.get_numwords()
        self.weekday=["mon","monday","tue","tuesday","wed","wednesday","thu","thursday",\
            "fri","friday","sat","saturday","sun","sunday"]
        self.timeUnits=["day","month","year","days","months","years"]
        self.timeWords=["current","now","today","yesterday","tomorrow","before",\
                        "after","ago","later","past","previous","last","before",\
                        "future","after","this","next"]

    def filterInput(self,_str):
        res=[]
        if len(_str)==0:
            return res
        _input=_str.lower()
        if "-" in _input:
            _input=_input.replace("-"," ")
        _input=_input.split()
        for w in _input:
            if self.isValidWord(w):
                res.append(w)
        return res


    def isValidWord(self,word):
        if self.isTimeUnit(word):
            return True
        elif self.isTimeWord(word):
            return True
        elif self.isWeekday(word):
            return True
        elif self.isNumber(word):
            return True
        else:
            return False

    def isTimeUnit(self,word):
        if word in self.timeUnits:
            return True
        return False

    def isTimeWord(self,word):
        if word in self.timeWords:
            return True
        return False

    def isWeekday(self,word):
        if word in self.weekday:
            return True
        return False

    def isNumber(self,word):
        if word.isdigit():
            return True
        else:
            words=word.split()
            for w in words:
                if w not in self.strNum:
                    return False
            return True

    def get_numwords(self):
        self.strNum=[]
        units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        self.strNum.extend(units)
        self.strNum.extend(tens)
        self.strNum.extend(scales)
        self.numwords={}
        self.numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    self.numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     self.numwords[word] = (1, (idx+2) * 10)
        for idx, word in enumerate(scales):   self.numwords[word] = (10 ** (idx * 3 or 2), 0)

    def updateCurrentTime(self):
        self.currentTime=datetime.today()

    def getCurrentTime(self):
        self.updateCurrentTime()
        return time.asctime(self.currentTime)

    def day2num(self,day):
        day=day.lower()
        if day.startswith("mon"):
            return 0
        elif day.startswith("tue"):
            return 1
        elif day.startswith("wed"):
            return 2
        elif day.startswith("thu"):
            return 3
        elif day.startswith("fri"):
            return 4
        elif day.startswith("sat"):
            return 5
        elif day.startswith("sun"):
            return 6

    def text2int(self,textnum):
        current = result = 0
        for word in textnum.split():
            if word not in self.numwords:
                raise Exception("Illegal word: " + word)
            scale, increment = self.numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
        return result + current

    def convertText2Int(self,textnum):
        if self.isNumber(textnum):
            if textnum.isdigit():
                res=int(textnum)
                return res
            else:
                res=self.text2int(textnum)
                return res
        return None
        
            
    def dealDate(self,num_str,unit_str,tag,defaultTime):
        # num_str="two"  unit_str="days", tag="past"
        tag=tag.lower()
        num=num_str
        delta=self.convertText2Int(num)
        if unit_str in ["day","days"]:
            if delta:
                if tag=="past":
                    self.updateQueryTime(-delta,defaultTime)
                elif tag=="future":
                    self.updateQueryTime(delta,defaultTime)
                return time.asctime(self.queryTime.timetuple())
            else:
                return "Error: cannot convert this input"

        elif unit_str in ["month","months"]:
            if delta:
                if tag=="past":
                    self.updateQueryTime(-delta,defaultTime,"month")
                elif tag=="future":
                    self.updateQueryTime(delta,defaultTime,"month")
                return time.asctime(self.queryTime.timetuple())
            else:
                return "Error: cannot convert this input"

        elif unit_str in ["year","years"]:
            if delta:
                if tag=="past":
                    self.updateQueryTime(-delta,defaultTime,"year")
                elif tag=="future":
                    self.updateQueryTime(delta,defaultTime,"year")
                return time.asctime(self.queryTime.timetuple())
            else:
                return "Error: cannot convert this input"

    def getQueryDayTime(self,datastr,date_str=None):
        _str=self.filterInput(datastr)
        if len(_str)==0:
            print "Invalid Input!!!"
            return None

        if not date_str:
            self.updateCurrentTime()
            defaultTime=self.currentTime
        else:
            defaultTime=self.getTimeFromString(date_str)

        if _str[0] in ["now","today","current"]:
            return time.asctime(defaultTime.timetuple())
        
        if _str[0]=="yesterday":
            delta=-1
            self.updateQueryTime(delta,defaultTime)
            return time.asctime(self.queryTime.timetuple())
        elif _str[0]=="tomorrow":
            delta=+1
            self.updateQueryTime(delta,defaultTime)
            return time.asctime(self.queryTime.timetuple())
        elif _str=="day before yesterday".split():
            delta=-2
            self.updateQueryTime(delta,defaultTime)
            return time.asctime(self.queryTime.timetuple())
        elif _str=="day after tomorrow".split():
            delta=+2
            self.updateQueryTime(delta,defaultTime)
            return time.asctime(self.queryTime.timetuple())

        if len(_str)>=3:
            # for example, two days ago
            if "ago" in _str:
                if _str[1] in self.timeUnits:
                    return self.dealDate(_str[0],_str[1],"past",defaultTime)
            elif "later" in _str:
                if _str[1] in self.timeUnits:
                    return self.dealDate(_str[0],_str[1],"future",defaultTime)
            # for example, past two days
            if _str[0] in ["past","previous","last","before"] :
                if _str[2] in self.timeUnits:
                    return self.dealDate(_str[1],_str[2],"past",defaultTime)
            elif _str[0] in ["future","after","next"] :
                if _str[2] in self.timeUnits:
                    return self.dealDate(_str[1],_str[2],"future",defaultTime)


        # for example, this monday
        if len(_str)>=2 and _str[0] in ["this","last","next"] and _str[1] in self.weekday:
            day=self.day2num(_str[1])
            if _str[0]=="this":
                delta=day-defaultTime.weekday()
                self.updateQueryTime(delta,defaultTime)
                return time.asctime(self.queryTime.timetuple())
            elif _str[0]=="last":
                delta=day-defaultTime.weekday()-7
                self.updateQueryTime(delta,defaultTime)
                return time.asctime(self.queryTime.timetuple())
            elif _str[0]=="next":
                delta=day-defaultTime.weekday()+7
                self.updateQueryTime(delta,defaultTime)
                return time.asctime(self.queryTime.timetuple())

        print "Invalid Input!!!"
        return None
        

    def updateQueryTime(self,delta,defaultTime,tag="day"):
        tag=tag.lower()
        self.queryTime=defaultTime
        if tag=="day":
            self.queryTime+=timedelta(delta)
        elif tag=="month":
            _month=self.queryTime.month+delta
            _year=self.queryTime.year
            if _month<1:
                _year-=-1
                _month+=12
            if _month>12:
                _year+=1
                _month-=12
            self.queryTime=self.queryTime.replace(year=_year, month=_month)
        elif tag=="year":
            _year=self.queryTime.year+delta
            self.queryTime=self.queryTime.replace(year=_year)

##########################  Str to time ###########################
    def getTimeFromString(self,time_str):
        try:
            res=datetime.strptime(time_str,"%d-%b-%Y")
            return res
        except ValueError:
            raise ValueError("Raised Time-Format-Error.\nPlease input your date following the example format: 18-May-2017")

    def getTimeToString(self,time_str):
        if time_str!="":
            _time=self.getTimeFromString(time_str)
            res=_time.strftime("%d-%b-%Y")
            return res
        else:
            _time=datetime.today()
            res=_time.strftime("%d-%b-%Y")
            return res

    def getFullTimeFromString(self,time_str):
        res=datetime.strptime(time_str,"%m-%d-%y %H-%M-%S")
        return res

    def reorderFullTimeIndex(self,timeStrList):
        # from latest to the earliest
        pq=PriorityQueue()
        timeList=[self.getFullTimeFromString(str) for str in timeStrList]
        standard=timeList[0]
        priority=0
        pq.push(0,priority)
        for i in range(1,len(timeList)):
            delta=timeList[i]-standard
            priority=delta.total_seconds()
            pq.push(i,priority)
        res=[]
        for i in range(len(timeList)):
            res.append(pq.pop())
        res.reverse()
        return res



    def reorderTimefromString(self,timestrList):
        pq=PriorityQueue()
        timeList=[self.getTimeFromString(_str) for _str in timestrList]
        standard=timeList[0]
        priority=0
        pq.push(timestrList[0],priority)
        for i in range(1,len(timeList)):
            delta=timeList[i]-standard
            priority=delta.days
            pq.push(timestrList[i],priority)
        res=[]
        for i in range(len(timeList)):
            res.append(pq.pop())
        return res

    def getPastDays(self,time_str):
        _time=self.getTimeFromString(time_str)
        delta=_time-self.currentTime
        day=delta.days+1
        return day

    def isSameDate(self,time_str1,time_str2):
        _time1=self.getTimeFromString(time_str1)
        if time_str2=="":
            _time2=datetime.today()
        else:
            _time2=self.getTimeFromString(time_str2)
        delta=_time1-_time2
        if time_str2!="":
            return delta.days==0
        else:
            return delta.days+1==0

    def getDate(self,queryTime):
        date=time.asctime(queryTime.timetuple())
        tags=date.split()
        res="-".join([tags[2],tags[1],tags[4]])
        return res

    def getWeekDates(self):
        self.updateCurrentTime()
        Deltas=[0,-1,-2,-3,-4,-5,-6]
        res=[]
        for delta in Deltas:
            _time=self.currentTime+timedelta(delta)
            _date=self.getDate(_time)
            res.append(_date)
        return res

    def getSocialTime(self,time_str):
        print "time_str: "+time_str
        _time=self.getTimeFromString(time_str)
        delta=_time-self.currentTime
        day_str=self.weekdayToStr(_time.weekday())
        day=delta.days+1
        print "day ",day
        weekday=self.currentTime.weekday()
        if day==0:
            return "today"
        elif day==-1:
            return "yesterday"
        elif day==1:
            return "tomorrow"
        # elif day==-2:
        #     return "the day before yesterday"
        # elif day==2:
        #     return "the day after tomorrow"
        elif -(weekday+1)<day<=6-weekday:
            return "this "+day_str
        elif -(weekday+8)<day<=-(weekday+1):
            return "last "+day_str
        elif 6-weekday<day<=13-weekday:
            return "next "+day_str
        elif day<=-(weekday+8):
            return "some day in the past"
        elif day>13-weekday:
            return "some day in the future"

    def weekdayToStr(self,weekday):
        if weekday==0:
            return "monday"
        elif weekday==1:
            return "tuesday"
        elif weekday==2:
            return "wednesday"
        elif weekday==3:
            return "thursday"
        elif weekday==4:
            return "friday"
        elif weekday==5:
            return "saturday"
        elif weekday==6:
            return "sunday"








if __name__=="__main__":
    findTime=findTime()
    input="one hundred and forty two"
    print findTime.text2int(input)
    while True:
        datastr=raw_input("Please input the query for time: ")
        print findTime.getQueryDayTime(datastr)
    
    
            
            
            
        
