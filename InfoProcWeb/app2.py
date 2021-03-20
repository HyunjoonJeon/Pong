from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import socket
import threading
import time
import queue

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio=SocketIO(app)

class ServerConsole():

    def __init__(self):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.localPort = 2399
        self.bufferSize = 1024
        self.sock.bind(("0.0.0.0", self.localPort))
        self.playerCount = 0 #number of players in the game (MAX 2)
        self.connectQueue = queue.Queue() #create a queue system
        self.currentThreads = [(), ()] #list with top two addresses
        self.currentVals = ["0", "0"] #list with most recent values
        print("UDP Server up and listening")
        tcal = threading.Thread(target=self.UDPcalculate, args=[])
        tcal.start()

    def UDPthread(self, Client, address, threadCount):
        print("Thread " + str(threadCount) + " started")
        t1 = threading.Thread(target=self.UDPreceive, args=[Client, address, threadCount])
        t1.start()
        t2 = threading.Thread(target=self.UDPsend, args=[Client, address, t1, threadCount])
        t2.start()

    def UDPdisconnect(self, Client, address , threadCount):
        self.playerCount -= 1
        self.currentVals[threadCount-1] = "0"
        self.currentThreads[threadCount-1] = ()
        if not self.connectQueue.empty():
            address = self.connectQueue.get()
            newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            newSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.localPort += 1
            newSock.bind(("0.0.0.0",self.localPort))
            self.sock.sendto(str.encode(str(self.localPort)), address)
            primary = threading.Thread(target=self.UDPthread, args=[newSock, address, self.threadCount])
            primary.start()
            self.playerCount += 1
            self.currentThreads[threadCount - 1] = (newSock, address)
        


    def UDPreceive(self, Client, address , threadCount):
        while True:
            data, addr = Client.recvfrom(self.bufferSize)
            assert address == addr
            print("Message from Client:{}".format(data))
            print("Client IP Address:{}".format(addr))
            if "{}".format(data) == "b'd'":
                print(f"killing thread {threadCount} UDPreceive")
                self.UDPdisconnect((Client, address) , threadCount)
                return
            else:
                self.currentVals[threadCount-1] = "{}".format(data)

    def UDPcalculate(self):
        while True:
            if self.currentVals[0] or self.currentVals[1] is not "0": #list not empty
                data = self.currentVals[0] + self.currentVals[1]
                socketio.emit('my_response',{'data' : data, 'count' : "test"}, broadcast = True)
                            
    def UDPsend(self, Client, address, t1, threadCount, msgFromServer="x"):
        while True:
            #msgFromServer = input()
            bytesToSend = str.encode(msgFromServer)
            Client.sendto(bytesToSend, address)
            time.sleep(3)
            if not t1.is_alive():
                print(f"killing thread {threadCount} UDPsend")
                return

    def UDPserver(self):
        while True:
            message, address = self.sock.recvfrom(self.bufferSize)
            print("Connected to:{}".format(address))
            if(self.playerCount < 2):
                threadCount = 0
                if self.currentVals[0] is "0":
                    threadCount = 1
                elif self.currentVals[1] is "0":
                    threadCount = 2
                newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                newSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.localPort += 1
                newSock.bind(("0.0.0.0",self.localPort))
                self.sock.sendto(str.encode(str(self.localPort)), address)
                primary = threading.Thread(target=self.UDPthread, args=[newSock, address, threadCount])
                primary.start()
                self.playerCount += 1
                self.currentThreads[threadCount-1] = (newSock, address)
            else:
                self.connectQueue.put(address) #first in first out


@socketio.on("connect")
def connect():
    print("Client connected", request.sid)


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.event
def my_ping():
    emit('my_pong')


if __name__ == '__main__':
    udpxServer = ServerConsole()
    udpServer = threading.Thread(target=udpxServer.UDPserver)
    udpServer.daemon = True
    udpServer.start()

    socketio.run(app,debug=False, host='0.0.0.0')
