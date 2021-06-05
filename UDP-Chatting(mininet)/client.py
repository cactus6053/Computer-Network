import sys
from socket import *
import threading
import time

serverIP = '10.0.0.3'
serverPort = 10080
clientPort = 10081
exit = 0

def recvmsg(sock, clients):
    while True:
        msg, addr = sock.recvfrom(1024)
        msg = msg.decode('utf-8')
        flag = 0
        from_id = ""
        ###check###
        for i in clients:
            if i[1] == addr:
                flag = 1
                from_id = i[0]
        if flag ==0 : #message from server
            if msg.endswith('|||'): ###@show_list###
                pass
            elif msg.find('is disappeared')>=0:
                print(msg)

            else: ###@enter or exit ####
                print(msg) #enter msg or exit msg
                client_info, addr = sock.recvfrom(1024) #update clients
                client_info = client_info.decode('utf-8')
                if client_info.endswith('|||'):
                    client_info = client_info.split("|||")
                    clients.clear()
                    length = len(client_info)
                    for i in range(0, length-2, 3):
                        data = [client_info[i], (client_info[i+1], int(client_info[i+2]))]
                        clients.append(data)
        elif flag == 1:
            print(f'From {from_id} [{msg}]')

def sendmsg(sock, clientID, clients,serverIP,serverPort):
    global exit
    while True:
        msg = input("")
        smsg = msg.encode('utf-8')

        if msg[0:5] == '@exit':
            exit = 1
            print(f'# {clientID} terminates')
            sock.sendto(smsg, (serverIP, serverPort))
            return
        elif msg[0:5] == '@chat':
            client_id = msg.split(" ")[1]
            smsg = msg.split(" ")[2:]
            smsg = ' '.join(smsg).encode('utf-8')
            flag = 0

            for i in clients:
                if client_id == i[0]:
                    flag = 1
                    sock.sendto(smsg,i[1])
            
        elif msg[0:10] == '@show_list':
            sock.sendto(smsg, (serverIP, serverPort))

def keepalive(conn_sock, serverPort, clientID):
    global exit 
    keepmsg = '@keepAlive'.encode('utf-8')
    while True:
        time.sleep(25)
        if exit == 1:
            return
        conn_sock.sendto(keepmsg,(serverIP, serverPort))

def client(serverIP, serverPort, clientID):
    
    conn_sock = socket(AF_INET, SOCK_DGRAM)
    conn_sock.bind(('',clientPort))
    conn_sock.setsockopt(SOL_SOCKET,SO_REUSEPORT, 1)
    conn_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    conn_sock.sendto(clientID.encode('utf-8'),(serverIP, serverPort))
    clients = []
   
    sendThread = threading.Thread(target=sendmsg, args=(conn_sock, clientID, clients,serverIP,serverPort,))
    sendThread.daemon = True
    sendThread.start()

    recvThread = threading.Thread(target=recvmsg, args=(conn_sock, clients,))
    recvThread.daemon = True
    recvThread.start()

    keepThread = threading.Thread(target=keepalive, args=(conn_sock,serverPort, clientID,))
    keepThread.daemon = True
    keepThread.start()
    
    while True:
        try:
            if exit == 1:
                return
            time.sleep(10)
        except KeyboardInterrupt:
            print('# stop the program by Ctrl-C')
            return
"""
Don't touch the code below!
"""
if  __name__ == '__main__':
    clientID = input("Enter ID : ")
    client(serverIP, serverPort, clientID)


