import socket

n = 1

#while n>0:

msgFromClient       = "Hackerman 2k21"
bytesToSend         = str.encode(msgFromClient)


serverAddressPort   = ("52.170.185.55", 2399)

bufferSize          = 1024

 
# print ("Test Matt")

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP sockethi
while n>0:
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

 

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)