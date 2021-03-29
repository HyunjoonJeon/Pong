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
        self.currentThreads = [ () , () ]
        #list with top two addresses
        self.currentVals = ["0", "0"] #list with most recent values
        self.zeroes = False
        self.playerdisconnect = [False, False] #list with disconnecting players
        self.scores = [0, 0]
        print("UDP Server up and listening")
        tcal = threading.Thread(target=self.UDPcalculate, args=[])
        tcal.start()

    def UDPthread(self, Client, address, threadCount):
        print("Thread " + str(threadCount) + " started")
        t1 = threading.Thread(target=self.UDPreceive, args=[Client, address, threadCount])
        t1.start()
        self.zeroes = False
        if threadCount == 1:
            self.UDPsend(Client, address, 'h')
            self.UDPsend(Client, address, 'c')
            self.UDPsend(Client, address, 'x')
        elif threadCount == 2:
            self.UDPsend(Client, address, 'a')
            self.UDPsend(Client, address, 'c')
            self.UDPsend(Client, address, 'x')

    def UDPdisconnect(self, Client, address , threadCount):
        print("UDP Disconenct Called")
        self.playerCount -= 1
        self.currentVals[threadCount-1] = "0"
        self.currentThreads[threadCount-1] = ()
        if self.connectQueue.empty():
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
            if "{}".format(data) == "b'd'" or self.playerdisconnect[threadCount - 1] == True:
                print(f"killing thread {threadCount} UDPreceive")
                self.playerdisconnect[threadCount - 1] = False
                self.UDPdisconnect(Client, address, threadCount)
                return
            else:
                self.currentVals[threadCount-1] = "{}".format(data)

    def UDPcalculate(self):
        p1currentposy = 215
        p2currentposy = 215
        score = [0,0]
        ballposx = 691
        ballposy = 491
        over = False
        roundstart = True
        ballDirectionX = 0
        ballDirectionY = 0
        while True:
            if (self.zeroes == True):
                self.currentVals[0] = "0"
                self.currentVals[1] = "0"
            time.sleep(1/10)
            if (self.currentVals[0] != "0") and (self.currentVals[1] != "0"): #list not empty
                p1currentspd = float(self.currentVals[0][2: -1])/6
                p2currentspd =float(self.currentVals[1][2: -1])/6
                p1currentposy, p2currentposy, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart = self.UDPupdate(p1currentposy, p2currentposy, p1currentspd, p2currentspd, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart)
                print(ballposx, ballposy, ballDirectionX, ballDirectionY)
                socketio.emit('my_response',{'p1currentposy': p1currentposy, 'p2currentposy': p2currentposy, 'ballposx': ballposx, 'ballposy': ballposy, 'score': [score[0], score[1]], 'over': over}, broadcast = True)
                if roundstart:
                    time.sleep(2)
                if over:
                    if score[1] == 2:
                        p1currentposy, p2currentposy, ballposx, ballposy, score = self.UDPreset(0, 0)
                        self.playerdisconnect[0] = True
                        self.currentVals[0] != "0"
                        self.zeroes = True
                        roundstart = True
                        over = False
                    elif score[0] == 2:
                        p1currentposy, p2currentposy, ballposx, ballposy, score = self.UDPreset(0, 0)
                        self.currentVals[1] != "0"
                        self.playerdisconnect[1] = True
                        self.zeroes = True
                        roundstart = True
                        over = False

    def UDPupdate(self, p1currentposy, p2currentposy, p1currentspd, p2currentspd, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart):
        canvasWidth = 1400
        canvasHeight = 1000
        ballWidth = 18
        ballHeight = 18
        ballSpeed = 12 
        paddleWidth = 18
        paddleHeight = 70
        p1currentposx = 150
        p2currentposx = canvasWidth - 150
        if not over:
            #If the ball collides with the bound limits - correct the x and y coords.
            if ballposx <= 0:
                print(roundstart)
                score[1] += 1
                client1 = self.currentThreads[0]
                client2 = self.currentThreads[1]
                self.UDPsend(client1[0], client1[1], 'y')
                self.UDPsend(client2[0], client2[1], 'x')
                (p1currentposy, p2currentposy, ballposx, ballposy, score) = self.UDPreset(score[0], score[1])
                roundstart = True
                return p1currentposy, p2currentposy, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart
                # reset
            elif ballposx >= canvasWidth - ballWidth:
                print(roundstart)
                score[0] += 1
                client1 = self.currentThreads[0]
                client2 = self.currentThreads[1]
                self.UDPsend(client1[0], client1[1], 'x')
                self.UDPsend(client2[0], client2[1], 'y')
                (p1currentposy, p2currentposy, ballposx, ballposy, score) = self.UDPreset(score[0], score[1])
                roundstart = True
                return p1currentposy, p2currentposy, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart
                # reset
                # reset
            if ballposy <= 0:
                ballDirectionY = 2
            elif ballposy >= canvasHeight - ballHeight:
                ballDirectionY = 1

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
                if round(random.uniform(0, 1)):
                    ballDirectionX = 3
                else:
                    ballDirectionX = 4
                if round(random.uniform(0, 1)):
                    ballDirectionY = 1
                else:
                    ballDirectionY = 2
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
            if ballDirectionY == 1:
                print(ballSpeed)
                ballposy -= ballSpeed / 1.5
            elif ballDirectionY == 2:
                print(ballSpeed)
                ballposy += ballSpeed / 1.5
            if ballDirectionX == 3:
                ballposx -= ballSpeed
            elif ballDirectionX == 4:
                ballposx += ballSpeed

			#Handle Player1-Ball collisions
            if ballposx - ballWidth <= p1currentposx and ballposx >= p1currentposx - paddleWidth:
                if ballposy <= p1currentposy + paddleHeight and ballposy + ballHeight >= p1currentposy:
                    ballposx = p1currentposx + ballWidth
                    ballDirectionX = 4
					#beep1.play()

            #Handle Player2-Ball collision
            if ballposx - ballWidth <= p2currentposx and ballposx >= p2currentposx - paddleWidth:
                if ballposy <= p2currentposy + paddleHeight and ballposy + ballHeight >= p2currentposy:
                    ballposx = p2currentposx - ballWidth
                    ballDirectionX = 3
					#beep1.play()

        if (score[0] ==2) or (score[1] == 2):
            over = True

        return p1currentposy, p2currentposy, ballposx, ballposy, ballDirectionX, ballDirectionY, score, over, roundstart
    
    def UDPreset(self, p1score, p2score):
        p1currentposy = 215
        print("I am resetting")
        p2currentposy = 215
        score = [p1score,p2score]
        client1 = self.currentThreads[0]
        client2 = self.currentThreads[1]
        self.UDPsend(client1[0], client1[1], str(p1score))
        self.UDPsend(client1[0], client1[1], str(p2score+6))
        self.UDPsend(client1[0], client1[1], 'x')
        self.UDPsend(client2[0], client2[1], str(p2score))
        self.UDPsend(client2[0], client2[1], str(p1score+6))
        self.UDPsend(client2[0], client2[1], 'x')
        ballposx = 691
        ballposy = 491
        return (p1currentposy, p2currentposy, ballposx, ballposy, score)
        
                            
    def UDPsend(self, Client, address, msgFromServer):
        bytesToSend = str.encode(msgFromServer)
        Client.sendto(bytesToSend, address)


    def UDPserver(self):
        while True:
            message, address = self.sock.recvfrom(self.bufferSize)
            print("Connected to:{}".format(address))
            print(self.playerCount)
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
