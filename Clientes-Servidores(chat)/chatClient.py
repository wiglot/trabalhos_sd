# -*- coding: utf-8 -*-

from optparse import OptionParser
from threading import  Thread
import  socket

class ClientReceiver(Thread):
    def __init__ (self, client):
        Thread.__init__(self)
        self.__client = client
        self.__serverPort = 0
        self.__quit = False
        

    def setPort(self, port):
        self.__serverPort = int(port)
    def quit(self):
        self.__quit = True
        
        
    def run(self):
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        
        try:
          conn.connect((self.__client.serverIP(), self.__serverPort))
          conn.send("I AM HERE")
          if (conn.recv(16) == "CONNECTED"):
            while not self.__quit:
                received = ""
                conn.settimeout(3)
                try:
                  rcv = conn.recv(4096).strip()
                  conn.send("OK")
                  if rcv == "DISCONNECT":
                      self.__client.disconnect()
                  else:
                      received += rcv
                  
                  if received:
                    self.__client.showMessage(received)
                except:
                  pass
          conn.close()
        except:
          print "Error connection to: ", self.__client.serverIP(), self.__serverPort

class Client:
    def __init__(self, id):
        self.__receiver = ClientReceiver(self)
        self.__serverPort = 0
        self.__serverIP = ""
        self.__myID = id

    def showMessage(self, message):
        print message
    def serverIP(self):
        return self.__serverIP
    def setServerIP(self, ip):
        self.__serverIP = ip

    def serverPort(self):
        return self.__serverPort
    def setServerPort(self, port):
        self.__serverPort = int(port)

    def connectServer(self, server, port):
        if self.connected():
            self.disconnect();
        
        self.__serverPort = int(port)
        self.__serverIP = server
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        try:
          conn.connect((self.__serverIP, self.__serverPort))

          conn.send("LOGIN:"+self.__myID)
          rcv = str(conn.recv(32))
          receivePort = rcv.split(":")
          if receivePort[0].upper() != "PORT":
              showMessage("ERROR: "+ rcv)
              return False
          self.__receiver = ClientReceiver(self)
          self.__receiver.setPort(int(receivePort[1]))
          self.__receiver.start()
          
        except:
          print "Cannot connect to server: ", self.__serverIP, self.__serverPort
          return False
        return True  

    def connected(self):
        if self.__serverIP == "" or self.__serverPort == 0:
           return False
        return True

    def disconnect(self):
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        try:
          conn.connect((self.__serverIP, self.__serverPort))
          conn.send ("LOGOFF:"+self.__myID)
          self.showMessage("Disconnected from server: "+ self.__serverIP)
        except:
          print "ERRO: Cannot connecto to server: "+ self.__serverIP
        self.__receiver.quit()
        
        self.setServerIP("")
        self.setServerPort(0)

    def sendMessage(self, userID, message):

        message = self.__myID+": "+message
      
        conn = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        try:
          conn.connect((self.__serverIP, self.__serverPort))
          conn.send ("MSG:"+userID)
          rcv = str(conn.recv(32)).strip()
          if rcv.upper() == "SEND MSG":
              conn.sendall(message)
              rcv = str(conn.recv(32)).strip()
              if rcv.upper() != "DELIVERED":
                  self.showMessage(rcv)
          else:
              self.showMessage(rcv)
          conn.close()
        except:
          print "ERRO: Cannot connecto to server: "+ self.__serverIP
    




parser = OptionParser()
parser.add_option("-s", "--server", dest="server",
                  help="Connects to server SERVER", metavar="SERVER")
parser.add_option("-p", "--port", dest="port",
                  help="Connects to server at PORT", metavar="PORT")
parser.add_option("-i", "--id", dest="id",
                  help="Uses ID as default ID", metavar="ID")

(options, args) = parser.parse_args()

if options.id == None:
  id = str(raw_input("Entre com seu ID: ")).strip()
else:
  id = options.id

server = options.server
port = options.port
if options.server == None:
  server = str(raw_input("Entre com um endereço de servidor válido: ")).strip()
  if len(server.split(":")) == 1 and options.port == None:
    port = int(raw_input("Entre com a porta do servidor: "))
  elif len(server.split(":")) == 2:
    port = server.split(":")[1]
    server = server.split(":")[0]
  elif options.port != None:
    port = int(options.port)
  else:
    print "No port given, exiting."
    exit()

client = Client(id)
client.connectServer(server, port)

while 1:
 
    inp = str(raw_input("#")).strip()
    if len(inp) > 0 and inp[0] == '!':
      inp = inp.split(" ", 1)
      if inp[0].upper() == "!EXIT":
          if client.connected():
            client.disconnect()
          exit()
      elif inp[0].upper() == "!CLIENTS":
          print "Clients"
      elif inp[0].upper() == "!CONNECT":
          if not client.connected():
            server = inp[1].split(":")[0]
            port = inp[1].split(":")[1]
            client.connectServer(server, port)
          else:
            print "Allready connected to a server. Server: ", client.serverIP()
      elif inp[0].upper() == "!DISCONNECT":
          if client.connected():
            client.disconnect()
          else:
            print "Not connected to any server."
      else :
          print "Comando inválido! Digite 'help' para ajuda"
    elif len(inp) > 0 and inp[0] == '@':
      parse = inp.split(" ",1)
      client.sendMessage(parse[0].split("@")[1], parse[1])
    else:
        print "Cliente de troca de mensagens."
        print "Comandos: "
        print "@User message         envia mensagem 'message' para o usuário 'User'"
        print "!connect Server:Port  conecta ao 'servidor' na porta 'port'."
        print "!disconnect           desconecta do servidor"
        print "!exit                 fecha o cliente e encerra a conexão."
