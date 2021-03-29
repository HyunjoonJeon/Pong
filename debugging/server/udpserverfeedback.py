import time
import socket
def checkUDP(UDPServerSocket, bufferSize, msgFromServer,measurements):
    for x in range (measurements):
        bytesToSend = str.encode(msgFromServer)
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)

        print(clientMsg)
        print(clientIP)

        if(x == 0):
            print("Sending: ",msgFromServer)
            UDPServerSocket.sendto(bytesToSend, address)




def main():
    localPort = 2399
    bufferSize = 1024

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind(("0.0.0.0", localPort))

    print("UDP server up and listening")

    checkUDP(UDPServerSocket, bufferSize, "2399", 1)

    checkUDP(UDPServerSocket, bufferSize, "x", 30)

    checkUDP(UDPServerSocket, bufferSize, "y", 30)

    checkUDP(UDPServerSocket, bufferSize, "s", 1)

if __name__ == "__main__":
    main()

