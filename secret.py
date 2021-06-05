from socket import *
import threading

class serverThread(threading.Thread):
	def __init__(self, serverPort):
		threading.Thread.__init__(self)		
		self.serverPort = serverPort
		self.serverSocket = socket(AF_INET, SOCK_STREAM)
		self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.connectionThreads = []
	def run(self):
		self.serverSocket.bind(('', self.serverPort))
		self.serverSocket.listen(1)
		while True:
			print('Ready to serve..')
			print(self.connectionThreads)
			conn, addr = self.serverSocket.accept()
			request = conn.recv(5000).decode()
			print('Message recieved, opening new thread')
			self.connectionThreads.append(connectionThread(conn, request))
			self.connectionThreads[-1].daemon = 1
			self.connectionThreads[-1].start()
	def close(self):
		for t in self.connectionThreads:
			try:
				t.connSocket.shutdown(SHUT_RDWR)
				t.connSocket.close()
			except socket.error:
				pass
		self.serverSocket.shutdown(SHUT_RDWR)
		self.serverSocket.close()

class connectionThread(threading.Thread):
	def __init__(self, conn, message):
		threading.Thread.__init__(self)		
		self.connSocket = conn
		self.message = message
	def run(self):
		print(self.message)
		print('want:'   , self.connSocket)
		check = self.message.split()[1]
		print(check)
		if check == '/':
			header = 'HTTP/1.1 200 OK\r\n'
			header += "Content-Type: text/html; charset=utf-8\r\n"
			header += "\r\n"
			header = header.encode()
			login = open('index.html','rb')
					
			data = login.read()
			self.connSocket.send(header + data)
			
		else :
			file_name = check[1:]
			pos = file_name.find('.')
			file_type = file_name[pos+1:]
			print(file_type)
			if file_type == 'html':
				header = 'HTTP/1.1 200 OK\r\n'
				header += "Content-Type: text/html; charset=utf-8\r\n"
				header += "\r\n"
				header = header.encode()
				login = open(file_name,'rb')
				data = login.read()
				self.connSocket.send(header + data)
			elif file_type == 'jpg':
				header = 'HTTP/1.1 200 OK\r\n'
				header += "Content-Type: image/webp; charset=utf-8\r\n"
				header += "\r\n"
				header = header.encode()
				try:
					img1 = open(file_name, 'rb')
					data = img1.read()
					self.connSocket.send(header + data)
				except IOError:
					header = 'HTTP/1.1 200 OK\r\n'
					header += "Content-Type: text/html; charset=utf-8\r\n"
					header += "\r\n"
					header = header.encode()
					self.connSocket.send(header + "404 Not Found".encode())
			else:
				header = 'HTTP/1.1 200 OK\r\n'
				header += "Content-Type: text/html; charset=utf-8\r\n"
				header += "\r\n"
				header = header.encode()
				self.connSocket.send(header + "404 Not Found".encode())
		
		self.connSocket.shutdown(SHUT_RDWR)
		self.connSocket.close()

		
			
def main():
	server = serverThread(10080)
	server.daemon = 1
	server.start()
	end = input("Press enter to stop server...\n")
	server.close()
	print("Program complete")

main()
			

