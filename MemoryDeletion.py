__author__ = 'IMI-User'
import cPickle as pickle
import sys
import os
from loadFolder import getPath
from findTime import findTime
import shutil

class MemoryDeletion:
    def __init__(self):
        self.timeAnalyser=findTime()
        self.dayThreshold=3 # delete episodes after the dayThreshold
        self.createFolder(os.getcwd() + "\\Forget")

    def filterMemory(self):
        print "Loading Past Episodes..."
        path=os.getcwd()+"\\Episodes"
        if os.path.exists(path):
            filePaths=getPath(path)
            for _p in filePaths:
                try:
                    episode=pickle.load(open(_p, "rb"))
                    if self.shouldBeDiscarded(episode):
                        self.shiftEpisode(sourceFile=_p)
                except:
                    print sys.exc_info()
                    print "Fail in loading episode: ",_p
            print "All Memory Checked!"
        else:
            print "The file doesn't exist!!!"
        self.deleteEmptyFolders()

    def shouldBeDiscarded(self,episode):
        days = self.timeAnalyser.getPastDays(episode.date)
        if abs(days)>self.dayThreshold:
            return True
        else:
            return False

    def shiftEpisode(self, sourceFile):
        mpaths=sourceFile.split("\\")
        mpaths[-3]="Forget"
        targetFolder=("\\").join(mpaths[:-1])
        self.createFolder(targetFolder)
        targetFile=os.path.join(targetFolder,mpaths[-1])
        shutil.copy2(sourceFile,targetFile)
        print "Copy File: %s" % sourceFile
        os.remove(sourceFile)

    def createFolder(self,dst):
        if not os.path.isdir(dst):
            print "MAKE DIR: ", dst
            os.makedirs(dst)

    def deleteEmptyFolders(self):
        dirs = [x[0] for x in os.walk(os.getcwd() + "\\Episodes")][1:]
        for dir in dirs:
            if not os.listdir(dir):
                os.rmdir(dir)


if __name__=="__main__":
    deletion=MemoryDeletion()
    deletion.filterMemory()