# -*- coding: utf-8 -*-
#from hashlib import md5
import subprocess
import Queue
from threading import  Thread
import os,  socket



        
class Server(Thread):
    def __init__(self):
    	Thread.__init__(self)
        self.__serverPort = 0
        self.__configure = 0
        self.__connection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
    def run(self):
        #configure = self.__configure()
        self.__serverPort = configure.getPort()
        self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__connection.bind( ("", self.__serverPort) )
#        self.__connection.settimeout(15)
        self.__connection.listen(1)
 
        while 1:
            try:
                i, addr = self.__connection.accept()
    
                data = i.recv(1024)

                data = data.replace('intranet', configure.getExternalServer())
                i.send(data)
                i.close()
            except:
                pass
                i.close()
                
    def setConfigure(self,  configure):
        self.__configure = configure
    def quit(self):
	pass

class Configure:
    def __init__(self):
        self.__port = 0
        self.__externalServer = ''

    def getPort(self):
        return self.__port
        
    def getExternalServer(self):
    	return self.__externalServer

    def setExternalServer(self, newName):
    	self.__externalServer = newName	

    def readConfigure(self, file):
        config = open(file)
        str = config.read()
        
        pos = str.find('port')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        port = ''
        for i in range( (pos+1), posFinal ):
            port+= str[i]
        self.__port = int(port)
        
        pos = str.find('externalServer')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ''
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__externalServer = tmp
        

configure = Configure()

configure.readConfigure("server.conf")

server = Server()
server.setConfigure(configure)
server.start()

while 1:
	read= str(raw_input("$>"))
	if read.upper() in ["EXIT","QUIT","SAIR"]:
		exit()
        else:
        	configure.setExternalServer(read)
        	print 'New external server configured: ',read
