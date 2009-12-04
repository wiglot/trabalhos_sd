# -*- coding: utf-8 -*-
import socket

class Server:
  def __init__(self, port):
      self.__port = int(port)
      self.__readLock = False
      self.__writeLock = False
      self.__locked = False

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
      print "Hey"
      while 1:
          try:
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
          except:
              break

  def readRequest(self):
     if self.__writeLock:
         self.__conn.send("No")
         return
     self.__readLock = True
     self.__conn.send("yes")
     if str(self.__conn.recv(32)).upper().strip() == "SEND":
        self.__conn.sendall("kkkrrr")#self.openFile())
     self.__readLock = False
  
  def writeRequest(self):
     while self.__readLock:
          pass

     self.__writeLock = True
     self.__conn.send("SEND")
     f = openFile() 
     while 1:
	  data = self.__conn.recv(4096)
	  if not data:
              break
          f.write(data)
     f.close()
     self.__writeLock = False
     self.unlock()

  def lockRequest(self, addr):
      if (self.__locked):
          self.__conn.send("NO")
          port = int(self.__conn.recv(32))
	  self.__queue.append((addr, port))
          return
      self.__locked = True
      self.__conn.send("YES")
      
  def unlock(self):
      self.__locked = False
      client = self.__queue[len(self.__queue)-1]
      self.__queue.remove(client)
      #send "UNLOCK" to client


server = Server(10000)
server.run()