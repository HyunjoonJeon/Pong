from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import socket
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio=SocketIO(app)

class ServerConsole():

    def __init__(self):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.localPort = 2399
        self.bufferSize = 1024
        self.sock.bind(("0.0.0.0", self.localPort))
        self.threadCount = 0
        self.clients = set() #stores addresses of the clients
        #self.sockets = set() #stores sockets in case the server wants to access them
        print("UDP Server up and listening")

    def UDPthread(self, Client, address, threadCount):
        print("Thread " + str(self.threadCount) + " started")
        t1 = threading.Thread(target=self.UDPreceive, args=[Client,address, threadCount])
        t1.start()
        t2 = threading.Thread(target=self.UDPsend, args=[Client,address, t1, threadCount])
        t2.start()

    def UDPreceive(self, Client, address, threadCount):
        while True:
            data, addr = Client.recvfrom(self.bufferSize)
            assert address == addr
            print("Message from Client:{}".format(data))
            print("Client IP Address:{}".format(addr))
            if "{}".format(data) == "b'd'":
                print(f"killing thread {threadCount} UDPreceive")
                return
            else:
                socketio.emit('my_response',{'data' : "{}".format(data), 'count' : addr}, broadcast = True)

    def UDPsend(self, Client, address, t1, threadCount, msgFromServer="Test"):
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
            self.clients.add(address)
            if len(self.clients) > self.threadCount:
                print("Connected to:{}".format(address))
                newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                newSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.localPort += 1 # new port
                newSock.bind(("0.0.0.0",self.localPort))
                self.sock.sendto(str.encode(str(self.localPort)), address)
                primary = threading.Thread(target=self.UDPthread, args=[newSock, address, self.threadCount])
                primary.start()
                self.threadCount += 1


@socketio.on("connect")
def connect():
    print("Client connected", request.sid)


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    udpxServer = ServerConsole()
    udpServer = threading.Thread(target=udpxServer.UDPserver)
    udpServer.daemon = True
    udpServer.start()

    socketio.run(app,debug=False, host='0.0.0.0')
