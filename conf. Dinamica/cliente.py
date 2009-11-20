#!/usr/bin python
# -*- coding: utf-8 -*-
import urllib
import socket, os
from threading import Thread


class Configure:
    def __init__(self):
        self.__serverIP = '127.0.0.1'
        self.__port = 0

    def getServerPort(self):
        return self.__port
    def getServerIP(self):
        return self.__serverIP

    def readConfigure(self, file):
        config = open(file)
        str = config.read()
        
        pos = str.find('serverIP')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ""
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__serverIP = tmp

        pos = str.find('serverPort')
        pos =  str.find(' ', pos)
        posFinal = str.find(';', pos)
        tmp = ""
        for i in range( (pos+1), posFinal ):
            tmp+= str[i]
        self.__port = int(tmp)


class Peer:
    def __init__(self,  configure):
        self.__configure = configure;

        
    def startPeer(self):
    	user = str(raw_input("Entre com o usuário do proxy: "))
    	passwd = str(raw_input("Entre com a senha: "))
        proxies = {'http': 'http://'+user+':'+passwd+'@proxy.cta.intranet:3128'}    	
        passwd = '*******************' #paranoia mode on....
        
        while (1):
            #Espera entrada do usuário para receber o nome do arquivo


            filename = str(raw_input("Qual site buscar: (bye sai do programa) "))
            if filename.upper() in ['QUIT', 'EXIT', 'BYE', '0']:
                exit()
            elif filename == '':
                pass
            else:
                #try:
                   connServer = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                   newPort = self.__configure.getServerPort()
                   connServer.connect((self.__configure.getServerIP(), (newPort)))
            
                   connServer.send(filename)
                   newSite = str(connServer.recv(512))
                   connServer.close()
                   
                   print newSite
                   
                   f = urllib.urlopen(newSite, proxies=proxies)
                   contents = f.read()
                   f.close()
                   print contents

                       
                #except:
                #    print "Can't connect to tracker ",  self.__configure.getServerIP(), ':', newPort
                #    print "Change tracker config at 'peer.conf' and try again."
                #    pass
                            
    
configure = Configure()
configure.readConfigure("client.conf")

peer = Peer(configure)
peer.startPeer()
