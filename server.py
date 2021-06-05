from socket import *
import threading
import time

cookies = {}

class serverThread(threading.Thread):
	global cookies

	def __init__(self, serverPort):
		threading.Thread.__init__(self)		
		self.serverPort = serverPort
		self.serverSocket = socket(AF_INET, SOCK_STREAM)
		self.serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		self.connectionThreads = []

	def run(self):
		self.serverSocket.bind(('', self.serverPort))
		self.serverSocket.listen(5)
		while True:
			print('Ready to listen')
			conn, addr = self.serverSocket.accept()
			request = conn.recv(1000).decode()
			print('Message recieved, opening new thread')
			self.connectionThreads.append(connectionThread(conn, addr, request))
			
			if request:
				if request.split()[0] == 'POST':
					cookie_msg = request.split()[-1]	
					name_pos = cookie_msg.find('&')
					Usr_ID = cookie_msg[3:name_pos] 
					Usr_Password = cookie_msg[name_pos+10:]
					cookie_expire_time = time.time()+30
					cookies[addr[0]] = (Usr_ID, Usr_Password, cookie_expire_time)		 	
		
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

	global cookies
	
	def __init__(self, conn, addr, message):
		threading.Thread.__init__(self)		
		self.connSocket = conn
		self.address = addr
		self.message = message

	def make_header(self, response_number):
		head = ''
		if response_number == 200:
			head += 'HTTP/1.1 200 OK\r\n'		
		elif response_number == 404:
			head += 'HTTP/1.1 404 Not Found\r\n'
		elif response_number == 403:
			head += 'HTTP/1.1 403 Forbidden\r\n'

		cur_time = time.time()
		current_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(cur_time))
		head += f'Date: {current_time} GMT\r\n'
		head += 'Server: Python 3.8\r\n'
		expire_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(cur_time+30))
		head += f'Expries: {expire_time} GMT\r\n'
		head += "Connection: keep-alive\r\n"
		head += "\r\n"

		return head
	
	def cookies_check(self, client_IP):
		current_time = time.time()
		flag = 0 # client IP check
		flag1 = 0 # expire_time check
		for key in cookies.keys():
			if key == client_IP:
				flag = 1
		if flag == 1:
			if current_time > cookies[client_IP][2]:
				del cookies[client_IP]
			else:
				flag1 = 1
		
		if flag == 1 and flag1 == 1:
			return 1
		else:
			return 0

	def run(self):
		cookie = self.cookies_check(self.address[0])
		check = self.message.split()[1]
		print(self.message)
		if check == '/':
			if self.message.split()[0] == 'GET':
				if cookie == 0:
					header = self.make_header(200)
					header = header.encode()
					login = open('index.html','rb')		
					data = login.read()
					self.connSocket.send(header + data)
				else:
					header = self.make_header(200)
					header = header.encode()
					login = open('secret.html','rb')		
					data = login.read()
					self.connSocket.send(header + data)

			elif self.message.split()[0] == 'POST':
				header = self.make_header(200)
				header = header.encode()
				login = open('secret.html','rb')		
				data = login.read()
				self.connSocket.send(header + data)			

		elif cookie == 1:
			file_name = check[1:]
			pos = file_name.find('.')
			file_type = file_name[pos+1:]
			if file_type == 'html':
				if file_name == 'cookie.html':
					header = self.make_header(200)
					header = header.encode()
					data = b"<html><head><title>Welcome "
					data += cookies[self.address[0]][0].encode()
					data += b"</title></head><body><br><br>Hello "
					data += cookies[self.address[0]][0].encode()
					data += b"<br><br>"
					left_time = int(cookies[self.address[0]][2] - time.time())
					data += str(left_time).encode()
					data += b" seconds left until your cookie expires."
					self.connSocket.send(header + data)

				else:
					header = self.make_header(200)
					header = header.encode()
					try:
						login = open(file_name,'rb')
						data = login.read()
					except IOError:
						header = self.make_header(404)
						header = header.encode()
						data = b"<html><body><h1>404 Not Found</h1></body></html>"
					self.connSocket.send(header + data)
			elif file_type == 'jpg':
				header = self.make_header(200)
				header = header.encode()
				try:
					img1 = open(file_name, 'rb')
					data = img1.read()
					self.connSocket.send(header + data)
				except IOError:
					header = self.make_header(404)
					header = header.encode()
					rdata = b"<html><body><h1>404 Not Found</h1></body></html>"
					self.connSocket.send(header + rdata)
			else:
				header = self.make_header(404)
				header = header.encode()
				data = b"<html><body><h1>404 Not Found</h1></body></html>"
				self.connSocket.send(header + data)

		else:
			header = self.make_header(403)
			header = header.encode()
			data = b"<html><body><h1>403 Forbidden</h1></body></html>"
			self.connSocket.send(header + data)
		

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
			

