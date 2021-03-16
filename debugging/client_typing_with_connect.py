import subprocess
import socket
import threading
import os
import sys

class ClientConsole():
    
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addressport = ("40.121.3.218", 2399)
        self.buffersize = 1024
        self.command = 'x'
        
    def UDPthread(self):
        t1 = threading.Thread(target=self.UDPreceive)
        t2 = threading.Thread(target=self.UDPsend)
        t1.start()
        t2.start()
        

    def UDPsend(self):
        while True:
            #print ("UDPsend loop <-> " , self.command)
            inputtxt = str.encode(input())
            self.sock.sendto(inputtxt ,self.addressport)
            print ("UDPsend loop <-> " , inputtxt)

    def UDPreceive(self):
        while True:
            #print ("UDPreceive loop")
            msgfromserver = self.sock.recvfrom(self.buffersize)
            msg = "Message from Server {}".format(msgfromserver[0])
            print(msg)
            self.command = msgfromserver[0].decode("utf-8")

    def UDPconnect(self):
        connectmsg = "Connect"
        self.sock.sendto(str.encode(connectmsg), self.addressport)
        newaddressport = self.sock.recvfrom(self.buffersize)
        self.addressport = ("40.121.3.218", int(newaddressport[0].decode("utf-8")))
        self.UDPthread()

if __name__ == '__main__':
    client = ClientConsole()
    client.UDPconnect()

