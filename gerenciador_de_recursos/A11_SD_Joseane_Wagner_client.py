import socket

class Client():
	def __init__(self, ip, port):
		self.__port = int(port)
		self.__ip = ip
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
			
	def writeRequest(self):
		self.__conn.send("LOCK")
		data = self.__conn.recv(8).strip()
		
		if data.upper() in ["YES"]:
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
		
		


