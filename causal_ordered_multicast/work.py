#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  Por Joseane e wagner
  Baseado em  http://fiorix.wordpress.com/2008/05/24/servidor-e-cliente-multicast-em-python/
'''

import sys, struct, socket
from threading import  Thread

class Server(Thread):
    def __init__(self, messages, addr, port):
        Thread.__init__(self)
        self.__messages = messages
        self.__port = port
        self.__addr = addr
        self.__fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind udp port
        self.__fd.bind(('', self.__port))

        # set mcast group
        mreq = struct.pack('4sl', socket.inet_aton(self.__addr), socket.INADDR_ANY)
        self.__fd.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def parse(self, message):
        tmp = message.split('"')
        msg = tmp[1]
        tmp = tmp[0].split(';')
        ID = tmp[0]
        tmp.remove(ID)
        vector = []
        for i in tmp:
            vector.append(int(i))

        return [int(ID), vector, msg]

    def run(self):

        while 1:
            data, addr = self.__fd.recvfrom(1024)
            message = self.parse(data)
            if (message[0] != self.__messages.ID()):
                self.__messages.received(message[0], message[1], message[2]);
        
             
  
class Messages:
    def __init__(self, ID):
      self.__vector = []
      self.__queueMessages = []
      self.__myID = ID
      while len(self.__vector) < (ID+1):
           self.__vector.append(0)
    def sendVector(self):
        self.__vector[self.__myID] += 1;
        k = ''
        for i in self.__vector:
            k += ';'+str(i)
        return k

    def ID(self):
        return self.__myID

    def sumVector(self, vector):
        s = 0
        for i in vector:
            s += i
        return s;

    def canPrint(self, vector):
        if (self.sumVector(vector) <= (self.sumVector(self.__vector)+1)):
            return True
        return False

    def setVectot(self, vector):
        self.__vector = vector;
    
    def updateVector(self, ID):
        #if (len(self.__vector)+1) >= ID:
            #self.__vector[ID] += 1
        #else:
        while len(self.__vector) <= (ID+1):
            self.__vector.append(0)
        self.__vector[ID] += 1

    def received(self, ID, vector, message ):
        if self.canPrint(vector):
            self.updateVector(ID)
            print message
            for i in self.__queueMessages:
                if self.canPrint(i[0]):
                    self.__queueMessages.remove(i)
                    self.received(ID, i[0], i[1])
        else:
            self.__queueMessages.append((vector, message))

class Input:
    def __init__ (self, ID, addr, port):
        self.__addr = addr
        self.__port = int(port)
        self.__id = int(ID)
        self.__fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__messages = Messages(int(ID))
        self.__server = Server(self.__messages, self.__addr, self.__port)
        self.__server.start();
    def read(self):
        while 1:
          try:
              inp = str(raw_input(">"))
              if len(inp) > 0:
                  if inp[0] == '#':
                      print "At your command sir!"
                  else:
                      inp = str(ID) + self.__messages.sendVector() + '"' + inp + '"'
                      self.__fd.sendto(inp, (addr, port))
          except KeyboardInterrupt:
              self.quit();
              sys.exit(0);
    def quit(self):
          print "Kill server and flush messages."


if __name__ == '__main__':
    try:
        ID = sys.argv[1]
        addr = sys.argv[2]
        port = int(sys.argv[3])
    except IndexError:
        print 'use: %s ID addr port' % sys.argv[0]
        sys.exit(1)
    inp = Input(ID, addr, port)
    inp.read()
