__author__ = 'IMI-Demo'

import pickle
import os
if __name__=="__main__":
    episode=pickle.load(open(os.getcwd()+"\\UnknownUser\\08-02-16 15-19-50.pickle","rb"))
    for event in episode.content:
        print event.sentence