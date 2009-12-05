# -*- coding: utf-8 -*-
import socket
from threading import Thread


class ClientListening(Thread):
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
              token = str(i.recv(1024))
              i.close()
              self.__connSocket.close()
              self.__connSocket.close()
              self.__client.setToken(token)
              return


class Client():
    def __init__(self, ip, port):
        self.__port = int(port)
        self.__ip = ip

        self.__hasLock = False
        self.__token = ""
        self.__content = ""

        self.__listen = None
        self.__conn = None
        
    def content(self):
        return self.__content

    def setContent(self, newContent):
        self.__content = newContent

    def execute(self, cmd):
        cmd = cmd.upper()
        if not cmd in ["READ", "WRITE", "LOCK"]:
            print "Invalid command. Valid commands: ", ["READ", "WRITE", "LOCK"]
            return

        self.__conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__conn.connect((self.__ip, self.__port))
        
        if cmd == "READ":
            self.readRequest();
        elif cmd == "WRITE":
            self.writeRequest()
        else:
            self.lockRequest()
        #self.__conn.disconnect()

    def setToken(self, token):
        self.__token = token
        self.__hasLock = True
        self.__listen = None

    def readRequest(self):
          self.__conn.send("READ")
          data = self.__conn.recv(8).strip()
          
          if data.upper() in ["YES"]:
              self.__conn.send("SEND")
              self.__content = ""
              while 1:
                  data = self.__conn.recv(1024).strip()
                  if not data:
                      break
                  self.__content += data
					
          elif data.upper() in ["NO"]:
              pass
	
		
    def writeRequest(self):
        if not self.__hasLock:
            print "Must ask for a lock first."
            return
        self.__conn.send("WRITE")
        data = self.__conn.recv(16).strip()
        print data
        if data.upper() == "SEND TOKEN":
            self.__conn.send(self.__token)
            data = self.__conn.recv(16).strip()
            print data
            if data.upper() in ["SEND"]:
                self.__conn.sendall(self.__content)
                print self.__content
        self.__hasLock = False
	
    def lockRequest(self):
        if self.__hasLock:
            print "Allready have a lock. must use it (write a content) first!."
            return
        self.__conn.send("LOCK")
        data = self.__conn.recv(32).strip()

        if data.upper() == "YES":
            self.__conn.send("TOKEN")
            self.setToken(str(self.__conn.recv(32).strip()))
            
        else:
            self.__listen = ClientListening(self)
            self.__listen.start()
            self.__conn.send(str(self.__listen.getPort()))


if __name__ == '__main__':
    ip = raw_input("Enter server IP: ")
    port = raw_input("Enter server IP: ")
    client = Client(ip, port)
    inp = ""
    while not inp.upper() in ["EXIT", "QUIT", "E", "Q"]:
        inp = raw_input("#>")
        if inp.upper() == "WRITE":
            newContent = raw_input("# Enter Content> ")
            client.setContent(newContent)

        client.execute(inp)
        print client.content()
    exit(0)
