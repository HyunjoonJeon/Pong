import socket



msgFromClient       = "Hello UDP Server - Zion"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("52.170.185.55", 2399)

bufferSize          = 1024

 
print("Creating UDP socket at Client Side")

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 
print("Send to server using Created UDP socket")

# Send to server using created UDP socket

print("Send to Socket")
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

 
print("Message from server working :")
msgFromServer = UDPClientSocket.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)
