__author__ = 'IMI-User'

import sys
import os
import Definition
import cPickle as pickle
from loadFolder import getPath
from findTime import findTime

class EpisodeEditor:
    def __init__(self):
        self.defaultRoot=os.getcwd()
        self.defaultFolder="Episodes\\James"
        self.mfolder="C:\\Users\\IMI-User\\Desktop\\UserDialogs"
        self.createFolder(self.mfolder)
        self.timeAnalyser=findTime()

    def getOutputFolder(self,time_str):
        subfolder=self.timeAnalyser.getTimeToString(time_str)
        outputFolder=os.path.join(self.mfolder,subfolder)
        self.createFolder(outputFolder)
        return outputFolder

    def getEpisodePath(self):
        while True:
            print "The default root is %s" % self.defaultRoot
            mfolder=raw_input("Please input your folder [Default folder is "+self.defaultFolder+"]: ")
            if mfolder=="":
                mfolder=self.defaultFolder
            mfile=raw_input("Please input episode file [file name]: ")
            path=mfolder+"\\"+mfile
            if not path.endswith("pickle"):
                print 'Error: You should input a pickle file!'
            elif os.path.exists(path):
                self.defaultFolder=mfolder
                return path
            else:
                path=self.defaultRoot+"\\"+path
                if os.path.exists(path):
                    self.defaultFolder=mfolder
                    return path
                else:
                    print 'Error: No such a path: %s' % path


    def episodeToFile(self,episodePath):
        episode=pickle.load(open(episodePath, "rb"))
        outputPath=episodePath.split(".")[0]+".txt"
        with open(outputPath,"w") as outFile:
            for event in episode.content:
                subject=event.getAttrLabelType("subject").split("=")[1]
                sent=subject+": "+event.sentence
                outFile.write(sent+"\n")
        print "Output is done for %s" % outputPath

    def printEpisodeByDate(self,episodePath,targetDate,outputFolder):
        episode=pickle.load(open(episodePath, "rb"))
        if self.timeAnalyser.isSameDate(episode.date,targetDate):
            outputPath=self.getOutputPath(episodePath,episode.user,outputFolder)
            with open(outputPath,"w") as outFile:
                for event in episode.content:
                    subject=event.getAttrLabelType("subject").split("=")[1]
                    sent=subject+": "+event.sentence
                    outFile.write(sent+"\n")
            print "Output is done for %s" % outputPath

    def getOutputPath(self,sourceFile,userName,outputFolder):
        fileName=sourceFile.split("\\")[-1]
        targetFileName=fileName.split(".")[0]+".txt"
        targetFolder=os.path.join(outputFolder,userName)
        self.createFolder(targetFolder)
        targetFile=os.path.join(targetFolder,targetFileName)
        return targetFile

    def processMemoryByDate(self):
        print "Default output folder is: %s"% self.mfolder
        episode_date=raw_input("Please input the date in following format. For example: 18-May-2017 [Default date is today]: ")
        outputFolder=self.getOutputFolder(episode_date)
        folders=[os.getcwd()+"\\Episodes",os.getcwd()+"\\Forget",os.getcwd()+"\\UnknownUser"]
        #folders=[os.getcwd()+"\\UnknownUser"]
        for path in folders:
            if os.path.exists(path):
                filePaths=getPath(path)
                for _p in filePaths:
                    try:
                        self.printEpisodeByDate(_p,episode_date,outputFolder)
                    except ValueError as error:
                        print error.message
                        return
                    except:
                        pass
                        # print sys.exc_info()
                        # print "Fail in loading episode: ",_p
            else:
                print "The file doesn't exist!!!"

    def createFolder(self,dst):
        if not os.path.isdir(dst):
            print "MAKE DIR: ", dst
            os.makedirs(dst)





if __name__=="__main__":
    editor=EpisodeEditor()
    while True:
        editor.processMemoryByDate()
        print "\n\n"
    # while True:
    #     path=editor.getEpisodePath()
    #     editor.episodeToFile(path)
    #     print "\n\n"

