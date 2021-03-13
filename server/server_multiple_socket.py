import socket
import threading
import time
#import _thread

class ServerConsole():

    def __init__(self):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.localPort = 2399
        self.bufferSize = 1024
        self.sock.bind(("0.0.0.0", self.localPort))
        self.currClientAddress = "empty"
        self.threadCount = 0
        self.threadKill = None
        self.clients = set() #stores addresses of the clients
        #self.sockets = set() #stores sockets in case the server wants to access them
        print("UDP Server up and listening")

    def UDPthread(self, Client, address, threadcount):
        print("Thread " + str(self.threadCount) + " started")
        t1 = threading.Thread(target=self.UDPreceive, args=[Client,address, threadcount])
        t2 = threading.Thread(target=self.UDPsend, args=[Client,address, threadcount])
        t1.start()
        t2.start()

    def UDPreceive(self, Client, address, threadcount):
        while True:
            rectime = time.time()
            try:
                data, addr = Client.recvfrom(self.bufferSize)
            except socket.error:
                if(time.time()>rectime+60):
                    self.threadKill = Client
                    print(f"Killed Receive Thread {threadcount}")
                    return
                else:
                    continue
            else:
                assert address == addr
                self.currClientAddress = addr
                print("Message from Client:{}".format(data))
                print("Client IP Address:{}".format(addr))
    
    def UDPsend(self, Client, address, threadcount, msgFromServer="Test"):
        while True:
            #msgFromServer = input()
            #if self.currClientAddress != "empty":
            bytesToSend = str.encode(msgFromServer)
            Client.sendto(bytesToSend, address)
            time.sleep(3)
            if self.threadKill == Client:
                print(f"Killed Send Thread {threadcount}")
                self.threadKill = None
                return

    def UDPserver(self):
        while True:
            message, address = self.sock.recvfrom(self.bufferSize)
            self.clients.add(address)
            if len(self.clients) > self.threadCount:
                print("Connected to:{}".format(address))
                newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                newSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.localPort += 1 # new port
                newSock.bind(("0.0.0.0",self.localPort))
                self.sock.sendto(str.encode(str(self.localPort)), address)
                #_thread.start_new_thread(self.UDPthread, (newSock, ))
                primary = threading.Thread(target=self.UDPthread, args=[newSock, address, self.threadCount])
                primary.start()
                self.threadCount += 1
                #print("Thread Number: " + str(self.threadCount))

if __name__ == "__main__":
    server = ServerConsole()
    server.UDPserver()