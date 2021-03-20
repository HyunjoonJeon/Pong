import socket
import turtle
import time
import sys

#Creating screen 
sc = turtle.Screen() 
sc.title("Pong game") 
sc.bgcolor("black") 
sc.setup(width=1000, height=600) 

#Creating paddle 
pad = turtle.Turtle() 
pad.speed(0) 
pad.shape("square") 
pad.color("white") 
pad.shapesize(stretch_wid=2, stretch_len=6) 
pad.penup() 
pad.goto(0, 0) 

def paddlemove(x):
    x0 = pad.xcor() 
    x0 += x
    pad.setx(x0)

def checkUDP(UDPServerSocket, bufferSize, msgFromServer="Hello UDP Client:D"): 
    while(True): 
        bytesToSend = str.encode(msgFromServer)
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)

        print(clientMsg)
        print(clientIP)
        gameloop(message)

        # Sending a reply to client

        UDPServerSocket.sendto(bytesToSend, address)

def gameloop(message):
    if(message != 0):
        try:
            reading = message.decode("utf-8") 
            value = reading[-2]+reading[-1]
            x = int(value, 16) - 127
            paddlemove(x)
        except Exception:
            pass


def main():
    localPort = 1800
    bufferSize = 1024


    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind(("0.0.0.0", localPort))

    print("UDP server up and listening")

    checkUDP(UDPServerSocket,bufferSize)

if __name__ == "__main__":
    main()
