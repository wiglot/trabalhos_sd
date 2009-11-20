# -*- coding: utf-8 -*-
#/usr/bin/python

from threading import  Thread
import  socket
import time

class ClientHandler(Thread):
  '''
    Trata as conexões recebidas dos outros servidores.
    Aceita conexões dos clientes e se preciso (signin) adiciona cliente ao servidor.
    Tambem fica como responsável em criar os objetos Clients os quais manteram uma conexão ativa com os clientes
  '''
  def __init__(self, server):
      Thread.__init__(self)
      self.__server = server
      self.__connection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      self.__quit = False
  def getServer(self):
      return self.__server
  def run(self):
      self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
          self.__connection.bind( ("", self.__server.getClientPort()) )
          self.__connection.listen(2)
      except:
          print "Não foi possível abrir a porta ", self.__server.getClientPort()
          exit()

      while not self.__quit:
          conn, addr = self.__connection.accept()
          #conn.settimeout(2)
          #try:
          recv = str(conn.recv(1024)).strip()
          data = recv.split(':')
          if data[0].upper() == "LOGIN" and len(data) == 2:
              #Cria um novo clients e envia a porta para o cliente
              #ret = [port:num | FAIL:description]
              ret = self.__server.createClientConnect(data[1]);
              conn.send(ret)
              #self.getServer().clientSign(self.getServer().getID(), data[1], 1 )
          elif data[0].upper() == "LOGOFF" and len(data) == 2:
              conn.send("Ok")
              self.getServer().clientSign(self.getServer().getID(), data[1], 0 )
          elif data[0].upper() == "MSG" and len(data) == 2:
              if self.__server.isClientConnected(data[1]):
                  client = data[1]
                  conn.send("SEND MSG")
                  data = conn.recv(8192)
                  if self.__server.deliveryMsgToClient(client, data):
                      conn.send("DELIVERED")
                  else:
                      conn.send("MSG_FAILURE:"+client)
              else:
                  conn.send("ID_FAILURE: "+ data[1] + " is offline.")
          else:
              conn.send("INVALID_OP: "+recv)
          #except:
            #pass
          conn.close()
          

  def quit(self):
      self.__quit = True
      #self.__connection.close()

class ServerHandler(Thread):
  '''
    Trata as conexões recebidas dos outros servidores.
    Ao rece
  '''
  def __init__(self, server):
    	Thread.__init__(self)
        self.__port = 0
        self.__quit = False
        self.__server = server
        self.__connection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

  def quit(self):
      self.__quit = True
      self.__connection.close()
  
  def setServer(self, server):
    self.__server = server

  def getServer(self):
    return self.__server

  def run(self):
      self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
          self.__connection.bind( ("", self.__server.getPort()) )
          self.__connection.listen(2)
      except:
          print "Não foi possível abrir a porta ", self.__server.getPort()
          exit()
      
      while not self.__quit:
          conn, addr = self.__connection.accept()
          recv = str(conn.recv(1024)).strip()
          data = recv.split(':')
          if data[0].upper() == "LOGIN" and len(data) == 3:
              conn.send(self.getServer().addServer(data[1], addr[0], data[2] ))
          elif data[0].upper() == "LOGOFF" and len(data) == 2:
              conn.send(self.__server.removeServer(data[1]) )
          elif data[0].upper() == "MSG" and len(data) == 2:
              if self.__server.isClientConnected(data[1]):
                  client = data[1]
                  conn.send("SEND MSG")
                  data = conn.recv(8192)
                  if self.__server.deliveryMsgToClient(client, data):
                      conn.send("DELIVERED")
                  else:
                      conn.send("MSG_FAILURE:"+client)
              else:
                  conn.send("ID_FAILURE: "+ data[1] + " is offline.")
          elif data[0].upper() == "SIGN" and len(data) == 4:
              conn.send("Ok")
              self.__server.clientSign(data[1], data[2], data[3])
          elif data[0].upper() == "LIST" and len(data) == 3:
              conn.send("Ok")
              if data[1].upper() == "CLIENTS":
                  self.__server.sendListOfClients(data[2])
          else:
              conn.send("INVALID_OP: "+recv)
          conn.close()


#######################################################################

class Server(Thread):
    '''
    Mantem as conexões e se comunica com os demais servidores.
    Recebe as mensagens dos handlers (de clientes e de servidores) tratando-as.
    '''
    def __init__(self):
        Thread.__init__(self)
        self.__clients = []
        self.__servers = []
        self.__handler = ServerHandler(self)
        self.__clientHandler = ClientHandler(self)
        self.__myID = ""
        self.__port = 0
        self.__ClientPort = 0


    def run (self):
        self.__handler.start()
        self.__clientHandler.start()
        ret = self.sayLoginToServers()
        for i in ret:
          if i[0] == "OK":
            conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            try:
              conn.connect((i[1].getIP(), i[1].getPort()))
              conn.send("LIST:CLIENTS:"+self.getID())
              rcv = (conn.recv(32)).strip()
              if  rcv.upper() != "OK":
                  print rcv
              conn.close()
              break
            except:
              pass
            
            
    
    def isClientConnected(self, ID):
        for i in range(len(self.__clients)):
            if self.__clients[i].getID() == ID:
                  return self.__clients[i].isOnline()
        return False


    def sendMsgToServer(self, client, msg):
        server = 0
        if not client.isOnline():
            return False
        for i in self.__servers:
            if i.getID() == client.getServer():
              server = i
        if server == 0:
            return False

        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        try:
          conn.connect((server.getIP(), server.getPort()))

          conn.send("MSG:"+client.getID())
          rcv = str(conn.recv(16)).strip()

          if rcv.upper() != "SEND MSG":
            conn.close()
            return False
          conn.send(str(msg))
          rcv = str(conn.recv(16)).strip()
          if rcv.upper() != "DELIVERED":
            conn.close()
            return False
          conn.close()
        except:
          print "Server: "+i.getID()+" offline."
          return False
        return True

    def deliveryMsgToClient(self, ID, msg):
        for i in self.__clients:
            if i.getID() == ID:
                if i.getServer() == self.getID():
                    return i.message(msg)
                else:
                    return self.sendMsgToServer(i, msg)
        return False


    def removeServer(self, ID):
        if ID == self.getID():
            return "FAIL: Cannot pullof others servers"
        for i in self.__servers:
            if i.getID() == ID:
                self.__servers.remove(i)
                return "REMOVED";
        return "FAIL: Server '"+ID+"' not found"


    def addServer(self, ID, IP, port):
        if ID == self.getID():
            return "FAIL: Server already logged"
        for i in range(len(self.__servers)):
            if ID == self.__servers[i].getID():
                self.__servers[i].update(IP, port)
                return "OK";
        srv = Servers()
        srv.setID(ID)
        srv.setIP(IP)
        srv.setPort(port)
        self.__servers.append(srv)        
        return "OK";

    def clientSign(self, serverID, clientID, tp):
      '''
      serverID : ID of server where client is connected
      clientID: ID of client
      tp: 1 is signin and 0 is signoff
      in case of a new client, ignores tp == 0 or create a neu client if tp == 1.
      '''
      #if is a sign is this server send messages to others servers...
      if serverID == self.getID():
          self.sayToServers("SIGN:"+self.getID()+":"+clientID+":"+str(tp))

      for i in range(len(self.__clients)):
          if self.__clients[i].getID() == clientID:
              self.__clients[i].updateState(serverID, tp)
              return
      client = Clients()
      client.setID(clientID)
      client.setServer(serverID)
      client.setOnline(tp)
      self.__clients.append(client)

    def createClientConnect(self, clientID):
      for i in self.__clients:
         if i.getID() == clientID:
            self.__clients.remove(i)
      client = Clients()
      self.__clients.append(client) 
      client.setID(clientID)
      client.setServer(self.getID())
      client.setOnline(1)
      port = client.openPort(self.getClientPort()+1)

      client.start()
      self.clientSign(self.getID(), clientID, 1)
      return "PORT:"+str(port)

    def quit(self):
      for i in self.__clients:
          if i.getServer() == self.getID() and i.isOnline():
            i.quit()
      self.__handler.quit()
      self.__clientHandler.quit()
      time.sleep(1)
    
    def setID(self, newID):
      self.__ID = newID
    def getID(self):
      return self.__ID
    def setPort(self, port):
       self.__port = int(port)
    def getPort(self):
       return self.__port
    def setClientPort(self, port):
       self.__ClientPort = int(port)
    def getClientPort(self):
       return self.__ClientPort
    def clients(self):
        return self.__clients
    def servers(self):
        return self.__servers


    def sayToServers(self, message):
        '''
        send a message to others servers, and store all the returns
        '''
        returns = []
        for i in self.__servers:
          conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
          try:
            conn.connect((i.getIP(), i.getPort()))
            conn.send(message)
            returns.append([i.getID(), str(conn.recv(256))])
            conn.close()
          except:
            pass
        return returns



    def sayLoginToServers(self):
      ret = []
      for i in self.__servers:
          conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
          try:
            conn.connect((i.getIP(), i.getPort()))
            conn.send("LOGIN:"+self.getID()+":"+str(self.getPort()))
            rcv = conn.recv(256)
            ret.append( (rcv, i) )
            if rcv.upper() != "OK":
                print rcv            
            conn.close()
          except:
            print "server: "+i.getID()+" offline."
            ret.append(("FAIL", i))
          
      return ret


    def sendListOfClients(self, serverID):
        server = None
        for server in self.__servers:
            if server.getID() == serverID:
               break
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        conn.connect((server.getIP(), server.getPort()))
        for i in self.__clients:
          tp = 0
          if i.isOnline():
            tp = 1
          conn.send("SIGN:"+i.getServer()+":"+i.getID()+":"+str(tp))
          rcv = conn.recv(32)
          


    def sayLogoffToServers(self):
      for i in self.__servers:
          conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
          try:
            conn.connect((i.getIP(), i.getPort()))
            conn.send("LOGOFF:"+self.getID())
            rcv = conn.recv(256)
            if rcv.upper() != "REMOVED":
                print rcv
            conn.close()
          except:
            pass

    def openConfig(self, configFile):
        config = open(configFile)
        file = str(config.read()).strip()
        file = file.split(";")
        for i in file:
            if i:
              line = i.strip().split(":")
              if line[0].upper() == 'NAME' and len(line) == 2:
                  self.setID(line[1])
              elif line[0].upper() == 'SERVER_PORT' and len(line) == 2:
                  self.setPort(line[1])
              elif line[0].upper() == 'CLIENT_PORT' and len(line) == 2:
                  self.setClientPort(line[1])
              elif len(line) == 4:
                  self.addServer(line[1], line[2], line[3])
              else:
                  print "line '"+i+"' in file '"+configFile+"' is not in a valid format"
        config.close()



###################################################################################

class Clients(Thread):
  '''
  Informações do tipo
      Em qual server cliente se encontra.
      Cliente está conectado?
      Qual ID do cliente?
      Para clientes do servidor incia uma thread e espera a conexão do cliente, mantendo ativa para o envio de mensagens.
  '''
  def __init__(self):
      Thread.__init__(self)
      self.__ID = ""
      self.__serverID = ""
      self.__online = False
      self.__port = 0
      self.__conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
      self.__connection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

  def setOnline(self, tp):
      self.__online = False
      if str(tp) == "1":
          self.__online = True
          
  def setID(self, ID):
      self.__ID = ID
  def setServer(self, serverID):
      self.__serverID = serverID
  def getServer(self):
      return self.__serverID 
  def getID(self):
      return self.__ID
  def isOnline(self):
      return self.__online
  def updateState(self, serverID, tp):
      self.setServer(serverID)
      self.setOnline(tp)
  def message(self, message):
      self.__conn.send(message)
      self.__conn.settimeout(5)
      try:
        rcv = str(self.__conn.recv(32)).strip()
        self.__conn.settimeout(None)
        if rcv.upper() == "OK":
            return True
      except:
        self.__conn.settimeout(None)
      return False

  def openPort(self, port):
      self.__port = int(port)
      self.__connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      while 1:
        try:
            self.__connection.bind( ("", self.__port) )
            self.__connection.listen(1)
            break;
        except:
            self.__port += 1
      return self.__port
  def run(self):
      self.__conn, addr = self.__connection.accept()
      recv = str(self.__conn.recv(1024)).strip()
      if recv.upper() == "I AM HERE":
          self.__conn.send("CONNECTED")
      else:
          self.__conn.close()
          self.__conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

  def quit(self):
      self.__conn.send("DISCONNECT")
      self.__conn.recv(32)
      self.__conn.close()

class Servers:
    def __init__(self):
        self.__ID = ""
        self.__IP = "127.0.0.1"
        self.__port = 0
    def setID(self, ID):
        self.__ID = ID
    def setIP(self, IP):
        self.__IP = IP
    def setPort(self, port):
        self.__port = int(port)
    def getID(self):
        return self.__ID
    def getIP(self):
        return self.__IP
    def getPort(self):
        return self.__port
    def update(self, IP, port):
        self.setIP(IP)
        self.setPort(port)

server = Server()
server.openConfig("server.conf")
server.start()

while 1:
    inp = str(raw_input("#"))
    if inp.upper() == "EXIT":
        server.sayLogoffToServers()
        server.quit()
        exit()
    elif inp.upper() == "SAY":
        server.sayLoginToServers();
    elif inp.upper() == "SERVERS":
        for i in server.servers():
            print i.getID(), i.getIP(), i.getPort()
    elif inp.upper() == "CLIENTS":
        for i in server.clients():
            print i.getID(), i.isOnline()