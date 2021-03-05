import socket

localPort = 2399
bufferSize = 1024

msgFromServer       = "Hello UDP Client:D"
bytesToSend         = str.encode(msgFromServer)

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPServerSocket.bind(("0.0.0.0", localPort))

print("UDP server up and listening")

while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)



    # Sending a reply to client

    UDPServerSocket.sendto(bytesToSend, address)
