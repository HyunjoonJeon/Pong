import socket
import threading

class ServerConsole():

    def __init__(self):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.localPort = 2399
        self.bufferSize = 1024
        self.sock.bind(("0.0.0.0", self.localPort))
        self.currClientAddress = "empty"
        print("UDP Server up and listening")

    def UDPthread(self):
        t1 = threading.Thread(target=self.UDPreceive)
        t2 = threading.Thread(target=self.UDPsend)
        t1.start()
        t2.start()

    def UDPreceive(self):
        while True:
            bytesAddressPair = self.sock.recvfrom(self.bufferSize)
            self.currClientMessage = bytesAddressPair[0]
            self.currClientAddress = bytesAddressPair[1]
            clientMsg = "Message from Client:{}".format(self.currClientMessage)
            clientIP = "Client IP Address:{}".format(self.currClientAddress)
            print(clientMsg)
            print(clientIP)
    
    def UDPsend(self, msgFromServer="Test"):
        while True:
            #msgFromServer = input()
            if self.currClientAddress != "empty":
                bytesToSend = str.encode(msgFromServer)
                self.sock.sendto(bytesToSend, self.currClientAddress)

if __name__ == "__main__":
    server = ServerConsole()
    server.UDPthread()