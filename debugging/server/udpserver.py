import socket
def checkUDP(UDPServerSocket, bufferSize, msgFromServer="D"): 
    while(True): 
        bytesToSend = str.encode(msgFromServer)
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)

        print(clientMsg)
        print(clientIP)

        # Sending a reply to client

        UDPServerSocket.sendto(bytesToSend, address)


def main():
    localPort = 2399
    bufferSize = 1024


    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPServerSocket.bind(("0.0.0.0", localPort))

    print("UDP server up and listening")

    checkUDP(UDPServerSocket,bufferSize)

if __name__ == "__main__":
    main()
