from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from enum import Enum
import socket
import threading
import time
import queue
import json
import random
import math

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
            primary = threading.Thread(target=self.UDPthread, args=[newSock, address, threadCount])
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
                self.UDPdisconnect(Client, address , threadCount)
                return
            else:
                self.currentVals[threadCount-1] = "{}".format(data)

    def UDPcalculate(self):
        p1currentposy = 215
        p2currentposy = 215
        score = (0,0)
        ballposx = 691
        ballposy = 491
        over = False
        roundstart = True
        ballDirectionX = 0
        ballDirectionY = 0
        while True:
            if self.currentVals[0] and self.currentVals[1] != "0": #list not empty
                p1currentspd = int(self.currentVals[0])
                p2currentspd =int(self.currentVals[1])
                p1currentposy, p2currentposy, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart = self.UDPupdate(p1currentposy, p2currentposy, p1currentspd, p2currentspd, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart)
                data_set = {"p1currentposy": p1currentposy, "p2currentposy": p2currentposy, "ballposx": ballposx, "ballposy": ballposy, "score": [score[0], score[1]], "over": over}
                data = json.dumps(data_set)
                socketio.emit('my_response',data, broadcast = True)
                if roundstart:
                    time.sleep(10)

    def UDPupdate(self, p1currentposy, p2currentposy, p1currentspd, p2currentspd, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart):
        class Direction(Enum):
            IDLE = 0
            UP = 1
            DOWN = 2
            LEFT = 3
            RIGHT = 4
        canvasWidth = 1400
        canvasHeight = 1000
        ballWidth = 18
        ballHeight = 18
        ballSpeed = 9
        paddleWidth = 18
        paddleHeight = 70
        p1currentposx = 150
        p2currentposx = canvasWidth - 150
        if not over:
            #If the ball collides with the bound limits - correct the x and y coords.
            if ballposx <= 0:
                score[0] += 1
                (p1currentspd, p2currentspd, ballposx, ballposy, score) = self.UDPreset(score[0], score[1])
                roundstart = True
                return p1currentspd, p2currentspd, ballposx, ballposy, score, roundstart
                # reset
            elif ballposx >= canvasWidth - ballWidth:
                score[1] += 1
                (p1currentspd, p2currentspd, ballposx, ballposy, score) = self.UDPreset(score[0], score[1])
                roundstart = True
                return p1currentspd, p2currentspd, ballposx, ballposy, score, roundstart
                # reset
            if ballposy <= 0:
                ballDirectionY = Direction.DOWN
            elif ballposy >= canvasHeight - ballHeight:
                ballDirectionY = Direction.UP

			#Move players if they player.move value was updated by a keyboard event
            if p1currentspd!=0:
                p1currentposy -= p1currentspd
            elif p1currentspd==0:
                p1currentposy += p1currentspd
            if p2currentspd!=0:
                p2currentposy -= p2currentspd
            elif p2currentspd==0:
                p2currentposy += p2currentspd

			#On new serve (start of each turn) move the ball to the correct side
			#and randomize the direction to add some challenge.
            if roundstart:
                ballDirectionX = (score[0]+score[1])%2 if Direction.LEFT else Direction.RIGHT
                ballDirectionY = round(random.uniform(0, 1)) if Direction.UP else Direction.DOWN
                ballposy = math.floor(random.uniform(0, 1) * canvasHeight - 200) + 200
                roundstart = False

			#If the players collide with the bound limits, update the x and y coords.
            if p1currentposy <= 0: 
                p1currentposy = 0
            elif p1currentposy >= (canvasHeight - paddleHeight):
                p1currentposy = (canvasHeight - paddleHeight)
            if p2currentposy <= 0:
                p2currentposy = 0
            elif p2currentposy >= (canvasHeight - paddleHeight):
                p2currentposy = (canvasHeight - paddleHeight)
			
            #Move ball in intended direction based on moveY and moveX values
            if ballDirectionY == Direction.UP:
                ballposy -= ballSpeed / 1.5
            elif ballDirectionY == Direction.DOWN:
                ballposy += ballSpeed / 1.5
            if ballDirectionX == Direction.LEFT:
                ballposx -= ballSpeed
            elif ballDirectionX == Direction.RIGHT:
                ballposx += ballSpeed

			#Handle Player1-Ball collisions
            if ballposx - ballWidth <= p1currentposx and ballposx >= p1currentposx - paddleWidth:
                if ballposy <= p1currentposy + paddleHeight and ballposy + ballHeight >= p1currentposy:
                    ballposx = p1currentposx + ballWidth
                    ballDirectionX = Direction.RIGHT
					#beep1.play()

            #Handle Player2-Ball collision
            if ballposx - ballWidth <= p2currentposx and ballposx >= p2currentposx - paddleWidth:
                if ballposy <= p2currentposy + paddleHeight and ballposy + ballHeight >= p2currentposy:
                    ballposx = p2currentposx - ballWidth
                    ballDirectionX = Direction.LEFT
					#beep1.play()

        if score[0] or score[1] == 5:
            over = True

        return p1currentposy, p2currentposy, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart
    
    def UDPreset(self, p1score, p2score):
        p1currentposy = 215
        p2currentposy = 215
        score = (p1score,p2score)
        ballposx = 691
        ballposy = 491
        return (p1currentposy, p2currentposy, ballposx, ballposy, score)
        
                            
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
                if self.currentVals[0] == "0":
                    threadCount = 1
                elif self.currentVals[1] == "0":
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
