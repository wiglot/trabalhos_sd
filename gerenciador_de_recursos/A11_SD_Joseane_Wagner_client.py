# -*- coding: utf-8 -*-
import socket


class ClientListening(Threading):
    def __init__(self, client):
        Thread.__init__(self)
        self.__port = 2000
        self.__client = client

        self.__connSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__connSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while 1:
          try:
              self.__connSocket.bind( ("", self.__port) )
              self.__connSocket.listen(1)
              break
          except:
              self.__port += 1

    def getPort(self):
        return self.__port
  
    def run(self):
        while 1:
          i, addr = self.__connSocket.accept()
          data = str(i.recv(8)).strip()
          if data.upper() == "UNLOCK":
              i.send("TOKEN")
              token = i.recv(1024)
              self.__client.setToken()
              i.close()
              return


class Client():
	def __init__(self, ip, port):
		self.__port = int(port)
		self.__ip = ip

        self.__hasLock = False
        self.__token = ""
		self.__content = ""
		self.__conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.__conn.connect((self.__ip, self.__port))

	def readRequest(self):
		self.__conn.send("READ")
		data = self.__conn.recv(8).strip()
		
		if data.upper() in ["YES"]:
			self.__conn.send("SEND")

			while 1:
				data = self.__conn.recv(1024).strip()
				if not data:
					break	
				self.__content += data
					
		elif data.upper() in ["NO"]:
			pass
	
		
	def write(self):
		self.__conn.send("WRITE")
		data = self.__conn.recv(8).strip()
		
		if data.upper() in ["YES"]:
			self.__conn.sendall(self.__content)
		self.__hasLock = False
	
	def writeRequest(self):
		self.__conn.send("LOCK")
		data = self.__conn.recv(8).strip()
		
		if data.upper() in ["YES"]:
            self.__hasLock = True
			self.write()
		elif data.upper() in ["NO"]:
         		listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	                listening_socket.bind( ("", 22222) )
            	     	listening_socket.listen(1)
            	     	i, addr = self.listening_socket.accept()
	                data = i.recv(8).strip()
	                
	                if data.upper() in ["UNLOCKED"]:
	                	self.writeRequest()
	                else:
	                	pass        
		
		


