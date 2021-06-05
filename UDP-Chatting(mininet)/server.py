import sys
from time import sleep
from socket import *
import threading 
import time

serverPort = 10080
KeepAlive = []


def KeepAliveCheck(serverSocket, clients):
    global KeepAlive
    while True:
        time.sleep(10)
        index = 0
        for i in KeepAlive:
            if i[2] < time.time():
                ##lock
                disconnected_id = ""
                disconnected_info = ""
                disconnected_id = clients[index][0]
                disconnected_info = clients[index][1][0] + ":" + str(clients[index][1][1])
                del clients[index]
                del KeepAlive[index]
                print(f'{disconnected_id} is disconnected')
                pos = 0
                for j in clients:
                    infomsg = ""
                    disconnectedMsg = disconnected_id + " is disappeared" + "    " + disconnected_info
                    serverSocket.sendto(disconnectedMsg.encode('utf-8'),j[1])
                    for k in clients:
                        infomsg += k[0] +"|||" + k[1][0]+ "|||" + str(k[1][1]) + "|||"
                    serverSocket.sendto(infomsg.encode('utf-8'),i[1])
            index += 1

def server():   
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('',serverPort))
    print('listening on',serverPort)
    clients = []
    keepThread = threading.Thread(target=KeepAliveCheck, args=(serverSocket, clients,))
    keepThread.daemon = True
    keepThread.start()
    while True:
        msg, addr = serverSocket.recvfrom(1024)
        msg = msg.decode('utf-8')
        if msg.startswith('@'):
            if msg == '@show_list':
                smsg = ""
                for x in clients:
                    smsg += x[0] + " " + x[1][0] +":" + str(x[1][1]) + "\n"
                serverSocket.sendto(smsg.encode('utf-8'), addr)
            elif msg == '@exit':
                index = 0
                exit_id = ""
                exit_info = ""
                for y in clients:
                    if y[1] == addr:
                        exit_id = clients[index][0]
                        exit_info = clients[index][1][0] + ":" + str(clients[index][1][1])
                        del clients[index]
                        del KeepAlive[index]
                        break
                    index +=1
                print(f'{exit_id} is unregistered')
                for i in clients:
                    infomsg = ""
                    exitmsg = exit_id + " is deregistered" + "    " + exit_info
                    serverSocket.sendto(exitmsg.encode('utf-8'),i[1])
                    for k in clients:
                        infomsg += k[0] +"|||" + k[1][0]+ "|||" + str(k[1][1]) + "|||"
                    serverSocket.sendto(infomsg.encode('utf-8'),i[1])
            elif msg == '@keepAlive':
                pos = 0
                for i in clients:
                    if addr == i[1]:
                        KeepAlive[pos][2] = time.time() + 30
                    pos += 1

            continue        
        info = str(addr[0]) + ":" + str(addr[1])
        client_id = msg
        data = [client_id, (addr[0], addr[1])]
        dataWithTime = [client_id, (addr[0], addr[1]), time.time()+30]
        clients.append(data)
        KeepAlive.append(dataWithTime)
        print(client_id, info)
        
        ###broadcasting client info###
        for i in clients:
            infomsg = ""
            entermsg = client_id + "\t" + info
            serverSocket.sendto(entermsg.encode('utf-8'),i[1])
            for k in clients:
                infomsg += k[0] +"|||" + k[1][0]+ "|||" + str(k[1][1]) + "|||"
            serverSocket.sendto(infomsg.encode('utf-8'),i[1])
        
    serverSocket.close()

"""
Don't touch the code below
"""
if  __name__ == '__main__':
    server()


