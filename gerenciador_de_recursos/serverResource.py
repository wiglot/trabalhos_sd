# -*- coding: utf-8 -*-
import socket
import string
import random
from threading import Semaphore




class Server:
  def __init__(self, port):
      self.__port = int(port)
      self.__readLock = False
      self.__writeLock = False
      self.__locked = False

      self.__token = "".join([random.choice(string.letters+string.digits) for x in range(15)])
      self.__content = "Arquivo"


      self.__queue = []

      self.__conn = None
      self.__connSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      self.__connSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      while 1:
        try:
            self.__connSocket.bind( ("", self.__port) )
            self.__connSocket.listen(1)
            break
        except:
            self.__port += 1

  def run(self):
      print "Server started"
      while 1:
          #try:
              self.__conn, addr = self.__connSocket.accept()
              data = str(self.__conn.recv(32)).strip()
              if data.upper() == "READ" :
                  self.readRequest()
              elif data.upper() == "WRITE" :
                  self.writeRequest()
              elif data.upper() == "LOCK" :
                  self.lockRequest(addr)
              else:
                  self.__conn.send("Invalid String: "+data)
              self.__conn.close()
          #except:
              #break

  def readRequest(self):
     if self.__writeLock:
         self.__conn.send("No")
         return
     self.__readLock = True
     self.__conn.send("yes")
     if str(self.__conn.recv(32)).upper().strip() == "SEND":
        self.__conn.sendall(self.__content)#self.openFile())
     self.__readLock = False
  
  def writeRequest(self):
     if not self.__locked:
        self.__conn.send("ERROR: Must ask for a lock")
        return

     self.__writeLock = True

     while self.__readLock:
          pass
     
     self.__conn.send("SEND TOKEN")
     data = str(self.__conn.recv(1024)).strip()
     if data != self.__token:
          self.__conn.send("Invalid Token: " + data)
     else:
          self.__conn.send("SEND")
          self.__content = ""
          while 1:
              data = self.__conn.recv(4096)
              if not data:
                    break
              self.__content += data        

     self.__writeLock = False
     self.unlock()

  def lockRequest(self, addr):
      if (self.__locked):
          self.__conn.send("NO")
          port = int(self.__conn.recv(32))
          self.__queue.append((addr[0], port))
          return
      
      self.__conn.send("YES")
      data = str(self.__conn.recv(32)).strip()
      if data.upper() == "TOKEN":
           self.__conn.send(self.__token)
           self.__locked = True
      
  def unlock(self):
      self.__token = self.newToken()
      if len (self.__queue) > 0:
          client = self.__queue[0]
          self.__queue.remove(client)
          print "Lieberado para cliente: ", client, " with token: ", self.__token
          try:
              conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
              conn.connect(client)#send "UNLOCK" + new token to client
              conn.send("UNLOCK")
              data = str(conn.recv(32)).strip()
              if data.upper() == "TOKEN":
                  conn.send(self.__token)
              conn.close()
          except socket.error:
              print "Cant Connect to Cliente: ", client
              self.unlock()

      else:
          self.__locked = False

  def newToken(self):
      return "".join([random.choice(string.letters+string.digits) for x in range(15)])
      

server = Server(10000)
server.run()