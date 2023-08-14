__author__ = 'Zhang Juzheng'

# -*- coding: utf-8 -*-
import os

def getPath(rootDir):
    list_dirs = os.walk(rootDir)
    res=[]
    for root, dirs, files in list_dirs:
        for f in files:
            res.append(root+"\\"+f)
    return res
        #for d in dirs:
            #print os.path.join(root, d)
        #for f in files:
            #print os.path.join(root, f)

if __name__=="__main__":
    print getPath("D:\BTC_VH\SOURCE\MemoryCollection\SpeechDialogue\TrainEpisodes")
