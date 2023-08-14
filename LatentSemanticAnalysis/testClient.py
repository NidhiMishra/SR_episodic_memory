__author__ = 'Zhang Juzheng'

import sys
sys.path.append("gen-py")
sys.path.append("i2p/tools/py")

import Inputs.LSAService as LSA_Service
from I2P.ttypes import *
import ThriftTools
   


if __name__=="__main__":
    import socket

    ip_address = socket.gethostbyname(socket.gethostname())
    print ip_address
    

    lsa_client = ThriftTools.ThriftClient(ip_address,12018,LSA_Service,'LSA client')
    while not lsa_client.connected:
        lsa_client.connect()
    print "Successfully connect with LSA"

    while True:
        question=raw_input("Your Input: ")
        queries=question.lower().split()
        answer=lsa_client.client.getCoordinates(queries)
        print answer[:5]