__author__ = 'IMI-Demo'
import os
import shutil

class DeleteUserData:
    def __init__(self):
        self.askDeletion()

    def deleteQuestionData(self,userName):
        path=os.getcwd()+"\\SpeechDialogue\\userData\\"+userName+".pickle"
        if os.path.isfile(path):
            os.remove(path)
            print "Question data of "+userName+" is successfully deleted"
        else:
            print "No Question data of "+userName+" is found!!!"

    def deleteMemoryData(self,userName):
        path=os.getcwd()+"\\EM_NLP\\Episodes\\"+userName
        if os.path.isdir(path):
            shutil.rmtree(path)
            print "Memory data of "+userName+" is successfully deleted"
        else:
            print "No Memory data of "+userName+" is found!!!"

    def deleteChatbotData(self,userName):
        path=os.getcwd()+"\\Chatbot\\aiml_program-ab-0.0.4.3\\chatbot\\userData\\"+userName+".txt"
        if os.path.isfile(path):
            os.remove(path)
            print "Chatbot data of "+userName+" is successfully deleted"
        else:
            print "No Chatbot data of "+userName+" is found!!!"

    def askDeletion(self):
        userName=raw_input("Please input which user to delete: ").capitalize()
        self.deleteChatbotData(userName)
        self.deleteMemoryData(userName)
        self.deleteQuestionData(userName)

if __name__=="__main__":
    deleteUser=DeleteUserData()


